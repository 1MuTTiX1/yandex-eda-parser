"""Сценарий работы с сайтом Яндекс Еды через Selenium."""
from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime, timedelta

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from .parsing import count_place_cards, extract_restaurant_urls

log = logging.getLogger(__name__)

DEFAULT_CITY_URL = "https://eats.yandex.com/ru-am/Yerevan?shippingType=delivery"

Locator = tuple[str, str]

# Селекторы собраны в одном месте: когда вёрстка поменяется, править нужно только их.
# Каждый шаг — это список вариантов: сначала устойчивые CSS-селекторы,
# затем исходные абсолютные XPath как запасной вариант.
SEL_ADDRESS_BUTTON: list[Locator] = [
    (By.CSS_SELECTOR, "[class*='DesktopAddressButton_address']"),
]
SEL_ADDRESS_INPUT: list[Locator] = [
    (By.CSS_SELECTOR, "div[role='dialog'] input"),
    (By.XPATH, "/html/body/div[3]/div/div/div/div/div[1]/div[2]/div/div/div[1]/input"),
]
SEL_FIRST_SUGGEST: list[Locator] = [
    (By.ID, "react-autowhatever-1--item-0"),
]
SEL_CONFIRM_BUTTON: list[Locator] = [
    (By.XPATH, "/html/body/div[3]/div/div/div/div/div[1]/div[2]/button"),
]
SEL_TIME_SELECTOR: list[Locator] = [
    (By.CSS_SELECTOR, "[class*='DeliveryTime'], [class*='ShippingTime']"),
    (By.XPATH, "/html/body/div[1]/div/div/div[1]/main/div/div/main/div[3]/div/div/div"),
]
SEL_TOMORROW_TAB: list[Locator] = [
    (By.XPATH, "/html/body/div[3]/div/div/div/div/div/div[1]/button[2]"),
]


@dataclass(frozen=True)
class ScraperConfig:
    city_url: str = DEFAULT_CITY_URL
    headless: bool = True
    timeout: float = 15.0
    scroll_pause: float = 2.0
    max_scrolls: int = 200
    delivery_hour: int = 15


def build_driver(headless: bool = True) -> WebDriver:
    options = webdriver.FirefoxOptions()
    options.add_argument("--width=1920")
    options.add_argument("--height=1080")
    if headless:
        options.add_argument("--headless")
    return webdriver.Firefox(options=options)


def target_delivery_time(hour: int, now: datetime | None = None) -> datetime:
    """Завтра в `hour`:00 — время, на которое нужно выбрать доставку."""
    now = now or datetime.now()
    tomorrow = now + timedelta(days=1)
    return tomorrow.replace(hour=hour, minute=0, second=0, microsecond=0)


class YandexEdaScraper:
    def __init__(self, driver: WebDriver, config: ScraperConfig | None = None):
        self.driver = driver
        self.config = config or ScraperConfig()
        self.wait = WebDriverWait(driver, self.config.timeout)

    # ── публичный API ────────────────────────────────────────────────────
    def collect(self, address: str) -> list[str]:
        """Собирает URL всех ресторанов, доступных по адресу."""
        log.info("Адрес: %s", address)
        self.driver.get(self.config.city_url)
        self._click(SEL_ADDRESS_BUTTON)
        self._type_address(address)
        self._click(SEL_FIRST_SUGGEST)
        self._click(SEL_CONFIRM_BUTTON)
        self._set_delivery_time()
        urls = self._scroll_and_collect()
        log.info("Найдено ресторанов: %d", len(urls))
        return urls

    # ── вспомогательные шаги ─────────────────────────────────────────────
    def _first_working(self, locators: list[Locator], condition):
        """Пробует локаторы по очереди и возвращает первый сработавший элемент."""
        last_error: TimeoutException | None = None
        for locator in locators:
            try:
                return WebDriverWait(self.driver, self.config.timeout).until(condition(locator))
            except TimeoutException as exc:
                log.debug("Локатор не сработал: %s", locator)
                last_error = exc
        raise TimeoutException(f"Ни один локатор не сработал: {locators}") from last_error

    def _click(self, locators: list[Locator]) -> None:
        self._first_working(locators, EC.element_to_be_clickable).click()

    def _type_address(self, address: str) -> None:
        field = self._first_working(SEL_ADDRESS_INPUT, EC.visibility_of_element_located)
        field.clear()
        field.send_keys(address)
        # Пробел запускает подсказки так же, как ручной ввод.
        field.send_keys(Keys.SPACE)

    def _set_delivery_time(self) -> None:
        """Выбирает «завтра, 15:00».

        Слот ищем по тексту (например «15:00»), а не по индексу button[31],
        который ломается при любом изменении сетки времени.
        """
        label = target_delivery_time(self.config.delivery_hour).strftime("%H:%M")
        self._click(SEL_TIME_SELECTOR)
        self._click(SEL_TOMORROW_TAB)
        slot = self.wait.until(
            EC.presence_of_element_located(
                (By.XPATH, f"//button[contains(normalize-space(.), '{label}')]")
            )
        )
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", slot)
        self.wait.until(EC.element_to_be_clickable(slot)).click()

    def _scroll_and_collect(self) -> list[str]:
        """Скроллит выдачу, пока число карточек растёт, и копит URL на каждом проходе.

        URL накапливаются во время скролла, а не только в конце: если список
        виртуализирован, ранние карточки могут пропасть из DOM.
        """
        body = self.driver.find_element(By.TAG_NAME, "body")
        collected: dict[str, None] = {}  # dict как упорядоченное множество
        previous = -1

        for _ in range(self.config.max_scrolls):
            body.send_keys(Keys.CONTROL + Keys.END)
            try:
                # Ждём роста числа карточек вместо фиксированных sleep().
                WebDriverWait(self.driver, self.config.scroll_pause + 1).until(
                    lambda d, prev=previous: count_place_cards(d.page_source) > prev
                )
            except TimeoutException:
                break
            html = self.driver.page_source
            previous = count_place_cards(html)
            collected.update(dict.fromkeys(extract_restaurant_urls(html)))
            log.debug("Карточек: %d, уникальных URL: %d", previous, len(collected))
        else:
            log.warning("Достигнут лимит скроллов (%d)", self.config.max_scrolls)

        return list(collected)
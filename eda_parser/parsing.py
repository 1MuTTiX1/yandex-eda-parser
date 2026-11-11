"""Чистые функции разбора HTML и работы с именами файлов.

Модуль не зависит от Selenium, поэтому его легко тестировать без браузера.
"""
from __future__ import annotations

import re
from collections.abc import Iterable

from bs4 import BeautifulSoup

BASE_URL = "https://eats.yandex.com"

# Класс карточки ресторана в выдаче. Яндекс периодически его меняет,
# поэтому он вынесен в константу и ищется по префиксу, а не по точной строке.
PLACE_ITEM_PREFIX = "PlaceListBduItem_placesListItem"

_FORBIDDEN_FILENAME_CHARS = re.compile(r'[\\/:*?"<>|,]+')


def extract_restaurant_urls(html: str, base_url: str = BASE_URL) -> list[str]:
    """Возвращает ссылки на рестораны из HTML страницы выдачи.

    Порядок сохраняется, дубликаты внутри одной страницы убираются.
    """
    soup = BeautifulSoup(html, "lxml")
    items = soup.find_all(
        "div",
        class_=lambda c: bool(c) and c.startswith(PLACE_ITEM_PREFIX),
    )

    urls: list[str] = []
    seen: set[str] = set()
    for item in items:
        link = item.find("a", href=True)
        if link is None:
            continue
        url = _absolute(link["href"], base_url)
        if url not in seen:
            seen.add(url)
            urls.append(url)
    return urls


def count_place_cards(html: str) -> int:
    """Количество карточек ресторанов на странице (нужно для детекции конца скролла)."""
    soup = BeautifulSoup(html, "lxml")
    return len(
        soup.find_all(
            "div",
            class_=lambda c: bool(c) and c.startswith(PLACE_ITEM_PREFIX),
        )
    )


def _absolute(href: str, base_url: str) -> str:
    if href.startswith(("http://", "https://")):
        return href
    return f"{base_url.rstrip('/')}/{href.lstrip('/')}"


def unique_preserve_order(urls: Iterable[str]) -> list[str]:
    """Убирает дубликаты, сохраняя порядок (в отличие от list(set(...)))."""
    return list(dict.fromkeys(urls))


def safe_filename(address: str, max_length: int = 120) -> str:
    """Превращает адрес в безопасное имя файла для Windows и Linux."""
    name = _FORBIDDEN_FILENAME_CHARS.sub(" ", address)
    name = re.sub(r"\s+", "_", name.strip())
    name = name.strip("._") or "address"
    return name[:max_length]

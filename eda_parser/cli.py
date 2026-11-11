"""Командный интерфейс: python -m eda_parser --address "..." """
from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

from .parsing import safe_filename

log = logging.getLogger("eda_parser")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        prog="eda_parser",
        description="Собирает URL ресторанов Яндекс Еды по адресу (доставка на завтра, 15:00).",
    )
    src = p.add_mutually_exclusive_group(required=True)
    src.add_argument("-a", "--address", action="append", help="адрес (можно указать несколько раз)")
    src.add_argument("-f", "--addresses-file", type=Path, help="файл со списком адресов, по одному на строку")
    p.add_argument("-o", "--output-dir", type=Path, default=Path("output"), help="куда сохранять результаты")
    p.add_argument("--city-url", help="URL города на eats.yandex.com")
    p.add_argument("--hour", type=int, default=15, help="час доставки на завтра (по умолчанию 15)")
    p.add_argument("--timeout", type=float, default=15.0, help="таймаут ожидания элементов, сек")
    p.add_argument("--no-headless", action="store_true", help="показывать окно браузера")
    p.add_argument("-v", "--verbose", action="store_true", help="подробные логи")
    return p.parse_args(argv)


def load_addresses(args: argparse.Namespace) -> list[str]:
    if args.addresses_file:
        lines = args.addresses_file.read_text(encoding="utf-8").splitlines()
        return [ln.strip() for ln in lines if ln.strip() and not ln.startswith("#")]
    return [a.strip() for a in args.address if a.strip()]


def save_urls(urls: list[str], address: str, output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / f"{safe_filename(address)}.txt"
    path.write_text("\n".join(urls) + ("\n" if urls else ""), encoding="utf-8")
    return path


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
    )

    addresses = load_addresses(args)
    if not addresses:
        log.error("Список адресов пуст")
        return 2

    # Selenium импортируется здесь, чтобы --help и тесты работали без браузера.
    from .scraper import DEFAULT_CITY_URL, ScraperConfig, YandexEdaScraper, build_driver

    config = ScraperConfig(
        city_url=args.city_url or DEFAULT_CITY_URL,
        headless=not args.no_headless,
        timeout=args.timeout,
        delivery_hour=args.hour,
    )

    failures = 0
    driver = build_driver(headless=config.headless)
    try:
        scraper = YandexEdaScraper(driver, config)
        for address in addresses:
            try:
                urls = scraper.collect(address)
            except Exception:
                # Ошибка по одному адресу не должна обрывать весь список.
                log.exception("Не удалось обработать адрес: %s", address)
                failures += 1
                continue
            path = save_urls(urls, address, args.output_dir)
            log.info("Сохранено %d URL → %s", len(urls), path)
    finally:
        driver.quit()

    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())

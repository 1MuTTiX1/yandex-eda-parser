# yandex-eda-parser

Консольный парсер, который по адресу доставки собирает ссылки на все рестораны
[Яндекс Еды](https://eats.yandex.com) (на примере Еревана) с выбранным временем
доставки «завтра, 15:00». Принимает один адрес или список адресов и сохраняет
результат в текстовые файлы.

*English: a CLI scraper that collects URLs of all restaurants on Yandex Eats for a
given delivery address and the "tomorrow, 15:00" delivery slot.*

## Возможности

- Один или несколько адресов (`-a` или файл `-f`)
- Явные ожидания элементов (`WebDriverWait`) вместо `time.sleep`
- Автоскролл выдачи до конца с накоплением и дедупликацией URL
- Ошибка по одному адресу не останавливает обработку остальных
- Логирование и код возврата для использования в скриптах/cron
- Парсинг HTML вынесен в чистые функции и покрыт тестами без браузера

## Установка

Нужны Python 3.10+, Firefox и [geckodriver](https://github.com/mozilla/geckodriver/releases)
(Selenium 4 обычно подтягивает драйвер сам).

```bash
git clone https://github.com/1MuTTiX1/yandex-eda-parser.git
cd yandex-eda-parser
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Использование

```bash
# один адрес
python -m eda_parser --address "Ереван, проспект Маршала Баграмяна 1"

# несколько адресов
python -m eda_parser -a "Адрес 1" -a "Адрес 2" -o results

# список из файла (один адрес на строку, строки с # игнорируются)
python -m eda_parser --addresses-file addresses.txt --output-dir results

# с видимым окном браузера и подробными логами
python -m eda_parser -a "Адрес" --no-headless -v
```

| Параметр | Описание | По умолчанию |
|---|---|---|
| `-a, --address` | Адрес (можно повторять) | — |
| `-f, --addresses-file` | Файл со списком адресов | — |
| `-o, --output-dir` | Папка для результатов | `output` |
| `--city-url` | URL города на eats.yandex.com | Ереван |
| `--hour` | Час доставки на завтра | `15` |
| `--timeout` | Таймаут ожидания элементов, сек | `15` |
| `--no-headless` | Показывать окно браузера | выключено |

Результат: файл `output/<адрес>.txt`, по одной ссылке на строку.

## Структура проекта

```
eda_parser/
  parsing.py   # разбор HTML, имена файлов (без Selenium)
  scraper.py   # сценарий в браузере: адрес → время → скролл
  cli.py       # аргументы командной строки, сохранение
tests/         # pytest
main.py        # совместимая точка входа
```

## Разработка

```bash
pip install -r requirements-dev.txt
ruff check .
pytest
```

## Ограничения

Парсер зависит от вёрстки сайта. Селекторы собраны в начале `eda_parser/scraper.py`
и `eda_parser/parsing.py`; при изменении интерфейса Яндекса достаточно обновить их.
Используйте парсер с учётом пользовательского соглашения сервиса и не создавайте
чрезмерную нагрузку на сайт.

## Лицензия

MIT

from eda_parser.parsing import (
    count_place_cards,
    extract_restaurant_urls,
    safe_filename,
    unique_preserve_order,
)

HTML = """
<html><body>
  <div class="PlaceListBduItem_placesListItem PlaceListBduItem_lg"><a href="/ru-am/r/cafe_one">One</a></div>
  <div class="PlaceListBduItem_placesListItem PlaceListBduItem_lg"><a href="/ru-am/r/cafe_two">Two</a></div>
  <div class="PlaceListBduItem_placesListItem PlaceListBduItem_lg"><a href="/ru-am/r/cafe_one">Dup</a></div>
  <div class="PlaceListBduItem_placesListItem PlaceListBduItem_lg"><span>без ссылки</span></div>
  <div class="Other_item"><a href="/ru-am/r/not_a_place">x</a></div>
</body></html>
"""


def test_extract_urls_absolute_deduplicated_ordered():
    assert extract_restaurant_urls(HTML) == [
        "https://eats.yandex.com/ru-am/r/cafe_one",
        "https://eats.yandex.com/ru-am/r/cafe_two",
    ]


def test_extract_urls_keeps_absolute_links():
    html = '<div class="PlaceListBduItem_placesListItem"><a href="https://x.test/a">a</a></div>'
    assert extract_restaurant_urls(html) == ["https://x.test/a"]


def test_extract_urls_empty_page():
    assert extract_restaurant_urls("<html></html>") == []


def test_count_place_cards_counts_cards_without_links():
    assert count_place_cards(HTML) == 4


def test_unique_preserve_order():
    assert unique_preserve_order(["b", "a", "b", "c", "a"]) == ["b", "a", "c"]


def test_safe_filename_strips_forbidden_chars():
    assert safe_filename("Ереван, ул. Абовяна 10/2") == "Ереван_ул._Абовяна_10_2"


def test_safe_filename_never_empty():
    assert safe_filename("///") == "address"


def test_safe_filename_truncates():
    assert len(safe_filename("a" * 500)) == 120

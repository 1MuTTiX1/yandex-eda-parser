from pathlib import Path

import pytest

from eda_parser.cli import load_addresses, parse_args, save_urls


def test_requires_address_source():
    with pytest.raises(SystemExit):
        parse_args([])


def test_multiple_addresses():
    args = parse_args(["-a", "A", "-a", "B"])
    assert load_addresses(args) == ["A", "B"]


def test_addresses_file_skips_blank_and_comments(tmp_path: Path):
    f = tmp_path / "addr.txt"
    f.write_text("Адрес 1\n\n# комментарий\n  Адрес 2  \n", encoding="utf-8")
    args = parse_args(["-f", str(f)])
    assert load_addresses(args) == ["Адрес 1", "Адрес 2"]


def test_save_urls_writes_one_per_line(tmp_path: Path):
    path = save_urls(["u1", "u2"], "Ереван, Абовяна 1", tmp_path / "out")
    assert path.read_text(encoding="utf-8") == "u1\nu2\n"
    assert path.parent == tmp_path / "out"


def test_save_urls_empty_list_creates_empty_file(tmp_path: Path):
    path = save_urls([], "X", tmp_path)
    assert path.read_text(encoding="utf-8") == ""

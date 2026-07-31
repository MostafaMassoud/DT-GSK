from __future__ import annotations

import pytest

from gsk_family.runners.verification import (
    load_reference_table,
    normalize_function_label,
    parse_optional_float,
)


def test_normalize_function_label_accepts_common_forms() -> None:
    assert normalize_function_label("1") == 1
    assert normalize_function_label("F1") == 1
    assert normalize_function_label("f001") == 1
    assert normalize_function_label("Function 12") == 12

    with pytest.raises(ValueError, match="Cannot parse"):
        normalize_function_label("abc")


def test_parse_optional_float_handles_reference_missing_tokens() -> None:
    assert parse_optional_float("1.25E+03") == 1250.0
    assert parse_optional_float("N/A") is None
    assert parse_optional_float("-") is None
    assert parse_optional_float("nan") is None


def test_load_reference_table_supports_d_zero_padding_and_missing_cells(tmp_path) -> None:
    ref_dir = tmp_path / "cec2020" / "agsk"
    ref_dir.mkdir(parents=True)
    table = ref_dir / "agsk_cec2020_D05.csv"
    table.write_text(
        "Function,Best,Median,Mean,Worst,SD\n"
        "F1,0,0,0,0,0\n"
        "f2,N/A,N/A,N/A,N/A,N/A\n",
        encoding="utf-8",
    )

    loaded = load_reference_table(tmp_path, "agsk", "cec2020", 5)

    assert loaded is not None
    assert loaded.dimension == 5
    assert loaded.cells[1].stats["Mean"] == 0.0
    assert loaded.cells[2].stats["Mean"] is None


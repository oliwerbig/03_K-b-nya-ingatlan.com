# data_ingestion.py – Unified data loading and validation

"""Utility module for loading real‑estate data from heterogeneous sources.

The project now has a canonical schema defined in ``data/schema.yaml``.  Any
incoming dataset (CSV, Excel, JSON, Parquet, scraped HTML → DataFrame, etc.) can
be normalized to that schema by providing an optional ``column_mapping``
dictionary.

Typical usage in notebooks:

```python
from data_ingestion import load_and_validate

# Load a local CSV from another district
df = load_and_validate(
    path='data/other_district.csv',
    source_type='csv',
    column_mapping={
        'external_id': 'listing_id',
        'price': 'price_huf',
        'size_sqm': 'alapterulet_nm',
        'rooms': 'szobaszam_osszes',
        'district': 'varosresz',
        'condition': 'allapot_kod',
        'precise_geo': 'minta_garantalt_pontos',
    }
)
```

If ``column_mapping`` is omitted the function assumes the source already uses the
canonical column names.  Validation is performed against the **required** and
**optional** sections of ``schema.yaml``; missing required columns raise a clear
exception, while missing optional columns are filled with ``NaN``/default values.
"""

import os
import pandas as pd
import yaml
from typing import Dict, Optional

SCHEMA_PATH = os.path.join(os.path.dirname(__file__), "data", "schema.yaml")


def _load_schema(schema_path: str = SCHEMA_PATH) -> dict:
    """Load the YAML schema file.

    Returns a dictionary with keys ``required``, ``optional`` and ``types``.
    """
    if not os.path.exists(schema_path):
        raise FileNotFoundError(f"Schema file not found: {schema_path}")
    with open(schema_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


_SCHEMA = _load_schema()


def _apply_mapping(df: pd.DataFrame, mapping: Dict[str, str]) -> pd.DataFrame:
    """Rename columns according to ``mapping``.

    ``mapping`` maps *source* column names → *canonical* column names.
    Columns not present in the mapping are left unchanged.
    """
    return df.rename(columns=mapping)


def _validate_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Validate ``df`` against the canonical schema.

    - Ensures all **required** columns exist.
    - Adds missing **optional** columns with ``NaN``.
    - Casts columns to the declared dtypes (``types`` section).
    - Returns the validated DataFrame.
    """
    required = set(_SCHEMA.get("required", {}).keys())
    optional = set(_SCHEMA.get("optional", {}).keys())
    missing_req = required - set(df.columns)
    if missing_req:
        raise ValueError(
            f"Missing required columns: {', '.join(sorted(missing_req))}. "
            "Check your ``column_mapping`` or source file headers."
        )

    # Add missing optional columns
    for col in optional - set(df.columns):
        df[col] = pd.NA

    # Cast to declared dtypes
    all_fields = {**_SCHEMA.get("required", {}), **_SCHEMA.get("optional", {})}
    for col, dtype in all_fields.items():
        if col in df.columns:
            try:
                if dtype == "float64":
                    df[col] = pd.to_numeric(df[col], errors="coerce").astype("float64")
                elif dtype == "int64":
                    df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype("int64")
                elif dtype == "object":
                    df[col] = df[col].astype("object")
            except Exception:
                pass

    # Re‑order columns to match the schema (nice for downstream code)
    ordered_cols = [c for c in _SCHEMA.get("required", {}) if c in df.columns] + [
        c for c in _SCHEMA.get("optional", {}) if c in df.columns
    ]
    remaining = [c for c in df.columns if c not in ordered_cols]
    df = df[ordered_cols + remaining]
    return df


def _load_file(path: str, source_type: str) -> pd.DataFrame:
    """Read a file according to ``source_type``.

    Supported ``source_type`` values: ``csv``, ``excel``, ``parquet``, ``json``.
    For ``excel`` the ``openpyxl`` engine is used (ensure the dependency is
    installed).  ``json`` is expected to be line‑delimited records or a JSON
    array that can be passed to ``pd.read_json``.
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"Data file not found: {path}")

    source_type = source_type.lower()
    if source_type == "csv":
        return pd.read_csv(path, encoding="utf-8-sig")
    elif source_type == "excel":
        return pd.read_excel(path, engine="openpyxl")
    elif source_type == "parquet":
        return pd.read_parquet(path)
    elif source_type == "json":
        return pd.read_json(path, lines=True)
    else:
        raise ValueError(
            f"Unsupported source_type '{source_type}'. Use csv, excel, parquet, or json."
        )


def load_and_validate(
    path: str,
    source_type: str = "csv",
    column_mapping: Optional[Dict[str, str]] = None,
) -> pd.DataFrame:
    """Load a data source, optionally rename columns, and validate against the schema.

    Parameters
    ----------
    path: str
        File system path to the source dataset.
    source_type: str, default ``"csv"``
        The format of the source file – one of ``csv``, ``excel``, ``parquet`` or
        ``json``.
    column_mapping: dict, optional
        Mapping from *source* column names to the canonical names defined in the
        schema.  If ``None`` the function assumes the source already follows the
        canonical naming.
    """
    df = _load_file(path, source_type)
    if column_mapping:
        df = _apply_mapping(df, column_mapping)
    df = _validate_dataframe(df)
    return df


# ---------------------------------------------------------------------------
# Helper for quick conversion of an Excel file to the canonical Parquet format
# (useful for the one‑off migration you mentioned).
# ---------------------------------------------------------------------------
def convert_excel_to_parquet(
    excel_path: str,
    parquet_path: str,
    column_mapping: Optional[Dict[str, str]] = None,
) -> None:
    """Read an Excel workbook, rename columns, validate, and write Parquet.

    This wrapper is handy when you receive a new data dump from a foreign
    portal.  It guarantees that the resulting Parquet file conforms to the
    project's schema and can be loaded with the existing ``load_szamitott_master``
    routine.
    """
    df = load_and_validate(
        path=excel_path,
        source_type="excel",
        column_mapping=column_mapping,
    )
    df.to_parquet(parquet_path, index=False)
    print(f"✅ Converted {excel_path} → {parquet_path} (schema‑validated)")


# End of module

# -*- coding: utf-8 -*-
"""tests/test_integrity.py — séma- és adatintegritás tesztek.

Futtatás:
  pytest tests/                   # pytesttel
  python tests/test_integrity.py  # pytest nélkül is
"""

import os
import sys

from ingatlan_tdk import verify as vmd


def test_sha256_manifest():
    ok, msg = vmd.verify_sums()
    assert ok, msg


def test_kobanya_record_counts():
    import pandas as pd

    df = pd.read_parquet(vmd._abs("data/processed/kobanya_ingatlan_szamitott_master.parquet"))
    assert len(df) == 1320
    assert int((df["listing_type"] == "elado").sum()) == 1140
    assert int((df["listing_type"] == "kiado").sum()) == 180
    assert int((df["minta_garantalt_pontos"] == 1).sum()) == 296


def test_kobanya_no_missing_price_or_invalid_area():
    import pandas as pd

    df = pd.read_parquet(vmd._abs("data/processed/kobanya_ingatlan_szamitott_master.parquet"))
    assert int(df["price_huf"].isna().sum()) == 0
    assert int((df["alapterulet_nm"] <= 0).sum()) == 0


def test_kobanya_route_integrity():
    import pandas as pd

    df = pd.read_parquet(vmd._abs("data/processed/kobanya_ingatlan_szamitott_master.parquet"))
    cols = ["tavolsag_kotottpalya_halozati_m", "tavolsag_metro_halozati_m",
            "tavolsag_vasut_halozati_m", "tavolsag_villamos_halozati_m"]
    if set(cols).issubset(df.columns):
        m = df.dropna(subset=cols)
        min3 = m[cols[1:]].min(axis=1)
        assert int(((m[cols[0]] - min3).abs() > 1.0).sum()) == 0


def test_kobanya_isochrone_hierarchy():
    import pandas as pd

    df = pd.read_parquet(vmd._abs("data/processed/kobanya_ingatlan_szamitott_master.parquet"))
    for prefix in ("vasut", "metro", "villamos", "busz", "park", "kotottpalya",
                   "iskola", "ovoda", "bolt", "gyogyszertar", "orvos"):
        c5, c10, c15 = f"{prefix}_5p_seta", f"{prefix}_10p_seta", f"{prefix}_15p_seta"
        if {c5, c10, c15}.issubset(df.columns):
            m = df.dropna(subset=[c5, c10, c15])
            assert int(((m[c5] > m[c10]) | (m[c10] > m[c15])).sum()) == 0, prefix


def test_wien_record_counts():
    import pandas as pd

    p = vmd._abs("data/processed/wien_nordbahnhof_szamitott_master.parquet")
    if os.path.exists(p):
        df = pd.read_parquet(p)
        assert len(df) == 1037
        assert int((df["minta_garantalt_pontos"] == 1).sum()) == 324



if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    failed = 0
    for t in tests:
        try:
            t()
            print(f"[PASS] {t.__name__}")
        except Exception as e:
            failed += 1
            print(f"[FAIL] {t.__name__}: {e}")
    print(f"\n{len(tests) - failed}/{len(tests)} teszt sikeres.")
    sys.exit(1 if failed else 0)

# -*- coding: utf-8 -*-
"""tests/test_integrity.py — adatintegritás-tesztek az areas.yaml-ből (dinamikusan).

Nincs beégetett darabszám vagy területnév; ha a processed kimenetek még nem
léteznek, a tesztek jelzik (a pipeline futtatása után teljesek).
"""
import os
import sys

import pytest

from ingatlan_tdk import verify as vmd

REQ = ["data/schema.yaml", "data/areas.yaml"]


def test_config_files_exist():
    for rel in REQ:
        assert os.path.exists(vmd._abs(rel)), rel


def test_schema_required_nonempty():
    areas, schema = vmd.load_cfg()
    assert len(schema["required"]) > 0
    assert len(areas["areas"]) >= 1


def test_processed_masters_exist_and_invariants():
    areas, _ = vmd.load_cfg()
    missing = []
    for aid, cfg in (areas.get("areas") or {}).items():
        if not os.path.exists(vmd._abs(cfg["data"]["master_parquet"])):
            missing.append(aid)
    assert not missing, f"processed master hiányzik (futtasd a pipeline-t): {missing}"
    for name, passed in vmd.verify_structure():
        assert passed, name


def test_sha256_manifest():
    if not os.path.exists(vmd.SUMS_PATH):
        pytest.skip("SHA256SUMS meg nem generalt (pipeline --gen-sums)")
    ok, msg = vmd.verify_sums()
    assert ok, msg


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))
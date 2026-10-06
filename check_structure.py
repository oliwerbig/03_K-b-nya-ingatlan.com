#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""check_structure.py — repo-struktúra- és konvenció-ellenőrző.

A CONTRIBUTING.md strukturális szabályainak végrehajtható tükre.
Minden szabályváltozást ide is be kell vezetni (és fordítva).

Használat:
  python check_structure.py   # exit 0 = minden rendben, exit 1 = szabálysértés
"""

import os
import re
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))

# A gyökérben engedélyezett fájlok (CONTRIBUTING.md 2. szakasz).
ROOT_ALLOWED_FILES = {
    "README.md",
    "CONTRIBUTING.md",
    "AGENTS.md",
    "CHANGELOG.md",
    "Makefile",
    "pyproject.toml",
    ".editorconfig",
    ".pre-commit-config.yaml",
    ".gitignore",
    "requirements.txt",
    "requirements-dev.txt",
    "SHA256SUMS.txt",
    "build_all.py",
    "generate_area_report.py",
    "verify_master_data.py",
    "check_structure.py",
    "data_ingestion.py",
    "Start_JupyterLab.bat",
}

# A gyökérben engedélyezett mappák.
ROOT_ALLOWED_DIRS = {
    "docs",
    "data",
    "notebooks",
    "report_engine",
    "scripts",
    "tests",
    "html_reports",
    "archive",
    ".github",
    ".git",
    ".venv",
    "__pycache__",
    ".ruff_cache",
    ".pytest_cache",
}

# Fájlnevek, amelyek sehol sem lehetnek a projektfában (.git/.venv/archive kivételével).
FORBIDDEN_FILES = {"desktop.ini", ".DS_Store", "Thumbs.db"}

NOTEBOOK_RE = re.compile(r"^\d{2}_[a-z0-9_]+\.ipynb$")
SCRIPT_RE = re.compile(r"^(fetch|enrich|preprocess)_[a-z0-9_]+\.py$")

SKIP_DIRS = {".git", ".venv", "archive", ".ruff_cache", ".pytest_cache", "__pycache__"}


def violations():
    v = []

    # 1) Gyökér: csak a kanonikus fájlok/mappák
    for name in sorted(os.listdir(ROOT)):
        p = os.path.join(ROOT, name)
        if os.path.isdir(p):
            if name not in ROOT_ALLOWED_DIRS:
                v.append(f"gyökér: nem kanonikus mappa: {name}/")
        else:
            if name not in ROOT_ALLOWED_FILES:
                v.append(f"gyökér: nem kanonikus fájl: {name}")

    # 2) Notebook-elnevezés: NN_tema_nev.ipynb
    nb_dir = os.path.join(ROOT, "notebooks")
    if os.path.isdir(nb_dir):
        for name in sorted(os.listdir(nb_dir)):
            if name.endswith(".ipynb") and not NOTEBOOK_RE.match(name):
                v.append(f"notebooks/: nem konform elnevezés: {name}")

    # 3) Script-elnevezés: fetch_/enrich_/preprocess_ prefix
    sc_dir = os.path.join(ROOT, "scripts")
    if os.path.isdir(sc_dir):
        for name in sorted(os.listdir(sc_dir)):
            if name.endswith(".py") and not SCRIPT_RE.match(name):
                v.append(f"scripts/: nem konform scriptnév: {name}")

    # 4) Tiltott fájlok és checkpoint-mappák a projektfában
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for d in dirnames:
            if d == ".ipynb_checkpoints":
                v.append(f"tilos mappa: {os.path.relpath(os.path.join(dirpath, d), ROOT)}")
        for fn in filenames:
            if fn.lower() in FORBIDDEN_FILES:
                v.append(f"tilos fájl: {os.path.relpath(os.path.join(dirpath, fn), ROOT)}")

    # 5) SHA256-manifest: teljes és minden fájl létezik
    import verify_master_data as vmd

    if os.path.exists(vmd.SUMS_PATH):
        manifest = set()
        with open(vmd.SUMS_PATH, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                _, _, rel = line.partition("  ")
                manifest.add(rel)
        expected = set(vmd.FILES)
        if manifest != expected:
            missing = sorted(expected - manifest)
            extra = sorted(manifest - expected)
            if missing:
                v.append(f"SHA256SUMS.txt: hiányzó bejegyzés(ek): {', '.join(missing)}")
            if extra:
                v.append(f"SHA256SUMS.txt: ismeretlen bejegyzés(ek): {', '.join(extra)}")
        for rel in sorted(manifest):
            if not os.path.exists(vmd._abs(rel)):
                v.append(f"SHA256SUMS.txt: hiányzó fájl: {rel}")

    # 6) areas.yaml: minden aktív terület master parquet-ja létezik
    import yaml

    cfg_path = os.path.join(ROOT, "data", "areas.yaml")
    if os.path.exists(cfg_path):
        with open(cfg_path, "r", encoding="utf-8") as f:
            cfg = yaml.safe_load(f) or {}
        for aid, a in (cfg.get("areas") or {}).items():
            if not a.get("is_active", True):
                continue
            mp = (a.get("data") or {}).get("master_parquet")
            if mp and not os.path.exists(os.path.join(ROOT, mp.replace("/", os.sep))):
                v.append(f"areas.yaml: aktív terület ({aid}) master parquet-ja hiányzik: {mp}")

    # 7) requirements-dev.txt a requirements.txt-re épül
    dev_req = os.path.join(ROOT, "requirements-dev.txt")
    if os.path.exists(dev_req):
        with open(dev_req, "r", encoding="utf-8") as f:
            first = f.readline().strip()
        if first != "-r requirements.txt":
            v.append("requirements-dev.txt: az első sor '-r requirements.txt' kell legyen")

    return v


def main():
    v = violations()
    if v:
        print("STRUKTÚRA-ELLENŐRZÉS: SZABÁLYSÉRTÉS(ek) TALÁLHATÓK:")
        for line in v:
            print(f"  [!] {line}")
        print(f"\n{len(v)} szabálysértés. Lásd: CONTRIBUTING.md")
        sys.exit(1)
    print("STRUKTÚRA-ELLENŐRZÉS: MINDEN RENDBEN.")
    sys.exit(0)


if __name__ == "__main__":
    main()

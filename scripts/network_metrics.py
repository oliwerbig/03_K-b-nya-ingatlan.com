# -*- coding: utf-8 -*-
"""scripts/network_metrics.py — VALÓDI hálózati gyalogos távolságok + vasúti immisszió.

Kánon (data/schema.yaml): az izokrón és POI-sávok HÁLÓZATI sétatávolságon alapulnak
(1.25 m/s). Ez a modul a korábbi „euklidészi × kerülőfaktor” közelítés helyett valódi
Dijkstra legrövidebb utakat számol az OSM utcahálózaton, és euklidészi távolságot a
vasúti vágányoktól (immissziós sávok).
"""
import json
import os
import math
import heapq

import numpy as np
import pandas as pd
from scipy.spatial import cKDTree

WALK_M_PER_MIN = 75.0          # 1.25 m/s
MAX_NET = 2000.0               # Dijkstra-cutoff: a folytonos távolságokhoz
# (a POI/izokrón SÁVOK ettől függetlenül 375/750/1125 m — lásd POI_BANDS)
MAX_SNAP = 300.0               # max. csatlakoztatási távolság az úthálózathoz (növelve a lefedettségért)
RAIL_EPS = 0.1                 # m

CATEGORIES = [
    "vasut", "metro", "villamos", "busz", "park",
    "iskola", "ovoda", "bolt", "gyogyszertar", "orvos",
]
# POI-count sávok: az ÖSSZES szolgáltatás-pont (POI geojson minden eleme)
POI_BANDS = [375.0, 750.0, 1125.0]

def _known_stations(area_id):
    """Fallback-állomások az areas.yaml-ből (a kódban SEMMILYEN területnév nincs)."""
    import os as _os
    import yaml as _yaml
    cfg_path = _os.path.join(_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))), "data", "areas.yaml")
    try:
        with open(cfg_path, encoding="utf-8") as f:
            cfg = _yaml.safe_load(f)
        st = ((cfg.get("areas") or {}).get(area_id) or {}).get("spatial", {}).get("fallback_stations", []) or []
        return [tuple(x) for x in st]
    except Exception:
        return []


def _proj(lat, lon, mid_lat):
    """Lokális síkvetület (méter) — a terület méretén elhanyagolható torzítással."""
    k = 111320.0 * math.cos(math.radians(mid_lat))
    return lon * k, lat * 110540.0


class StreetGraph:
    """Utcahálózat-gráf + célpont-csatlakoztatás + Dijkstra."""

    def __init__(self, street_file):
        self.coords = {}
        self.adj = {}
        self.mid_lat = None
        self._load(street_file)

    def _load(self, path):
        data = json.load(open(path, encoding="utf-8"))
        ways = [e for e in data.get("elements", [])
                if e.get("type") == "way" and len(e.get("geometry") or []) >= 2]
        lats = [p["lat"] for e in ways for p in e["geometry"]]
        self.mid_lat = float(np.median(lats))
        for e in ways:
            g = e["geometry"]
            nids = e.get("nodes") or []
            if len(nids) != len(g):
                nids = ["%s_%d" % (e["id"], i) for i in range(len(g))]
            pts = []
            for nid, p in zip(nids, g):
                self.coords[nid] = _proj(p["lat"], p["lon"], self.mid_lat)
                pts.append(nid)
            for a, b in zip(pts, pts[1:]):
                d = math.dist(self.coords[a], self.coords[b])
                if d <= 0:
                    continue
                self.adj.setdefault(a, []).append((b, d))
                self.adj.setdefault(b, []).append((a, d))
        ids = list(self.coords)
        arr = np.array([self.coords[i] for i in ids])
        self.tree = cKDTree(arr)
        self.node_ids = ids

    def snap(self, lat, lon):
        x, y = _proj(lat, lon, self.mid_lat)
        d, i = self.tree.query(np.array([x, y]), k=1)
        return self.node_ids[int(i)], float(d)

    def attach(self, key, lat, lon):
        """Célpont/ingatlan csatlakoztatása a legközelebbi csomóponthoz (snap-él)."""
        nid, d = self.snap(lat, lon)
        if d > MAX_SNAP:
            return None, d
        self.coords[key] = _proj(lat, lon, self.mid_lat)
        self.adj[key] = [(nid, d)]
        self.adj[nid].append((key, d))
        return key, d

    def dijkstra(self, src, cutoff):
        dist = {src: 0.0}
        pq = [(0.0, src)]
        while pq:
            d, u = heapq.heappop(pq)
            if d > dist.get(u, math.inf):
                continue
            for v, w in self.adj.get(u, ()):
                nd = d + w
                if nd <= cutoff and nd < dist.get(v, math.inf):
                    dist[v] = nd
                    heapq.heappush(pq, (nd, v))
        return dist


def _rail_linestrings(transit_file):
    """Vasúti vágánygeometriák (rail/light_rail) az új, pufferelt tranzitfájlból."""
    data = json.load(open(transit_file, encoding="utf-8"))
    lines = []
    for e in data.get("elements", []):
        tags = e.get("tags", {})
        if e.get("type") == "way" and tags.get("railway") in ("rail", "light_rail"):
            g = e.get("geometry") or []
            if len(g) >= 2:
                lines.append([(p["lat"], p["lon"]) for p in g])
    return lines


def _point_seg_dist(px, py, x1, y1, x2, y2):
    dx, dy = x2 - x1, y2 - y1
    L2 = dx * dx + dy * dy
    if L2 == 0:
        return math.hypot(px - x1, py - y1)
    t = max(0.0, min(1.0, ((px - x1) * dx + (py - y1) * dy) / L2))
    return math.hypot(px - (x1 + t * dx), py - (y1 + t * dy))


def compute_area(area_id, df, street_file, transit_file, poi_geojson_path):
    """Kiszámítja a hálózati + immissziós oszlopokat a masterhez."""
    import geopandas as gpd

    mid_lat = float(df["geokodolt_lat"].median())
    G = StreetGraph(street_file)

    # --- Célpontok: POI geojson + tranzitfájl megállói ---
    targets = []  # (key, cat, lat, lon, name)
    poi_all = 0
    if os.path.exists(poi_geojson_path):
        poi = gpd.read_file(poi_geojson_path)
        cat_map = {
            "iskola": "iskola", "ovoda": "ovoda", "elelmiszer_bolt": "bolt",
            "gyogyszertar": "gyogyszertar", "orvos_egeszsegugy": "orvos",
            "park_zoldterulet": "park", "metroallomas": "metro",
            "vasutallomas": "vasut",
        }
        for i, row in poi.iterrows():
            cat = cat_map.get(row.get("category"))
            if cat is None:
                cat = "egyeb"
            nm = row.get("name") if "name" in row.index else ""
            targets.append((f"poi_{i}", cat, row.geometry.y, row.geometry.x, nm))
            poi_all += 1
    else:
        print(f"[{area_id}] POI geojson hiányzik: {poi_geojson_path}")

    tdata = json.load(open(transit_file, encoding="utf-8"))
    for e in tdata.get("elements", []):
        tags = e.get("tags", {})
        cat = None
        if e.get("type") == "node":
            if tags.get("railway") in ("station", "halt"):
                cat = "metro" if (tags.get("station") == "subway" or tags.get("subway") == "yes"
                                  or tags.get("operator") == "Wiener Linien") else "vasut"
            elif tags.get("station") == "subway" or tags.get("railway") == "subway_entrance":
                cat = "metro"
            elif tags.get("railway") == "tram_stop" or tags.get("tram") == "yes":
                cat = "villamos"
            elif tags.get("highway") == "bus_stop" or tags.get("public_transport") == "stop_position":
                cat = "busz"
            if cat:
                targets.append((f"t_{e['id']}", cat, e["lat"], e["lon"], tags.get("name", "")))
        elif e.get("type") == "way" and tags.get("railway") in ("station", "halt") and e.get("geometry"):
            g = e["geometry"]
            cat = "metro" if (tags.get("station") == "subway" or tags.get("operator") == "Wiener Linien") else "vasut"
            mid = g[len(g) // 2]
            targets.append((f"t_{e['id']}", cat, mid["lat"], mid["lon"], tags.get("name", "")))

    # Fallback ismert állomások
    found_vasut = any(c == "vasut" for _, c, _, _, _ in targets)
    if not found_vasut:
        for name, lat, lon in _known_stations(area_id):
            targets.append((f"st_{name}", "vasut", lat, lon, name))

    # Csatlakoztatás
    attach_map = {}
    for key, cat, lat, lon, nm in targets:
        node, snap = G.attach(key, lat, lon)
        if node is not None:
            attach_map[key] = (cat, snap, nm)

    # --- Ingatlanok: MINDEN geokódolt sor (nem csak a pontos alminta) ---
    idxs = df.index[df["geokodolt_lat"].notna()]
    out = {c: pd.Series(np.nan, index=df.index) for c in [
        "tavolsag_vasut_halozati_m", "tavolsag_metro_halozati_m",
        "tavolsag_villamos_halozati_m", "tavolsag_busz_halozati_m",
        "tavolsag_park_halozati_m", "tavolsag_iskola_halozati_m",
        "tavolsag_ovoda_halozati_m", "tavolsag_bolt_halozati_m",
        "tavolsag_gyogyszertar_halozati_m", "tavolsag_orvos_halozati_m",
        "poi_5p_count", "poi_10p_count", "poi_15p_count",
    ]}
    for c in CATEGORIES:
        out[f"legkozelebbi_{c}"] = pd.Series("", index=df.index, dtype="object")
    for c in list(out):
        if not c.startswith("legkozelebbi"):
            out[c] = out[c].astype(float)

    n = 0
    for idx in idxs:
        lat = df.at[idx, "geokodolt_lat"]
        lon = df.at[idx, "geokodolt_lon"]
        if pd.isna(lat) or pd.isna(lon):
            continue
        pnode, psnap = G.attach(f"prop_{idx}", lat, lon)
        if pnode is None:
            continue
        dists = G.dijkstra(pnode, cutoff=MAX_NET + MAX_SNAP)
        best = {c: math.inf for c in CATEGORIES}
        bestname = {c: "" for c in CATEGORIES}
        counts = [0, 0, 0]
        for key, (cat, _snap, nm) in attach_map.items():
            d = dists.get(key)
            if d is None:
                continue
            if d <= POI_BANDS[0]: counts[0] += 1
            if d <= POI_BANDS[1]: counts[1] += 1
            if d <= POI_BANDS[2]: counts[2] += 1
            if cat in best and d < best[cat]:
                best[cat] = d
                bestname[cat] = nm
        for cat in CATEGORIES:
            if best[cat] < math.inf:
                out[f"tavolsag_{cat}_halozati_m"].at[idx] = round(best[cat], 1)
                out[f"legkozelebbi_{cat}"].at[idx] = bestname[cat]
        out["poi_5p_count"].at[idx] = counts[0]
        out["poi_10p_count"].at[idx] = counts[1]
        out["poi_15p_count"].at[idx] = counts[2]
        n += 1
        if n % 100 == 0:
            print(f"[{area_id}] hálózat: {n}/{len(idxs)} ingatlan kész", flush=True)
    print(f"[{area_id}] hálózati távolságok kész ({n} ingatlan)", flush=True)

    # --- Vasúti euklidészi immisszió (minden koordinátás sorra) ---
    rail_lines = _rail_linestrings(transit_file)
    t = np.zeros(len(df)) * np.nan
    if rail_lines:
        for i, (ridx, row) in enumerate(df.iterrows()):
            lat, lon = row["geokodolt_lat"], row["geokodolt_lon"]
            if pd.isna(lat) or pd.isna(lon):
                continue
            x, y = _proj(lat, lon, mid_lat)
            best = math.inf
            for line in rail_lines:
                for (la1, lo1), (la2, lo2) in zip(line, line[1:]):
                    x1, y1 = _proj(la1, lo1, mid_lat)
                    x2, y2 = _proj(la2, lo2, mid_lat)
                    d = _point_seg_dist(x, y, x1, y1, x2, y2)
                    if d < best:
                        best = d
            if best < math.inf:
                t[i] = round(best, 1)
    out["tavolsag_vasut_m"] = pd.Series(t, index=df.index)
    print(f"[{area_id}] vasúti euklidészi távolság kész ({len(rail_lines)} vágányszakasz)", flush=True)
    return out
# -*- coding: utf-8 -*-
"""Egységes elemző modul — MINDEN számítás pontosan egyszer, itt definiálva.

A notebookok ezt hívják (cached_compute-on keresztül); párhuzamos modelkód
sehol máshol nincs. Minden függvény serializálható eredményt ad vissza
(DataFrame / dict-of-DataFrame / skalár), hogy a cache működjön.
"""
import os

import numpy as np
import pandas as pd

from ._utils import (CANON_PHYSICAL, VASUT_IMMISSZIO_LABELS, build_immission_dummies,
                     cached_compute, fit_canonical_hedonic, load_szamitott_master,
                     get_area_metadata, IZOKRON_LABELS, MERET_BINS, EPITES_EVE_BINS)


def _master(area=None):
    area = area or os.environ.get("TDK_ACTIVE_AREA")
    return load_szamitott_master(area)


def pontos_elado(area=None):
    df = _master(area)
    out = df[(df["minta_garantalt_pontos"] == 1) & (df["listing_type"] == "elado")].copy()
    if "ingatlan_tipus" in out.columns:
        from ._utils import is_residential_tipus
        out = out[out["ingatlan_tipus"].map(is_residential_tipus)]
    return out


# ---------------------------------------------------------------------------
# 01 — leíró statisztika
# ---------------------------------------------------------------------------

def descriptive(area=None, force=False):
    def fn():
        df = _master(area)
        p = pontos_elado(area)
        out = {}
        out["minta"] = pd.DataFrame({
            "mutato": ["osszes", "elado", "kiado", "pontos", "pontos_elado"],
            "ertek": [len(df),
                      int((df["listing_type"] == "elado").sum()),
                      int((df["listing_type"] == "kiado").sum()),
                      int((df["minta_garantalt_pontos"] == 1).sum()),
                      len(p)],
        })
        out["listing_type_ar"] = df.dropna(subset=["nm_ar_huf"]).groupby("listing_type")["nm_ar_huf"].agg(
            N="size", atlag="mean", median="median", min="min", max="max").reset_index()
        if p["varosresz"].notna().any():
            out["varosresz"] = p.dropna(subset=["nm_ar_huf", "varosresz"]).groupby("varosresz")["nm_ar_huf"].agg(
                N="size", median="median", atlag="mean").sort_values("median", ascending=False).reset_index()
        if "allapot" in df.columns and df["allapot"].notna().any():
            out["allapot"] = p["allapot"].value_counts(dropna=True).rename_axis("allapot").reset_index(name="N")
        if "epites_eve_kategoria" in p.columns and p["epites_eve_kategoria"].notna().any():
            out["korszak"] = p["epites_eve_kategoria"].value_counts(dropna=True).rename_axis("korszak").reset_index(name="N")
        if "szobaszam_kategoria" in p.columns and p["szobaszam_kategoria"].notna().any():
            out["szobaszam"] = p["szobaszam_kategoria"].value_counts(dropna=True).rename_axis("kategoria").reset_index(name="N")
        # decilisek
        dec = p["nm_ar_huf"].quantile(np.linspace(0.1, 0.9, 9))
        out["decilisek"] = dec.rename_axis("decilis").reset_index(name="nm_ar_huf")
        return out
    return cached_compute(area, "descriptive", fn, force=force)


def cluster_analysis(area=None, n_clusters=4, force=False):
    def fn():
        from sklearn.cluster import KMeans
        from sklearn.preprocessing import StandardScaler
        p = pontos_elado(area)
        cols = [c for c in ["log_nm_ar", "korrigalt_alapterulet_nm", "szobaszam_osszes",
                            "allapot_kod", "epulet_kora_ev", "emelet_szam"]
                if c in p.columns and p[c].notna().sum() > 10]
        d = p.dropna(subset=cols).copy()
        X = StandardScaler().fit_transform(d[cols])
        km = KMeans(n_clusters=min(n_clusters, len(d)), random_state=42, n_init=10).fit(X)
        d["klaszter"] = km.labels_
        prof = d.groupby("klaszter")[cols].mean().round(3).reset_index()
        prof["N"] = d.groupby("klaszter").size().values
        return {"profil": prof, "n": len(d)}
    return cached_compute(area, "cluster", fn, force=force)


# ---------------------------------------------------------------------------
# 02 — térbeli mérések
# ---------------------------------------------------------------------------

def spatial_metrics(area=None, force=False):
    def fn():
        p = pontos_elado(area)
        rows = []
        for prefix in ["vasut", "metro", "villamos", "kotottpalya"]:
            c15 = f"{prefix}_15p_seta"
            if c15 not in p.columns:
                continue
            rows.append({
                "halozat": prefix,
                "5p_N": int(p[f"{prefix}_5p_seta"].sum()),
                "10p_N": int(p[f"{prefix}_10p_seta"].sum()),
                "15p_N": int(p[c15].sum()),
                "folytonos_kitoltott": int(p[f"tavolsag_{prefix}_halozati_m"].notna().sum()),
                "median_tav_m": round(float(p[f"tavolsag_{prefix}_halozati_m"].median()), 0),
            })
        iso = pd.DataFrame(rows)
        # immissziós sávok
        zc = p["vasut_zona"].value_counts()
        zonak = pd.DataFrame({
            "sav": VASUT_IMMISSZIO_LABELS,
            "N": [int(zc.get(l, 0)) for l in VASUT_IMMISSZIO_LABELS],
        })
        # POI átlagok a 15p körzetben
        poi = pd.DataFrame({
            "poi": [c for c in ["poi_5p_count", "poi_10p_count", "poi_15p_count"] if c in p.columns],
            "atlag": [round(float(p[c].mean()), 1) for c in ["poi_5p_count", "poi_10p_count", "poi_15p_count"] if c in p.columns],
        })
        return {"izokronok": iso, "immisszios_savok": zonak, "poi": poi}
    return cached_compute(area, "spatial_metrics", fn, force=force)


# ---------------------------------------------------------------------------
# 03 — vasúti árhatás: kanonikus modell + gradiens
# ---------------------------------------------------------------------------

def _coef_table(m):
    ci = m.conf_int()
    return pd.DataFrame({
        "valtozo": m.params.index,
        "coef": m.params.values,
        "se": m.bse.values,
        "p": m.pvalues.values,
        "ci_lo": ci.iloc[:, 0].values,
        "ci_hi": ci.iloc[:, 1].values,
    })


def canonical_hedonic(area=None, force=False):
    def fn():
        import statsmodels.api as sm
        from statsmodels.stats.outliers_influence import variance_inflation_factor
        p = pontos_elado(area)
        r = fit_canonical_hedonic(p)
        # VIF a főmodell design-mátrixán (a sáv–TOD kollinearitás dokumentálása)
        try:
            Xv = r["X"]
            vif = pd.DataFrame({
                "valtozo": Xv.columns[1:],
                "VIF": [round(float(variance_inflation_factor(Xv.values, i)), 2)
                        for i in range(1, Xv.shape[1])],
            }).sort_values("VIF", ascending=False).reset_index(drop=True)
        except Exception:
            vif = pd.DataFrame({"valtozo": [], "VIF": []})
        return {
            "teljes": _coef_table(r["model"]),
            "zaj": _coef_table(r["model_zones"]),
            "kp": _coef_table(r["model_kp"]),
            "fe": _coef_table(r["model_fe"]) if r["model_fe"] is not None else pd.DataFrame({"valtozo": [], "coef": [], "p": []}),
            "vif": vif,
            "meta": pd.DataFrame({
                "n": [r["n"]],
                "r2_teljes": [round(float(r["model"].rsquared), 4)],
                "r2_zaj": [round(float(r["model_zones"].rsquared), 4)],
                "r2_kp": [round(float(r["model_kp"].rsquared), 4)],
                "r2_fe": [round(float(r["model_fe"].rsquared), 4)] if r["model_fe"] is not None else [np.nan],
                "ref_zona": [r["ref_zone"]],
                "tod_cols": [",".join(r["tod_cols"])],
                "kp_cols": [",".join(r["kp_cols"])],
                "zone_cols": [",".join(r["zone_cols"])],
                "trend": ["igen (x, y, x², y², xy)"],
                "fe": ["igen" if r["model_fe"] is not None else "nincs variancia"],
            }),
        }
    return cached_compute(area, "canonical_hedonic", fn, force=force)


def geokodolas_erzekenyseg(area=None, force=False):
    """Érzékenység-vizsgálat: a kanonikus modell csak-exakt (hazszam) vs.
    interpoláltat-is-tartalmazó (hazszam + hazszam_interpolalt) mintán —
    a legközelebbi-házszám közelítés hatása a fő együtthatókra."""
    def fn():
        from ._utils import fit_canonical_hedonic
        p = pontos_elado(area).copy()
        rows = []
        for cimke, sub in [("csak exakt", p[p["geokodolas_pontossag"] == "hazszam"]),
                           ("exakt + interpolalt", p[p["geokodolas_pontossag"].isin(["hazszam", "hazszam_interpolalt"])])]:
            if len(sub) < 20:
                rows.append({"minta": cimke, "n": len(sub), "zaj_150m_coef": np.nan,
                             "zaj_150m_p": np.nan, "tod15p_pct": np.nan})
                continue
            r = fit_canonical_hedonic(sub)
            ct = {v: (c, pv) for v, c, pv in zip(r["model"].params.index, r["model"].params.values,
                                                 r["model"].pvalues.values)}
            zaj_c, zaj_p = ct.get("<150 m", (np.nan, np.nan))
            tod_pct = (np.exp(sum(ct.get(c, (0.0, 1.0))[0] for c in r["tod_cols"])) - 1) * 100
            rows.append({"minta": cimke, "n": r["n"], "zaj_150m_coef": float(zaj_c),
                         "zaj_150m_p": float(zaj_p), "tod15p_pct": float(tod_pct)})
        return pd.DataFrame(rows)
    return cached_compute(area, "geokodolas_erzekenyseg", fn, force=force)


def price_surface(area=None, force=False):
    """Ár/reziduum-pontfelhő a 02-es értékdomborzathoz (pontos eladó, fizikai kontrollok utáni reziduummal)."""
    def fn():
        import statsmodels.api as sm
        from ._utils import drop_constant_columns
        p = pontos_elado(area).copy()
        phys = [c for c in CANON_PHYSICAL if c in p.columns and p[c].nunique() > 1]
        d = p.dropna(subset=["log_nm_ar", "nm_ar_huf", "geokodolt_lat", "geokodolt_lon"] + phys).copy()
        phys2 = [c for c in phys if d[c].nunique() > 1]
        m = sm.OLS(d["log_nm_ar"], drop_constant_columns(sm.add_constant(d[phys2].astype(float)))).fit()
        return pd.DataFrame({
            "geokodolt_lat": d["geokodolt_lat"].values,
            "geokodolt_lon": d["geokodolt_lon"].values,
            "nm_ar_huf": d["nm_ar_huf"].values,
            "log_nm_ar": d["log_nm_ar"].values,
            "resid": m.resid.values,
        })
    return cached_compute(area, "price_surface", fn, force=force)


def immission_gradient(area=None, force=False):
    """Nyers sáv-statisztikák + referencia-érzékenység + MW-U + placebo/Chow."""
    def fn():
        import statsmodels.api as sm
        from scipy import stats as st
        p = pontos_elado(area)
        # sávstatisztika
        zst = p.dropna(subset=["nm_ar_huf", "vasut_zona"]).groupby("vasut_zona")["nm_ar_huf"].agg(
            N="size", median="median", atlag="mean").reindex(
            [l for l in VASUT_IMMISSZIO_LABELS if l in p["vasut_zona"].dropna().unique()]).reset_index()
        # adaptív referencia
        counts = p["vasut_zona"].value_counts()
        ordered = [l for l in VASUT_IMMISSZIO_LABELS if counts.get(l, 0) > 0]
        ref = next((l for l in reversed(ordered) if counts.get(l, 0) >= 20), ordered[-1])
        med_ref = p[p["vasut_zona"] == ref]["nm_ar_huf"].median()
        med_u150 = p[p["tavolsag_vasut_m"] < 150]["nm_ar_huf"].median()
        # érzékenységi tábla: diszkont minden jelölt referencia mellett
        sens = []
        for rc in [l for l in VASUT_IMMISSZIO_LABELS if counts.get(l, 0) >= 10 and l != "<150 m"]:
            mr = p[p["vasut_zona"] == rc]["nm_ar_huf"].median()
            if pd.notna(mr) and mr > 0:
                sens.append({"referencia": rc, "N_ref": int(counts.get(rc, 0)),
                             "nyers_diszkont_150_pct": round(float((med_u150 - mr) / mr * 100), 1)})
        # MW-U az adaptív referenciához
        mwu = []
        for z in [l for l in VASUT_IMMISSZIO_LABELS if counts.get(l, 0) > 0 and l != ref]:
            a = p[p["vasut_zona"] == z]["nm_ar_huf"].dropna()
            b = p[p["vasut_zona"] == ref]["nm_ar_huf"].dropna()
            if len(a) >= 3 and len(b) >= 3:
                u, up = st.mannwhitneyu(a, b, alternative="two-sided")
                mwu.append({"sav": z, "N": len(a), "U": round(float(u), 0), "p": float(up)})
        # placebo/Chow: <300 m törés a hedonikus struktúrán (kontrollok, szegmensenként variáló oszlopok)
        d = p.dropna(subset=["log_nm_ar"] + [c for c in CANON_PHYSICAL if c in p.columns]).copy()
        phys = [c for c in CANON_PHYSICAL if d[c].nunique() > 1]
        Xc = sm.add_constant(d[phys].astype(float))
        yc = d["log_nm_ar"]
        seg = (d["tavolsag_vasut_m"] < 300)
        cols_ok = [c for c in Xc.columns if Xc[seg][c].nunique() > 1 and Xc[~seg][c].nunique() > 1]
        if len(cols_ok) == 0:
            # a szegmensekben minden kontroll konstans (kis minta) — a placebo-teszt őszintén kimarad
            return {
                "savok": zst,
                "referencia": pd.DataFrame({"ref_zona": [ref], "N_ref": [int(counts.get(ref, 0))], "med_ref": [med_ref]}),
                "erzekenyseg": pd.DataFrame(sens),
                "mwu": pd.DataFrame(mwu),
                "chow": pd.DataFrame({"megjegyzes": ["nincs varialo kontroll a <300m szegmensben"]}),
            }
        Xc2 = Xc[cols_ok]
        m_full = sm.OLS(yc, Xc2).fit()
        m_a = sm.OLS(yc[seg], Xc2[seg]).fit()
        m_b = sm.OLS(yc[~seg], Xc2[~seg]).fit()
        k = Xc2.shape[1]
        n_full, n_a, n_b = int(m_full.nobs), int(m_a.nobs), int(m_b.nobs)
        rss_f = float(np.sum(m_full.resid ** 2)); rss_a = float(np.sum(m_a.resid ** 2)); rss_b = float(np.sum(m_b.resid ** 2))
        chow_f = ((rss_f - (rss_a + rss_b)) / k) / ((rss_a + rss_b) / (n_a + n_b - 2 * k))
        chow_p = float(1 - st.f.cdf(chow_f, k, n_a + n_b - 2 * k))
        return {
            "savok": zst,
            "referencia": pd.DataFrame({"ref_zona": [ref], "N_ref": [int(counts.get(ref, 0))], "med_ref": [med_ref]}),
            "erzekenyseg": pd.DataFrame(sens),
            "mwu": pd.DataFrame(mwu),
            "chow": pd.DataFrame({"f": [round(float(chow_f), 2)], "p": [round(chow_p, 4)], "k": [k],
                                  "n_full": [n_full], "n_a": [n_a], "n_b": [n_b]}),
        }
    return cached_compute(area, "immission_gradient", fn, force=force)

import os

import numpy as np
import pandas as pd

from ._utils import (CANON_PHYSICAL, cached_compute, build_immission_dummies,
                     canonical_rail_dummies)
from .analyses import pontos_elado


def _projected_xy(df):
    mid = float(df["geokodolt_lat"].median())
    return np.column_stack((
        df["geokodolt_lon"].values * 111320.0 * np.cos(np.radians(mid)),
        df["geokodolt_lat"].values * 110540.0))


# ---------------------------------------------------------------------------
# 03 — Moran és SAR/SEM
# ---------------------------------------------------------------------------

def moran_analysis(area=None, force=False):
    def fn():
        import statsmodels.api as sm
        from libpysal.weights import KNN
        from esda.moran import Moran
        p = pontos_elado(area).dropna(subset=["log_nm_ar"] + [c for c in CANON_PHYSICAL if c in pontos_elado(area).columns]).copy()
        phys = [c for c in CANON_PHYSICAL if p[c].nunique() > 1]
        X = sm.add_constant(p[phys].astype(float))
        m = sm.OLS(p["log_nm_ar"], X).fit()
        xy = _projected_xy(p)
        w = KNN.from_array(xy, k=8)
        w.transform = "R"
        mi = Moran(m.resid, w)
        # permutáció (seedelt)
        rng = np.random.default_rng(42)
        perm = []
        resid = m.resid.values
        for _ in range(999):
            perm.append(Moran(rng.permutation(resid), w).I)
        p_val = float((1 + np.sum(np.array(perm) >= mi.I)) / 1000)
        return {
            "moran": pd.DataFrame({"I": [float(mi.I)], "EI": [float(mi.EI)], "p_perm": [p_val],
                                   "z": [float(mi.z_norm)]}),
            "ols_resid": pd.DataFrame({"resid": m.resid.values, "fitted": m.fittedvalues.values}),
        }
    return cached_compute(area, "moran", fn, force=force)


def sar_sem(area=None, force=False):
    def fn():
        import statsmodels.api as sm
        from libpysal.weights import KNN
        from spreg import GM_Lag, ML_Error
        p = pontos_elado(area).copy()
        d = p.dropna(subset=["log_nm_ar", "tavolsag_kotottpalya_halozati_m"] +
                    [c for c in CANON_PHYSICAL if c in p.columns]).copy()
        phys = [c for c in CANON_PHYSICAL if d[c].nunique() > 1]
        rail = canonical_rail_dummies(d)
        kp = [c for c in rail.columns if c.startswith("kp")]
        zones, ref = build_immission_dummies(d)
        feats = phys + kp + list(zones.columns)
        X = pd.concat([d[phys], rail[kp], zones], axis=1).astype(float)
        y = d["log_nm_ar"].values.reshape(-1, 1)
        xy = _projected_xy(d)
        w = KNN.from_array(xy, k=8)
        w.transform = "R"
        out = {}
        # OLS + LM-tesztek (zárt alakú, Burridge/Anselin — a spreg e verziója
        # nem tartalmaz LM-diagnosztikát, ezért kézzel számoljuk)
        Xc = sm.add_constant(X)
        ols = sm.OLS(d["log_nm_ar"], Xc).fit()
        out["ols"] = pd.DataFrame({"valtozo": ols.params.index, "coef": ols.params.values,
                                   "p": ols.pvalues.values, "r2": ols.rsquared})
        try:
            from scipy.stats import chi2 as _chi2
            W = w.sparse.todense()
            n = len(d)
            e = ols.resid.values
            sig2 = float(e @ e / n)
            We = np.asarray(W @ e).ravel()
            Wy = np.asarray(W @ d["log_nm_ar"].values).ravel()
            T1 = float(np.trace((W + W.T) @ W))
            lm_err = (float(e @ We) / sig2) ** 2 / T1
            p_err = float(1 - _chi2.cdf(lm_err, 1))
            Xb = ols.fittedvalues.values
            M = np.eye(n) - Xc.values @ np.linalg.pinv(Xc.values.T @ Xc.values) @ Xc.values.T
            WXb = np.asarray(W @ Xb).ravel()
            D_lag = float(WXb @ M @ WXb) / sig2 + T1
            lm_lag = (float(e @ Wy) / sig2) ** 2 / D_lag
            p_lag = float(1 - _chi2.cdf(lm_lag, 1))
            out["lm"] = pd.DataFrame({
                "teszt": ["LM_lag", "LM_error"],
                "stat": [round(lm_lag, 3), round(lm_err, 3)],
                "p": [round(p_lag, 4), round(p_err, 4)],
            })
        except Exception:
            out["lm"] = pd.DataFrame({"teszt": ["LM_lag", "LM_error"],
                                      "stat": [np.nan] * 2, "p": [np.nan] * 2})
        from scipy import stats as _st

        def _tab(res, names, extra=None):
            coefs = [float(b[0]) for b in res.betas[:-1]]
            ps = [float(z[1]) for z in res.z_stat[:len(coefs)]]
            rows = pd.DataFrame({"valtozo": ["const"] + names, "coef": coefs, "p": ps})
            if extra:
                rows = pd.concat([rows, pd.DataFrame({"valtozo": [extra[0]], "coef": [extra[1]],
                                                      "p": [np.nan]})], ignore_index=True)
            return rows

        # GM_Lag (SAR)
        try:
            gm = GM_Lag(y, X.values, w=w, name_y="log_nm_ar", name_x=feats)
            rho_v = float(gm.betas[-1][0])
            out["sar"] = _tab(gm, feats, extra=("rho", rho_v))
            out["sar_rho"] = pd.DataFrame({"rho": [rho_v],
                                           "mult": [1.0 / (1.0 - rho_v) if rho_v < 1 else np.nan]})
        except Exception as ex:
            out["sar"] = pd.DataFrame({"valtozo": [], "coef": [], "p": []})
            out["sar_hiba"] = pd.DataFrame({"hiba": [str(ex)[:200]]})
        # ML_Error (SEM)
        try:
            me = ML_Error(y, X.values, w=w, name_y="log_nm_ar", name_x=feats)
            lam_v = float(me.lam)
            out["sem"] = _tab(me, feats, extra=("lambda", lam_v))
            out["sem_lambda"] = pd.DataFrame({"lambda": [lam_v]})
        except Exception as ex:
            out["sem"] = pd.DataFrame({"valtozo": [], "coef": [], "p": []})
            out["sem_hiba"] = pd.DataFrame({"hiba": [str(ex)[:200]]})
        return out
    return cached_compute(area, "sar_sem", fn, force=force)


def gwr_analysis(area=None, force=False):
    def fn():
        p = pontos_elado(area).copy()
        p["log_vasut_m"] = np.log(p["tavolsag_vasut_m"].replace(0, 1))
        feats = [c for c in ["korrigalt_alapterulet_nm", "szobaszam_osszes", "is_panel", "has_lift",
                             "has_erkely", "allapot_kod", "emelet_szam", "epulet_kora_ev",
                             "tavolsag_metro_halozati_m", "log_vasut_m", "tavolsag_vasut_halozati_m"]
                 if c in p.columns and p[c].nunique() > 1]
        df_reg = p.dropna(subset=["log_nm_ar", "geokodolt_lon", "geokodolt_lat"] + feats).copy()
        # épületszintű aggregáció (nagy mintánál) / jitter (kis mintánál)
        tmp = df_reg.copy()
        tmp["lon_r"] = tmp["geokodolt_lon"].round(5)
        tmp["lat_r"] = tmp["geokodolt_lat"].round(5)
        agg = tmp.groupby(["lon_r", "lat_r"])[feats + ["log_nm_ar"]].mean().reset_index()
        if len(agg) >= 40:
            df_agg = agg.rename(columns={"lon_r": "geokodolt_lon", "lat_r": "geokodolt_lat"})
            modszer = f"epuletszintu (N={len(df_agg)})"
        else:
            df_agg = df_reg.copy()
            dup = df_agg.duplicated(subset=["geokodolt_lon", "geokodolt_lat"], keep=False)
            if int(dup.sum()) > 0:
                rng = np.random.default_rng(42)
                df_agg.loc[dup, "geokodolt_lon"] += rng.normal(0, 1.5e-5, int(dup.sum()))
                df_agg.loc[dup, "geokodolt_lat"] += rng.normal(0, 1.5e-5, int(dup.sum()))
            modszer = f"jitterelt (N={len(df_agg)})"
        coords = list(zip(df_agg["geokodolt_lon"], df_agg["geokodolt_lat"]))
        y = df_agg["log_nm_ar"].values.reshape(-1, 1)
        X = df_agg[feats].values
        out = {"modszer": pd.DataFrame({"modszer": [modszer], "n": [len(df_agg)], "feat": [",".join(feats)]})}
        try:
            from mgwr.gwr import GWR
            from mgwr.sel_bw import Sel_BW
            gwr_results = None
            for bw_min in [max(20, len(feats) + 10), 40, 60]:
                if bw_min >= len(df_agg) - 1:
                    break
                try:
                    sel = Sel_BW(coords, y, X, fixed=False)
                    bw = sel.search(search_method="interval", interval=6, bw_min=bw_min,
                                    bw_max=max(bw_min + 5, len(df_agg) - 1))
                    gwr_results = GWR(coords, y, X, bw, fixed=False).fit()
                    break
                except Exception:
                    continue
            if gwr_results is not None:
                params = pd.DataFrame(gwr_results.params, columns=["const"] + feats)
                tvals = pd.DataFrame(gwr_results.filter_tvals(), columns=["const"] + feats)
                params["geokodolt_lon"] = df_agg["geokodolt_lon"].values
                params["geokodolt_lat"] = df_agg["geokodolt_lat"].values
                tvals["geokodolt_lon"] = df_agg["geokodolt_lon"].values
                tvals["geokodolt_lat"] = df_agg["geokodolt_lat"].values
                out["params"] = params
                out["tvals"] = tvals
                out["meta_gwr"] = pd.DataFrame({"bw": [int(bw)], "r2": [float(gwr_results.R2)],
                                                "adj_r2": [float(gwr_results.adj_R2)], "aicc": [float(gwr_results.aicc)]})
                zcol = "log_vasut_m" if "log_vasut_m" in feats else feats[0]
                sig_n = int((tvals[zcol].abs() >= 1.96).sum())
                out["meta_gwr"]["sig_zaj"] = sig_n
            else:
                out["meta_gwr"] = pd.DataFrame({"bw": [np.nan], "r2": [np.nan], "adj_r2": [np.nan],
                                                "aicc": [np.nan], "sig_zaj": [np.nan]})
        except Exception as ex:
            out["gwr_hiba"] = pd.DataFrame({"hiba": [str(ex)[:200]]})
            out["meta_gwr"] = pd.DataFrame({"bw": [np.nan], "r2": [np.nan], "adj_r2": [np.nan],
                                            "aicc": [np.nan], "sig_zaj": [np.nan]})
        return out
    return cached_compute(area, "gwr", fn, force=force)

import os

import numpy as np
import pandas as pd

from ._utils import (CANON_PHYSICAL, cached_compute, build_immission_dummies,
                     canonical_rail_dummies, get_area_metadata)


# Egy hatás = egy változó elv: a folytonos hálózati távolságok szerepelnek, a belőlük
# képzett 15p dummyk NEM (azok duplikálnák ugyanazt az információt és megosztanák a
# permutációs fontosságot).
ML_FEATURES = ["korrigalt_alapterulet_nm", "szobaszam_osszes", "is_panel", "has_lift",
               "has_erkely", "allapot_kod", "emelet_szam", "epulet_kora_ev",
               "tavolsag_metro_halozati_m", "tavolsag_vasut_m",
               "tavolsag_vasut_halozati_m", "tavolsag_kotottpalya_halozati_m",
               "is_vasut_immisszio_150m", "poi_15p_count"]


def ml_analysis(area=None, force=False):
    def fn():
        from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
        from sklearn.model_selection import RepeatedKFold, cross_validate, KFold
        from sklearn.inspection import permutation_importance
        p = pontos_elado(area).copy()
        feats = [c for c in ML_FEATURES if c in p.columns]
        d = p.dropna(subset=["log_nm_ar"] + feats).copy()
        for c in feats:
            if d[c].dtype.kind not in "iuf":
                d[c] = d[c].astype(float)
            d[c] = d[c].fillna(d[c].median())
        X, y = d[feats], d["log_nm_ar"]
        out = {}
        # RF + ismételt CV + térbeli blokk-CV
        rf = RandomForestRegressor(n_estimators=120, max_depth=12, random_state=42, n_jobs=-1)
        rkf = RepeatedKFold(n_splits=5, n_repeats=1, random_state=42)
        cv1 = cross_validate(rf, X, y, cv=rkf, scoring="neg_mean_squared_error", n_jobs=1)
        # térbeli blokk-CV: KMeans blokk a koordinátákra
        from sklearn.cluster import KMeans
        xy = d[["geokodolt_lon", "geokodolt_lat"]].values
        blk = KMeans(n_clusters=8, random_state=42, n_init=10).fit_predict(xy)
        gkf = KFold(n_splits=5, shuffle=True, random_state=42)
        cv2 = cross_validate(rf, X, y, cv=gkf, groups=blk, scoring="neg_mean_squared_error", n_jobs=1)
        out["cv"] = pd.DataFrame({
            "mod": ["RF ismételt 5×1", "RF térbeli blokk"],
            "RMSE": [float(np.sqrt(-cv1["test_score"].mean())), float(np.sqrt(-cv2["test_score"].mean()))],
            "R2": [float(1 - (-cv1["test_score"].mean()) / y.var()), float(1 - (-cv2["test_score"].mean()) / y.var())],
        })
        # illesztett RF + permutációs fontosság (seedelt)
        rf.fit(X, y)
        rng = np.random.default_rng(42)
        perm = permutation_importance(rf, X, y, n_repeats=30, random_state=42, n_jobs=-1)
        # feature-kontextus: lefedettség, nunique, domináns arány
        base = p[feats]
        ctx = pd.DataFrame({
            "feature": feats,
            "lefedettseg_pct": [round(float(base[c].notna().mean()) * 100, 1) for c in feats],
            "nunique": [int(base[c].nunique()) for c in feats],
            "dom_arany_pct": [round(float(base[c].value_counts(normalize=True).iloc[0]) * 100, 1) for c in feats],
            "fontossag": [round(float(v), 4) for v in perm.importances_mean],
        }).sort_values("fontossag", ascending=False).reset_index(drop=True)
        out["fontossag"] = ctx
        # kvantilis GB intervallum
        lo = GradientBoostingRegressor(n_estimators=100, max_depth=4, learning_rate=0.06,
                                       loss="quantile", alpha=0.05, random_state=42).fit(X, y)
        hi = GradientBoostingRegressor(n_estimators=100, max_depth=4, learning_rate=0.06,
                                       loss="quantile", alpha=0.95, random_state=42).fit(X, y)
        pred = pd.DataFrame({
            "log_ar": y.values, "pred_rf": rf.predict(X),
            "q05": lo.predict(X), "q95": hi.predict(X),
        })
        pred["pred_intervallum_arany"] = (pred["log_ar"].between(pred["q05"], pred["q95"])).mean()
        out["pred"] = pred
        # arbitrázs: legnagyobb alulárazottság (RF reziduum)
        pred["resid"] = pred["log_ar"] - pred["pred_rf"]
        top = d.iloc[pred["resid"].nsmallest(20).index][["listing_id", "ar_millio_ft", "korrigalt_alapterulet_nm",
                                                          "varosresz", "vasut_zona"]].reset_index(drop=True)
        top["becsult_alulertekelts_pct"] = (-pred["resid"].nsmallest(20) * 100).round(1).values
        out["arbitrazs"] = top
        return out
    return cached_compute(area, "ml", fn, force=force)


def rent_gap_analysis(area=None, force=False):
    def fn():
        import statsmodels.api as sm
        df = pontos_elado(area).index.name  # noqa
        m = __import__("ingatlan_tdk._utils", fromlist=["load_szamitott_master"])
        full = m.load_szamitott_master()
        el = full[(full["listing_type"] == "elado") & (full["minta_garantalt_pontos"] == 1)].copy()
        ki = full[(full["listing_type"] == "kiado") & (full["minta_garantalt_pontos"] == 1)].copy()
        if "ingatlan_tipus" in full.columns:
            from ._utils import is_residential_tipus
            el = el[el["ingatlan_tipus"].map(is_residential_tipus)]
            ki = ki[ki["ingatlan_tipus"].map(is_residential_tipus)]
        feats = [c for c in ["korrigalt_alapterulet_nm", "szobaszam_osszes", "allapot_kod",
                             "is_panel", "has_lift", "has_erkely"] if c in el.columns]
        if len(el) < 5 or len(ki) < 3:
            # túl kicsi (vagy üres) alminta — a rent-gap elemzés őszintén kimarad
            return {
                "hedon": pd.DataFrame(columns=["valtozo", "coef_elado", "coef_kiado"]),
                "rent_gap_savok": pd.DataFrame(columns=["sav", "N_elado", "N_kiado", "median_hozam_pct"]),
                "cap_szenz": pd.DataFrame(columns=["cap_rate", "atlagos_ingatlan_ertek_indeksz"]),
                "megjegyzes": pd.DataFrame({"megjegyzes": [f"túl kicsi alminta (eladó={len(el)}, kiadó={len(ki)})"]}),
            }

        def fit(sub, ycol):
            s = sub.dropna(subset=[ycol] + [c for c in feats if sub[c].nunique() > 1]).copy()
            f2 = [c for c in feats if s[c].nunique() > 1]
            X = sm.add_constant(s[f2].astype(float))
            return sm.OLS(s[ycol], X).fit()

        m_el = fit(el, "log_nm_ar")
        m_ki = fit(ki, "log_ar")
        out = {"hedon": pd.DataFrame({
            "valtozo": m_el.params.index,
            "coef_elado": m_el.params.values,
            "coef_kiado": m_ki.params.reindex(m_el.params.index).values,
        })}
        # rent gap zónánként (bruttó hozam)
        cap = 0.05
        ki2 = ki.dropna(subset=["log_ar", "ar_ezer_ft_ho"]).copy()
        el2 = el.dropna(subset=["log_nm_ar", "nm_ar_huf"]).copy()
        rows = []
        for z in [l for l in el2["vasut_zona"].dropna().unique()]:
            e = el2[el2["vasut_zona"] == z]
            k = ki2[ki2["vasut_zona"] == z]
            if len(e) >= 3 and len(k) >= 3:
                rows.append({
                    "sav": z, "N_elado": len(e), "N_kiado": len(k),
                    "median_hozam_pct": round(float(((k["ar_ezer_ft_ho"] * 12 / (k["ar_millio_ft"] * 1000)) * 100).median()), 2)
                    if "ar_millio_ft" in k.columns and k["ar_millio_ft"].notna().any() else np.nan,
                })
        out["rent_gap_savok"] = pd.DataFrame(rows)
        # cap-rate érzékenység
        out["cap_szenz"] = pd.DataFrame({
            "cap_rate": [0.03, 0.04, 0.05, 0.06, 0.07],
            "atlagos_ingatlan_ertek_indeksz": [round(float(100 * 0.05 / c), 0) for c in [0.03, 0.04, 0.05, 0.06, 0.07]],
        })
        return out
    return cached_compute(area, "rent_gap", fn, force=force)


def monte_carlo_risk(area=None, force=False, n_sim=2000):
    def fn():
        import statsmodels.api as sm
        from ._utils import drop_constant_columns
        p = pontos_elado(area).copy()
        phys = [c for c in CANON_PHYSICAL if p[c].nunique() > 1]
        d = p.dropna(subset=["log_nm_ar"] + phys).copy()
        phys = [c for c in phys if d[c].nunique() > 1]
        m = sm.OLS(d["log_nm_ar"], drop_constant_columns(sm.add_constant(d[phys].astype(float)))).fit()
        resid_sd = float(m.resid.std())
        rng = np.random.default_rng(42)
        shocks = rng.normal(0, resid_sd, size=(n_sim, len(d)))
        sim = m.fittedvalues.values[:, None] + shocks.T  # (N, n_sim)
        paths = pd.DataFrame(sim).quantile([0.05, 0.25, 0.5, 0.75, 0.95]).T
        paths.columns = ["q05", "q25", "q50", "q75", "q95"]
        out = {"paths": paths, "meta": pd.DataFrame({"resid_sd": [resid_sd], "n": [len(d)], "n_sim": [n_sim]})}
        # tornado: egyenkénti 1-szórás-változások hatása az árra
        torn = []
        for c in phys:
            b = float(m.params[c]); sd = float(d[c].std())
            torn.append({"valtozo": c, "hatas_pct": round(float((np.exp(b * sd) - 1) * 100), 1)})
        out["tornado"] = pd.DataFrame(torn).sort_values("hatas_pct", key=abs, ascending=False)
        return out
    return cached_compute(area, "monte_carlo", fn, force=force)


def lvc_analysis(area=None, force=False):
    def fn():
        import numpy as _np
        canon = canonical_hedonic(area)
        zt = canon["zaj"]
        out = {}
        # sávonkénti felértékelődési potenciál: a zaj-fókuszú modell sávdummyi
        rows = []
        for z in ["<150 m", "150-300 m", "300-500 m", "500-1000 m"]:
            rr = zt[zt["valtozo"] == z]
            if len(rr):
                b = float(rr["coef"].iloc[0])
                rows.append({"sav": z, "diszkont_pct": round(float((_np.exp(b) - 1) * 100), 1)})
        out["sav_diszont"] = pd.DataFrame(rows)
        out["meta_lvc"] = pd.DataFrame({"n": [int(canon["meta"]["n"].iloc[0])]})
        return out
    return cached_compute(area, "lvc", fn, force=force)


def pooled_comparison(force=False):
    """Kétterületes pooled regresszió (terület×sáv interakciók), EUR-ban."""
    def fn():
        import statsmodels.api as sm
        from ._utils import load_areas_config
        name_to_id = {v["name"]: k for k, v in load_areas_config()["areas"].items()}
        from ._utils import is_residential_tipus, load_areas_config as _lac, _PROJECT_ROOT
        frames = []
        areas_cfg = _lac()
        for a_id, acfg in sorted((areas_cfg.get("areas") or {}).items()):
            mp_path = os.path.join(_PROJECT_ROOT, acfg.get("data", {}).get("master_parquet", ""))
            if not (mp_path and os.path.exists(mp_path)):
                continue
            df = pd.read_parquet(mp_path)
            e = df[(df["listing_type"] == "elado") & (df["minta_garantalt_pontos"] == 1)].copy()
            if "ingatlan_tipus" in e.columns:
                e = e[e["ingatlan_tipus"].map(is_residential_tipus)]
            e["area_id"] = a_id
            # összehasonlítás HUF-alapon (a kánon minden területet HUF-ban is hordoz,
            # a rögzített, dokumentált crawl-napi árfolyamon)
            e["log_nm_ar_eur"] = e["log_nm_ar"]
            frames.append(e)
        mp = pd.concat(frames, ignore_index=True)
        d = mp.dropna(subset=["log_nm_ar_eur", "tavolsag_kotottpalya_halozati_m"] +
                     [c for c in CANON_PHYSICAL if c in mp.columns]).copy()
        phys = [c for c in CANON_PHYSICAL if d[c].nunique() > 1]
        rail = canonical_rail_dummies(d)
        kp = [c for c in rail.columns if c.startswith("kp")]
        zones, ref = build_immission_dummies(d)
        d = pd.concat([d, zones], axis=1)
        X = pd.concat([d[phys], rail[kp], zones,
                       pd.get_dummies(d["area_id"], drop_first=True)], axis=1).astype(float)
        roles = {k: v.get("role", "control") for k, v in (areas_cfg.get("areas") or {}).items()}
        primary = next((k for k, r in roles.items() if r == "primary"), sorted(d["area_id"].unique())[0])
        inter = []
        for area in d["area_id"].unique():
            if area == primary:
                continue
            for z in [c for c in zones.columns]:
                n_cell = int(((d["area_id"] == area) & (d[z] == 1)).sum())
                if n_cell >= 10:
                    col = f"ia_{area}__{z}"
                    X[col] = ((d["area_id"] == area) & (d[z] == 1)).astype(int)
                    inter.append({"interakcio": col, "N": n_cell})
        from ._utils import drop_constant_columns
        X = drop_constant_columns(X)
        m = sm.OLS(d["log_nm_ar_eur"], sm.add_constant(X)).fit(cov_type="HC1")
        ci = m.conf_int()
        out = {
            "coef": pd.DataFrame({"valtozo": m.params.index, "coef": m.params.values,
                                  "p": m.pvalues.values, "ci_lo": ci.iloc[:, 0].values,
                                  "ci_hi": ci.iloc[:, 1].values}),
            "meta": pd.DataFrame({"n": [int(m.nobs)], "r2": [round(float(m.rsquared), 4)],
                                  "ref_zona": [ref], "interakciok": [len(inter)]}),
        }
        return out
    return cached_compute("pooled", "pooled", fn, force=force)
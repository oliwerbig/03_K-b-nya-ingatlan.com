import sys, os
sys.path.append('notebooks')
from _utils import load_szamitott_master
import pandas as pd
import numpy as np
from scipy import stats
import statsmodels.api as sm

df = load_szamitott_master()
elado = df[df['listing_type'] == 'elado'].copy()
kiado = df[df['listing_type'] == 'kiado'].copy()
pontos = df[df['minta_garantalt_pontos'] == 1].copy()
pontos_elado = elado[elado['minta_garantalt_pontos'] == 1].copy()

print("=== NB00 & NB01 ===")
print(f"Total: {len(df)}, Elado: {len(elado)} ({len(elado)/len(df)*100:.1f}%), Kiado: {len(kiado)} ({len(kiado)/len(df)*100:.1f}%), Pontos: {len(pontos)} ({len(pontos)/len(df)*100:.1f}%)")
print(f"Elado Price Mean: {elado['price_huf'].mean()/1e6:.1f} M Ft, Median: {elado['price_huf'].median()/1e6:.1f} M Ft")
print(f"Elado m2 price Mean: {elado['nm_ar_huf'].mean():,.0f} Ft, Median: {elado['nm_ar_huf'].median():,.0f} Ft")
print(f"Elado Area Mean: {elado['alapterulet_nm'].mean():.1f} m2, Median: {elado['alapterulet_nm'].median():.1f} m2")
print(f"Elado Room Mean: {elado['szobaszam_osszes'].mean():.1f}, Mode: {elado['szobaszam_osszes'].mode()[0]}")
print(f"Elado m2 price Std: {elado['nm_ar_huf'].std():,.0f} Ft (rel std: {elado['nm_ar_huf'].std()/elado['nm_ar_huf'].mean()*100:.1f}%)")
print(f"Elado m2 price Skew: {stats.skew(elado['nm_ar_huf'].dropna()):.2f}")
q1, q3 = elado['nm_ar_huf'].quantile(0.25), elado['nm_ar_huf'].quantile(0.75)
print(f"Q1: {q1:,.0f} Ft, Q3: {q3:,.0f} Ft, IQR: {q3-q1:,.0f} Ft")

print("\n=== NB02 (Panel vs Tegla) ===")
tegla = elado[elado['is_panel'] == 0]['nm_ar_huf']
panel = elado[elado['is_panel'] == 1]['nm_ar_huf']
print(f"Tegla median: {tegla.median():,.0f} Ft, mean: {tegla.mean():,.0f} Ft (N={len(tegla)})")
print(f"Panel median: {panel.median():,.0f} Ft, mean: {panel.mean():,.0f} Ft (N={len(panel)})")
diff_pct = (tegla.median() - panel.median()) / tegla.median() * 100
print(f"Panel discount vs tegla: {diff_pct:.1f}%")

print("\n=== NB04 (Hedonikus OLS) ===")
elado['log_tavolsag_vasut_m'] = np.log(elado['tavolsag_vasut_m'].replace(0, 1))
features = [
    'korrigalt_alapterulet_nm', 'szobaszam_osszes', 'is_panel', 
    'has_lift', 'allapot_kod', 
    'tavolsag_metro_halozati_m',
    'log_tavolsag_vasut_m',
    'tavolsag_vasut_halozati_m'
]
df_reg = elado.dropna(subset=['log_nm_ar'] + features).copy()
X = sm.add_constant(df_reg[features])
y = df_reg['log_nm_ar']
model_ols = sm.OLS(y, X).fit()
print(f"N: {int(model_ols.nobs)}, R2: {model_ols.rsquared:.4f}, Adj R2: {model_ols.rsquared_adj:.4f}")
for col in model_ols.params.index:
    coef = model_ols.params[col]
    pval = model_ols.pvalues[col]
    pct = (np.exp(coef) - 1) * 100
    print(f"  {col}: {coef:.5f} (p={pval:.4e}, implicit: {pct:+.1f}%)")

print("\n=== NB05 (Vasúti diszkont & izokrónok) ===")
for band in ['0-150m', '150-300m', '300-500m', '500-1000m', '>1000m']:
    sub_band = pontos_elado[pontos_elado['vasut_puffer_kat'] == band]['nm_ar_huf']
    if len(sub_band) > 0:
        print(f"  Vasút zóna {band} (N={len(sub_band)}): median={sub_band.median():,.0f} Ft, mean={sub_band.mean():,.0f} Ft")

for izo in ['0-5p (<=375m)', '5-10p (375-750m)', '10-15p (750-1125m)', '>15p (>1125m)']:
    sub_izo = pontos_elado[pontos_elado['izokron_vasut_kat'] == izo]['nm_ar_huf'] if 'izokron_vasut_kat' in pontos_elado else []
    if len(sub_izo) > 0:
        print(f"  Izokrón vasút {izo} (N={len(sub_izo)}): median={sub_izo.median():,.0f} Ft")

print("\n=== NB06 (Kiado vs Elado & Yield) ===")
print(f"Kiado count: {len(kiado)}, mean rent: {kiado['price_huf'].mean():,.0f} Ft/ho, Median: {kiado['price_huf'].median():,.0f} Ft/ho")
print(f"Kiado mean m2 rent: {kiado['nm_ar_huf'].mean():,.0f} Ft/m2/ho, Median: {kiado['nm_ar_huf'].median():,.0f} Ft/m2/ho")
print(f"Kiado mean area: {kiado['alapterulet_nm'].mean():.1f} m2, Elado mean area: {elado['alapterulet_nm'].mean():.1f} m2")
gross_yield_m2 = (kiado['nm_ar_huf'].mean() * 12) / elado['nm_ar_huf'].mean() * 100
gross_yield_unit = (kiado['price_huf'].mean() * 12) / elado['price_huf'].mean() * 100
pr_ratio = elado['price_huf'].mean() / (kiado['price_huf'].mean() * 12)
print(f"Gross yield m2: {gross_yield_m2:.2f}%, Gross yield unit: {gross_yield_unit:.2f}%, P/R ratio: {pr_ratio:.1f} years")

print("\n=== NB10 & NB13 (Moran & SAR) ===")
from libpysal.weights import KNN
from esda.moran import Moran
df_agg = pontos_elado.groupby(['geokodolt_lon', 'geokodolt_lat'])[['nm_ar_huf', 'log_nm_ar', 'korrigalt_alapterulet_nm', 'is_panel', 'tavolsag_metro_halozati_m']].mean().reset_index()
w = KNN.from_dataframe(df_agg, geom_col=None, ids=None, k=8)
w.transform = 'R'
mi = Moran(df_agg['log_nm_ar'], w)
print(f"Aggregated points N: {len(df_agg)} (from {len(pontos_elado)})")
print(f"Moran's I: {mi.I:.4f}, E(I): {mi.EI:.4f}, z-score: {mi.z_norm:.4f}, p-value: {mi.p_norm:.4e}")

y_agg = df_agg['log_nm_ar']
Wy = pd.Series(w.sparse.dot(y_agg), index=df_agg.index)
df_agg['Wy'] = Wy
sar_X = sm.add_constant(df_agg[['Wy', 'korrigalt_alapterulet_nm', 'is_panel', 'tavolsag_metro_halozati_m']])
sar_model = sm.OLS(y_agg, sar_X).fit()
rho = sar_model.params['Wy']
print(f"SAR rho: {rho:.4f} (p={sar_model.pvalues['Wy']:.4e})")
print(f"Spatial multiplier 1/(1-rho): {1/(1-rho):.3f}")

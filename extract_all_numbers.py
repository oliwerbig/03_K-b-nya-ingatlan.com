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
pontos_elado = elado[elado['minta_garantalt_pontos'] == 1].copy()

out = {}

# NB00 & NB01
out['n_total'] = len(df)
out['n_elado'] = len(elado)
out['pct_elado'] = len(elado)/len(df)*100
out['n_kiado'] = len(kiado)
out['pct_kiado'] = len(kiado)/len(df)*100
out['n_pontos'] = len(df[df['minta_garantalt_pontos'] == 1])
out['pct_pontos'] = out['n_pontos']/len(df)*100
out['elado_mean_price_m'] = elado['price_huf'].mean() / 1e6
out['elado_median_price_m'] = elado['price_huf'].median() / 1e6
out['elado_mean_nm_ar'] = elado['nm_ar_huf'].mean()
out['elado_median_nm_ar'] = elado['nm_ar_huf'].median()
out['elado_mean_area'] = elado['alapterulet_nm'].mean()
out['elado_median_area'] = elado['alapterulet_nm'].median()
out['elado_mean_rooms'] = elado['szobaszam_osszes'].mean()
out['elado_mode_rooms'] = elado['szobaszam_osszes'].mode()[0]
out['elado_std_nm_ar'] = elado['nm_ar_huf'].std()
out['elado_rel_std'] = elado['nm_ar_huf'].std() / elado['nm_ar_huf'].mean() * 100
out['elado_skew'] = stats.skew(elado['nm_ar_huf'].dropna())
out['q1'] = elado['nm_ar_huf'].quantile(0.25)
out['q3'] = elado['nm_ar_huf'].quantile(0.75)
out['iqr'] = out['q3'] - out['q1']

# NB02
tegla = elado[elado['is_panel'] == 0]['nm_ar_huf']
panel = elado[elado['is_panel'] == 1]['nm_ar_huf']
out['tegla_median'] = tegla.median()
out['panel_median'] = panel.median()
out['panel_discount_pct'] = (tegla.median() - panel.median()) / tegla.median() * 100

# NB04
elado['log_tavolsag_vasut_m'] = np.log(elado['tavolsag_vasut_m'].replace(0, 1))
features = ['korrigalt_alapterulet_nm', 'szobaszam_osszes', 'is_panel', 'has_lift', 'allapot_kod', 'tavolsag_metro_halozati_m', 'log_tavolsag_vasut_m', 'tavolsag_vasut_halozati_m']
df_reg = elado.dropna(subset=['log_nm_ar'] + features).copy()
m_ols = sm.OLS(df_reg['log_nm_ar'], sm.add_constant(df_reg[features])).fit()
out['ols_r2'] = m_ols.rsquared
out['ols_r2_adj'] = m_ols.rsquared_adj
out['ols_n'] = int(m_ols.nobs)
out['ols_zaj_coef'] = m_ols.params['log_tavolsag_vasut_m']
out['ols_zaj_pval'] = m_ols.pvalues['log_tavolsag_vasut_m']
out['ols_panel_coef'] = m_ols.params['is_panel']
out['ols_panel_disc'] = (np.exp(m_ols.params['is_panel']) - 1) * 100
out['ols_allapot_coef'] = m_ols.params['allapot_kod']
out['ols_allapot_prem'] = (np.exp(m_ols.params['allapot_kod']) - 1) * 100
out['ols_metro_coef'] = m_ols.params['tavolsag_metro_halozati_m']

# NB05
elado['vasut_zona'] = pd.cut(
    elado['tavolsag_vasut_m'],
    bins=[0, 150, 300, 500, 1000, 2000, 10000],
    labels=['<150 m (Immisszió)', '150-300 m (Erős teher)', '300-500 m (Átmeneti)', '500-1000 m (Háttérzaj)', '1000-2000 m (Közepes ref.)', '>2000 m (Tiszta ref.)']
)
out['med_under150'] = elado[elado['vasut_zona'] == '<150 m (Immisszió)']['nm_ar_huf'].median()
out['med_ref'] = elado[elado['vasut_zona'].isin(['1000-2000 m (Közepes ref.)', '>2000 m (Tiszta ref.)'])]['nm_ar_huf'].median()
out['vasut_diszkont_pct'] = ((out['med_under150'] - out['med_ref']) / out['med_ref']) * 100
out['n_terhelt_300'] = int((elado['tavolsag_vasut_m'] < 300).sum())
kw_groups = [g['nm_ar_huf'].values for _, g in elado.dropna(subset=['vasut_zona']).groupby('vasut_zona', observed=True)]
kw_stat, kw_p = stats.kruskal(*kw_groups)
out['kw_stat'] = kw_stat
out['kw_p'] = kw_p

# NB06
out['kiado_count'] = len(kiado)
out['kiado_mean_rent'] = kiado['price_huf'].mean()
out['kiado_median_rent'] = kiado['price_huf'].median()
out['kiado_mean_m2_rent'] = kiado['nm_ar_huf'].mean()
out['kiado_median_m2_rent'] = kiado['nm_ar_huf'].median()
out['kiado_mean_area'] = kiado['alapterulet_nm'].mean()
out['gross_yield_m2'] = (kiado['nm_ar_huf'].mean() * 12) / elado['nm_ar_huf'].mean() * 100
out['gross_yield_unit'] = (kiado['price_huf'].mean() * 12) / elado['price_huf'].mean() * 100
out['pr_ratio'] = elado['price_huf'].mean() / (kiado['price_huf'].mean() * 12)

# NB10 & NB13
from libpysal.weights import KNN
from esda.moran import Moran
df_agg = pontos_elado.groupby(['geokodolt_lon', 'geokodolt_lat'])[['nm_ar_huf', 'log_nm_ar', 'korrigalt_alapterulet_nm', 'is_panel', 'tavolsag_metro_halozati_m']].mean().reset_index()
w = KNN.from_array(df_agg[['geokodolt_lon', 'geokodolt_lat']], k=8)
w.transform = 'R'
mi = Moran(df_agg['log_nm_ar'], w)
out['moran_i'] = mi.I
out['moran_ei'] = mi.EI
out['moran_z'] = mi.z_norm
out['moran_p'] = mi.p_norm
out['agg_n'] = len(df_agg)

y_agg = df_agg['log_nm_ar']
Wy = pd.Series(w.sparse.dot(y_agg), index=df_agg.index)
df_agg['Wy'] = Wy
sar_model = sm.OLS(y_agg, sm.add_constant(df_agg[['Wy', 'korrigalt_alapterulet_nm', 'is_panel', 'tavolsag_metro_halozati_m']])).fit()
out['sar_rho'] = sar_model.params['Wy']
out['sar_mult'] = 1 / (1 - sar_model.params['Wy'])

for k, v in out.items():
    if isinstance(v, float):
        print(f"{k}: {v:.4f}")
    else:
        print(f"{k}: {v}")

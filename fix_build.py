import os

mapping = {
    "05_vasuti_diszkont_es_izokronok": "04_vasuti_diszkont_es_izokronok",
    "14_poi_es_15_perces_varos": "05_poi_es_15_perces_varos",
    "09_klaszter_es_tipologia": "06_klaszter_es_tipologia",
    "04_hedonikus_armodell": "07_hedonikus_armodell",
    "10_moran_es_autokorrelacio": "08_moran_es_autokorrelacio",
    "13_terokonometria_sar_sem": "09_terokonometria_sar_sem",
    "15_lokalis_terokonometria_gwr": "10_lokalis_terokonometria_gwr",
    "12_gepi_tanulas_es_arbitrazs": "11_gepi_tanulas_es_arbitrazs",
    "06_berleti_piac_es_rent_gap": "12_berleti_piac_es_rent_gap",
    "08_monte_carlo_kockazat": "13_monte_carlo_kockazat",
    "07_lvc_szimulacio": "14_lvc_szimulacio",
    "11_ingatlan_kereso_dashboard": "15_ingatlan_kereso_dashboard"
}

with open('build_all_notebooks.py', 'r', encoding='utf-8') as f:
    c = f.read()

for k, v in mapping.items():
    c = c.replace(f"'{k}.ipynb'", f"'TEMP_{v}.ipynb'")
    
for k, v in mapping.items():
    c = c.replace(f"'TEMP_{v}.ipynb'", f"'{v}.ipynb'")

with open('build_all_notebooks.py', 'w', encoding='utf-8') as f:
    f.write(c)

print("build_all_notebooks.py updated!")

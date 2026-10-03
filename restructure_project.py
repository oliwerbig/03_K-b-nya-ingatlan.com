import os
import glob
import re
import shutil
import time

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

folders = ["notebooks", "docs", "html_exports"]
extensions = [".ipynb", ".html"]

print("Starting safe rename process...")
# 1. Rename to temporary names to avoid collisions
temp_mapping = {}
for old_name, new_name in mapping.items():
    temp_name = "TEMP_" + new_name
    temp_mapping[old_name] = temp_name
    
    for folder in folders:
        for ext in extensions:
            old_path = os.path.join(folder, old_name + ext)
            temp_path = os.path.join(folder, temp_name + ext)
            if os.path.exists(old_path):
                os.rename(old_path, temp_path)

# 2. Rename from temporary to final names
for old_name, new_name in mapping.items():
    temp_name = "TEMP_" + new_name
    
    for folder in folders:
        for ext in extensions:
            temp_path = os.path.join(folder, temp_name + ext)
            new_path = os.path.join(folder, new_name + ext)
            if os.path.exists(temp_path):
                os.rename(temp_path, new_path)

print("Files renamed successfully.")

# 3. Update notebook_docs.py to reflect new numbering in the docs dictionary keys and texts
docs_path = "notebook_docs.py"
if os.path.exists(docs_path):
    with open(docs_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # We must be careful not to double replace. We'll replace the exact string keys.
    # We'll create a mapping of old keys to temporary tokens, then tokens to new keys.
    
    # Also update the dictionary keys for the titles in the docs dictionary.
    for old_name, new_name in mapping.items():
        # E.g., '05_vasuti_diszkont_es_izokronok' -> '04_vasuti_diszkont_es_izokronok'
        content = content.replace(f'"{old_name}"', f'"TEMP_{new_name}"')
        content = content.replace(f"'{old_name}'", f"'TEMP_{new_name}'")
        
    for old_name, new_name in mapping.items():
        content = content.replace(f'"TEMP_{new_name}"', f'"{new_name}"')
        content = content.replace(f"'TEMP_{new_name}'", f"'{new_name}'")

    with open(docs_path, "w", encoding="utf-8") as f:
        f.write(content)
    print("notebook_docs.py updated.")

print("Restructuring complete.")

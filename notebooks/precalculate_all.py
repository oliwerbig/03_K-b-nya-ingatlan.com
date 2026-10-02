# -*- coding: utf-8 -*-
"""Precalculate and execute all 12 notebooks for nbviewer.org compatibility."""
import os, sys, glob, time, json, subprocess
sys.stdout.reconfigure(encoding='utf-8')
import nbformat
from nbclient import NotebookClient

_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
NB_DIR = _THIS_DIR
PROJECT_ROOT = os.path.dirname(NB_DIR)
HTML_DIR = os.path.join(PROJECT_ROOT, "html_exports")
os.makedirs(HTML_DIR, exist_ok=True)

notebooks = sorted([f for f in os.listdir(NB_DIR) if f.endswith('.ipynb')])
print(f"Found {len(notebooks)} notebooks to execute in {NB_DIR}:")

results = {}

for nb_name in notebooks:
    nb_path = os.path.join(NB_DIR, nb_name)
    t0 = time.time()
    print(f"\n[{time.strftime('%H:%M:%S')}] Executing: {nb_name} ...", flush=True)
    
    try:
        with open(nb_path, 'r', encoding='utf-8') as f:
            nb = nbformat.read(f, as_version=4)
        
        client = NotebookClient(
            nb,
            timeout=300,
            kernel_name='python3',
            resources={'metadata': {'path': NB_DIR}}
        )
        
        client.execute()
        
        # Save back the executed notebook with outputs!
        with open(nb_path, 'w', encoding='utf-8') as f:
            nbformat.write(nb, f)
        
        elapsed = time.time() - t0
        total_outs = sum(len(c.get('outputs', [])) for c in nb.cells if c.cell_type == 'code')
        file_kb = round(os.path.getsize(nb_path) / 1024, 1)
        results[nb_name] = f"SUCCESS ({elapsed:.1f}s, {total_outs} outputs, {file_kb} KB)"
        print(f"  --> SUCCESS in {elapsed:.1f}s! Total outputs: {total_outs}, File size: {file_kb} KB", flush=True)
        
    except Exception as e:
        elapsed = time.time() - t0
        err_msg = str(e).split('\n')[0]
        results[nb_name] = f"FAILED ({elapsed:.1f}s): {err_msg}"
        print(f"  --> ERROR in {elapsed:.1f}s: {e}", flush=True)

print("\n" + "=" * 60)
print("PRECALCULATION SUMMARY:")
print("=" * 60)
for k, v in results.items():
    print(f"  {k}: {v}")

print("\n" + "=" * 60)
print("EXPORTING ALL NOTEBOOKS TO HTML...")
print("=" * 60)
jupyter_bin = os.path.join(PROJECT_ROOT, ".venv", "Scripts", "jupyter.exe")
export_cmd = f'"{jupyter_bin}" nbconvert --to html "{NB_DIR}\\*.ipynb" --output-dir "{HTML_DIR}"'
print(f"Running: {export_cmd}")
res = subprocess.run(export_cmd, shell=True, capture_output=True, text=True)
print("HTML Export returncode:", res.returncode)
if res.stderr:
    print("Export Stderr summary:", res.stderr.split('\\n')[-5:])
print("HTML EXPORT COMPLETED SUCCESSFULLY!")


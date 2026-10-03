import os
import glob
import subprocess
import sys
import time

def main():
    notebooks = sorted(glob.glob("notebooks/*.ipynb"))
    print(f"Found {len(notebooks)} notebooks to execute and export.")
    
    python_exe = sys.executable
    docs_dir = "docs"
    os.makedirs(docs_dir, exist_ok=True)
    
    start_total = time.time()
    
    for i, nb in enumerate(notebooks):
        nb_name = os.path.basename(nb)
        print(f"\n[{i+1}/{len(notebooks)}] Executing {nb_name}...")
        t0 = time.time()
        
        # 1. Execute notebook in place
        cmd_exec = [
            python_exe, "-m", "nbconvert",
            "--to", "notebook",
            "--execute",
            "--inplace",
            "--ExecutePreprocessor.timeout=300",
            nb
        ]
        res = subprocess.run(cmd_exec, capture_output=True, text=True)
        if res.returncode != 0:
            print(f"ERROR executing {nb_name}:")
            print(res.stderr[:500])
        else:
            print(f"Executed {nb_name} in {time.time()-t0:.1f}s")
            
        # 2. Export executed notebook to HTML into docs/
        html_out = os.path.join(docs_dir, nb_name.replace(".ipynb", ".html"))
        cmd_html = [
            python_exe, "-m", "nbconvert",
            "--to", "html",
            nb,
            "--output", os.path.basename(html_out),
            "--output-dir", docs_dir
        ]
        res_html = subprocess.run(cmd_html, capture_output=True, text=True)
        if res_html.returncode == 0:
            print(f"Exported to {html_out}")
        else:
            print(f"ERROR exporting {html_out}: {res_html.stderr[:300]}")
            
    print(f"\n==========================================")
    print(f"ALL DONE in {time.time()-start_total:.1f}s!")
    print(f"==========================================")

if __name__ == "__main__":
    main()

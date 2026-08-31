import subprocess
import sys
import os

def is_frozen():
    return getattr(sys, 'frozen', False)

def main():
    if not is_frozen():
        base_dir = os.path.dirname(os.path.abspath(__file__))
        aggiorna_script = os.path.join(base_dir, "aggiornaCampionato.py")
        app_script = os.path.join(base_dir, "app.py")
        subprocess.run([sys.executable, aggiorna_script])
        subprocess.run([sys.executable, app_script])
    else:
        base_dir = os.path.dirname(sys.executable)
        aggiorna_exe = os.path.join(base_dir, "aggiornaCampionato.exe")
        app_exe = os.path.join(base_dir, "app.exe")
        
        if os.path.exists(aggiorna_exe):
            subprocess.run([aggiorna_exe])
        if os.path.exists(app_exe):
            subprocess.run([app_exe])

if __name__ == "__main__":
    main()
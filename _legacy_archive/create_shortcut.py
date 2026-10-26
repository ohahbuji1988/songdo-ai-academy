import os
import sys

desktop = os.path.join(os.environ["USERPROFILE"], "Desktop")
shortcut_path = os.path.join(desktop, "Curriculum Creator.lnk")
target = sys.executable.replace("python.exe", "pythonw.exe")
target_script = r"C:\Users\Brain\devils-advocate\curriculum_creator.py"
work_dir = r"C:\Users\Brain\devils-advocate"

ps_script = f"""
$WshShell = New-Object -ComObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut('{shortcut_path}')
$Shortcut.TargetPath = '{target}'
$Shortcut.Arguments = '"{target_script}"'
$Shortcut.WorkingDirectory = '{work_dir}'
$Shortcut.IconLocation = 'shell32.dll,43'
$Shortcut.Save()
"""

ps_file = os.path.join(work_dir, "make_lnk.ps1")
with open(ps_file, "w", encoding="utf-8") as f:
    f.write(ps_script)

import subprocess
res = subprocess.run(["powershell", "-ExecutionPolicy", "Bypass", "-File", ps_file], capture_output=True, text=True)
print("Return code:", res.returncode)
print("Stdout:", res.stdout)
print("Stderr:", res.stderr)
if os.path.exists(shortcut_path):
    print("SUCCESS: Shortcut exists at", shortcut_path)

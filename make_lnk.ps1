
$WshShell = New-Object -ComObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut('C:\Users\Brain\Desktop\Curriculum Creator.lnk')
$Shortcut.TargetPath = 'C:\Users\Brain\AppData\Local\Python\pythoncore-3.14-64\pythonw.exe'
$Shortcut.Arguments = '"C:\Users\Brain\devils-advocate\curriculum_creator.py"'
$Shortcut.WorkingDirectory = 'C:\Users\Brain\devils-advocate'
$Shortcut.IconLocation = 'shell32.dll,43'
$Shortcut.Save()

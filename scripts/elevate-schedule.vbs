Set objShell = CreateObject("Shell.Application")
objShell.ShellExecute "powershell.exe", "-ExecutionPolicy Bypass -File ""C:\Users\asus\Documents\Obsidian Vault\scripts\schedule-sync.ps1""", "", "runas", 1

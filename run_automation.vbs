Set WshShell = CreateObject("WScript.Shell")
WshShell.Run chr(34) & "run_automation.bat" & Chr(34), 0
Set WshShell = Nothing
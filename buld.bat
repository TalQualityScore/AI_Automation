pyinstaller --noconfirm --onefile --windowed --name "AI_Automation_Suite" --add-data "Assets;Assets" --add-data "azure.tcl;." --add-data ".env;." app/src/__main__.py
pause

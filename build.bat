@echo off
pyinstaller --onefile --name Gaello --icon=icon.ico --splash=splash.png ^
    --add-data "assets/*;assets" ^
    --add-data "node_modules/*;node_modules" ^
    --add-data "server/*;server" ^
    --add-data "views/*;views" ^
    --add-data "models/api/*;models/api" ^
    --add-data "app;." ^
    --add-data ".env;." ^
    --add-data "package.json;." ^
    --collect-submodules "models" ^
    --collect-submodules "databases" ^
    --collect-submodules "app"  ^
    --collect-submodules "utils"  ^
    --collect-submodules "client"   ^
    --console ^
    src/main.py
pause


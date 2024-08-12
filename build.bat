@echo off
pyinstaller --onefile --name Gaello --icon=icon.ico --splash=splash.png ^
    --add-data "assets/UI/*.ui;assets/UI" ^
    --add-data "assets/fonts/Exo_2/static/*;assets/fonts/Exo_2/static" ^
    --add-data "assets/fonts/Montserrat/static/*;assets/fonts/Montserrat/static" ^
    --add-data "assets/fonts/Quicksand/static/*;assets/fonts/Quicksand/static" ^
    --add-data "assets/fonts/Roboto_Mono/static/*;assets/fonts/Roboto_Mono/static" ^
    --add-data "assets/images/*;assets/images" ^
    --add-data "assets/icons/*;assets/icons" ^
    --add-data "assets/spinners/*;assets/spinners" ^
    --add-data "assets/videos/*;assets/videos" ^
    --add-data "assets/html/*;assets/html" ^
    --add-data "assets/logo/*;assets/logo" ^
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


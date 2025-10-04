@echo off
REM ============================================================
REM Build script for DynamicSpawnTemplateManager.exe
REM ============================================================

echo Building DynamicSpawnTemplateManager executable...
echo.

REM Check if PyInstaller is installed
python -c "import PyInstaller" 2>nul
if %errorlevel% neq 0 (
    echo PyInstaller not found. Installing...
    pip install pyinstaller
    echo.
)

REM Build the executable using custom spec file (preserves image assets)
pyinstaller DynamicSpawnTemplateManager.spec

echo.
echo Build complete!
echo Executable location: dist\DynamicSpawnTemplateManager.exe
echo.
echo IMPORTANT: Copy aircraft_inventory.lua to the same folder as the .exe file
echo.
pause

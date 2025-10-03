# DynamicSpawnTemplateManager - Build Instructions

## Prerequisites
- Python 3.11 or higher
- PyInstaller (`pip install pyinstaller`)

## Quick Build (Recommended)

Simply run:
```batch
build_executable.bat
```

This will:
1. Check if PyInstaller is installed (and install it if needed)
2. Build the executable with all necessary files
3. Create `dist\DynamicSpawnTemplateManager.exe`

## Manual Build

If you prefer to build manually:

```batch
pip install pyinstaller
pyinstaller DynamicSpawnTemplateManager.spec
```

## What Gets Included

The executable will bundle:
- All Python code
- tkinter GUI libraries
- The `aircraft_inventory.lua` file (embedded in the .exe)

## Distribution

After building, you can distribute:
1. `DynamicSpawnTemplateManager.exe` (from the `dist` folder)
2. `aircraft_inventory.lua` (must be in the same folder as the .exe)

**IMPORTANT**: The `aircraft_inventory.lua` file must be in the same directory as the executable for the program to work correctly.

## File Structure for End Users

```
YourFolder/
├── DynamicSpawnTemplateManager.exe
└── aircraft_inventory.lua
```

## Testing the Executable

After building:
1. Navigate to the `dist` folder
2. Copy `aircraft_inventory.lua` to the `dist` folder (next to the .exe)
3. Run `DynamicSpawnTemplateManager.exe`

## Troubleshooting

**"Missing aircraft_inventory.lua" error:**
- Make sure `aircraft_inventory.lua` is in the same folder as the .exe

**Executable doesn't start:**
- Try building with console mode to see errors:
  - Edit `DynamicSpawnTemplateManager.spec` and change `console=False` to `console=True`
  - Rebuild: `pyinstaller DynamicSpawnTemplateManager.spec`

**GUI doesn't appear:**
- Check if you have tkinter installed: `python -m tkinter`
- Rebuild the executable

## Build Output

After successful build, you'll find:
- `dist/DynamicSpawnTemplateManager.exe` - The final executable
- `build/` - Temporary build files (can be deleted)
- `DynamicSpawnTemplateManager.spec` - Build configuration

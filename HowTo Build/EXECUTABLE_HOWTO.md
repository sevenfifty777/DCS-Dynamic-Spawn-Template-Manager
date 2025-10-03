# Creating Windows Executable for DynamicSpawnTemplateManager

## Quick Start - Easy Method

1. Open PowerShell or Command Prompt in this folder
2. Run: `build_executable.bat`
3. Wait for the build to complete
4. Your executable will be in the `dist` folder
5. Copy `aircraft_inventory.lua` to the `dist` folder (next to the .exe)

That's it! You can now distribute the `dist` folder with both files.

## Files Created

After building, you'll have:

- **build_executable.bat** - One-click build script (run this!)
- **DynamicSpawnTemplateManager.spec** - PyInstaller configuration
- **BUILD_README.md** - Detailed build instructions
- **dist/DynamicSpawnTemplateManager.exe** - Your final executable ✓

## Distribution Package

To share with others, create a folder with:
```
DynamicSpawnTemplateManager/
├── DynamicSpawnTemplateManager.exe
└── aircraft_inventory.lua
```

## Requirements

- Python 3.11+ (already installed if you've been running the script)
- PyInstaller (will be auto-installed by build_executable.bat)

## First Time Building?

If PyInstaller isn't installed, the bat file will install it automatically.
Just run `build_executable.bat` and follow the prompts.

## Testing the Executable

1. Go to the `dist` folder
2. Copy `aircraft_inventory.lua` into `dist`
3. Double-click `DynamicSpawnTemplateManager.exe`
4. The GUI should appear with the modern dark theme!

## Troubleshooting

**Problem**: "PyInstaller not found"
**Solution**: The bat file will install it automatically, or manually run: `pip install pyinstaller`

**Problem**: Executable doesn't start
**Solution**: Try building with console to see errors:
1. Edit `DynamicSpawnTemplateManager.spec`
2. Change `console=False` to `console=True`
3. Run `pyinstaller DynamicSpawnTemplateManager.spec`
4. Check console for error messages

**Problem**: "aircraft_inventory.lua not found"
**Solution**: Make sure the file is in the same folder as the .exe

## Advanced: Manual Build

If you prefer manual control:

```batch
# Install PyInstaller
pip install pyinstaller

# Build using spec file
pyinstaller DynamicSpawnTemplateManager.spec

# Or build with command line
pyinstaller --onefile --noconsole --name "DynamicSpawnTemplateManager" DynamicSpawnTemplateManager.py
```

## What Gets Bundled

The executable includes:
- ✓ All Python code
- ✓ tkinter GUI libraries  
- ✓ All dependencies (zipfile, re, os, etc.)
- ✓ Modern dark theme styling

**Note**: `aircraft_inventory.lua` must be external (same folder as .exe) for easy updates.

---

**Ready to build?** Just run: `build_executable.bat`

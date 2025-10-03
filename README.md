# DCS Dynamic Template Manager
**Note**: You need the `moose.lua` and `airbases_map.lua` files (should be included with this tool) for the CSV generation to work.

## ⚠️ Prerequisites Before Using the Tool

**IMPORTANT**: Before using this tool, you must prepare your mission properly:

### Aircraft Group Naming Requirements

1. **Open your mission** in DCS Mission Editor
2. **Create aircraft groups** with skill set to **"Player"** and check **"DynamicTemplate"** option
3. **Rename these groups** to end with `_DynTemp`
   - ✅ Good examples: 
     - `F-16C_Squadron_DynTemp`
     - `A-10C_CAS_DynTemp` 
     - `F/A-18C_Strike_DynTemp`
   - ❌ Bad examples:
     - `F-16C Squadron` (missing `_DynTemp`)
     - `Player_Aircraft` (missing `_DynTemp`)

4. **Save your mission** after renaming the groups

**Why this is needed**: The tool looks specifically for aircraft groups ending in `_DynTemp` to create dynamic templates. Without this naming, the tool won't find any templates to work with.

## 🚀 Quick Start Guide*A simple tool to manage dynamic aircraft spawning in DCS World missions**

## 📋 What This Tool Does

This tool helps you set up **dynamic aircraft spawning** in your DCS World missions. You will be able to configure each airbase with all different option and assign Dynamic Template for aircraft

## 📦 What You Need

1. **The executable files** (you should have received these):
   - `DynamicSpawnTemplateManager.exe` - The main program
   - `aircraft_inventory.lua` - Required data file

2. **Your DCS mission files**:
   - A `.miz` mission file you want to modify
   - A CSV file with airbase information (usually named something like `AirbasesList_[MapName].csv`)

## � How to Generate the Airbase CSV File

If you don't have the CSV file yet, you can generate it yourself:

1. **Create a new empty mission** in DCS Mission Editor with your desired map
2. **Add triggers**:
   - Create a new trigger with **MISSIONSTART** event
   - Add action: **DO SCRIPT FILE** → Select `moose.lua` file
   - Add another action: **DO SCRIPT FILE** → Select `airbases_map.lua` file
3. **Save and launch the mission** in DCS World
4. **Wait a few seconds** - the mission will generate the CSV file automatically
5. **Find the CSV file** at: `C:\Users\[YourUsername]\Saved Games\DCS\Logs\`
   - Look for a file named like `AirbasesList_[MapName].csv`

**Note**: You need the `moose.lua` and `airbases_map.lua` files (should be included with this tool) for the CSV generation to work.

## �🚀 Quick Start Guide

### Step 1: Prepare Your Files

1. **Create a folder** somewhere on your computer (e.g., `C:\DCS_Templates\`)
2. **Copy these files** to that folder:
   - `DynamicSpawnTemplateManager.exe`
   - `aircraft_inventory.lua`
   - Your `.miz` mission file
   - Your airbases CSV file

### Step 2: Launch the Program

1. **Double-click** on `DynamicSpawnTemplateManager.exe`
2. The program window will open with a modern dark interface

### Step 3: Configure Dynamic Spawning (STEP 1)

The program works in **2 steps**. First, you'll configure which airbases can spawn aircraft with all Dynamic spawn option:

1. **Click "📁 Load Airbases CSV"**
   - Select your CSV file corresponding to the mission map (e.g., `AirbasesList_Caucasus.csv`)

2. **Click "📦 Load MIZ File"**
   - Select your `.miz` mission file
   - The airbases will appear in the right panel

3. **Configure each airbase**:
   - **Select checkbox**: Check airbases where you want dynamic spawning
   - **Coalition**: Choose BLUE, RED, or NEUTRAL for each airbase
   - **DynSpawn**: ✅ Check this to enable dynamic spawning
   - **HotStart**: ✅ Check if you want aircraft to start with engines running
   - **DynCargo**: ✅ Check for dynamic cargo operations
   - **∞Munitions**: ✅ Usually leave checked (unlimited weapons)
   - **∞Aircraft**: ✅ Usually leave checked (unlimited aircraft)
   - **∞Fuel**: ✅ Usually leave checked (unlimited fuel)

4. **Click "✓ Apply Options & Save"**
   - This saves a new file: `[YourMission]_Step1_Options.miz`
   - Choose **YES** when asked if you want to continue to Step 2

### Step 4: Link Aircraft Templates (STEP 2)

Now you'll choose which aircraft types can will be used as a Dynamioc Template at each airbase:

1. The program will reload and show available aircraft templates
2. **For each airbase and aircraft type**:
   - Use the dropdown menus to select which template to use
   - Choose "None (Disabled)" if you don't want that aircraft type at that airbase

3. **Click "Apply Templates & Save Final"**
   - This creates your final mission: `[YourMission]_Final.miz`

### **Notes:** If you stop the process before generationg the final mission, clean all temp folders and files created if any

### Step 5: Use Your Mission

1. **Load the final mission** (`[YourMission]_Final.miz`) in DCS World
2. **Enjoy dynamic aircraft spawning** during your mission!

## 📚 Detailed Explanations

### Coalition Colors

- **🔵 BLUE**: NATO/Allied forces
- **🔴 RED**: OPFOR/Enemy forces  
- **⚪ NEUTRAL**: Civilian or neutral forces

### DynSpawn Options Explained

| Option | What it does |
|--------|-------------|
| **DynSpawn** | Enables dynamic aircraft spawning at this airbase |
| **HotStart** | Aircraft spawn with engines already running (ready to takeoff) |
| **DynCargo** | Enables dynamic cargo/transport operations |
| **∞Munitions** | Unlimited weapons (aircraft won't run out of ammo) |
| **∞Aircraft** | Unlimited aircraft (new ones keep spawning) |
| **∞Fuel** | Unlimited fuel (aircraft won't need to refuel) |

## 🔧 Troubleshooting

### Program Won't Start
- **Check**: Make sure `aircraft_inventory.lua` is in the same folder as the `.exe`
- **Try**: Right-click the `.exe` → "Run as administrator"

### "No CSV file selected" Error
- **Check**: Make sure you're selecting a `.csv` file, not a `.txt` or other file
- **Try**: Look for files named like `AirbasesList_[MapName].csv`

### "Failed to load MIZ file" Error
- **Check**: Make sure you're selecting a `.miz` file from DCS World
- **Check**: The `.miz` file isn't corrupted or locked by another program

### No Templates Found
- **Cause**: Your mission doesn't have any aircraft groups with names ending in `_DynTemp`
- **Solution**: In DCS Mission Editor, rename your aircraft groups to end with `_DynTemp` (e.g., `F-16C_Squadron_DynTemp`)

### Step 2 Shows No Airbases
- **Cause**: No airbases were configured with DynSpawn enabled in Step 1
- **Solution**: Go back to Step 1 and make sure to check the "DynSpawn" option for airbases you want

## 📁 File Organization

After using the tool, you'll have these files:

```
Your Folder/
├── DynamicSpawnTemplateManager.exe    (The program)
├── aircraft_inventory.lua             (Required data)
├── YourMission.miz                    (Original mission)
├── YourMission_Step1_Options.miz      (After Step 1 - can be deleted if not done automatically)
└── YourMission_Final.miz              (Final mission - use this one!)
```

## ✅ Tips for Success

1. **Start simple**: Try with just 2-3 airbases first to learn how it works
2. **Backup originals**: Keep a copy of your original `.miz` file
3. **Test in DCS**: Always test your final mission in DCS World
4. **Naming matters**: Aircraft groups must end with `_DynTemp` in the Mission Editor
5. **One aircraft type per template**: Each template should contain only one type of aircraft
6. **One Template per aircraft per base**: multiple template can be created for same aircraft but only one assign to each airbase

## 📞 Need Help?

If you're still having trouble:

1. **Check your aircraft naming**: Groups must end with `_DynTemp`
2. **Try a different mission**: Some missions may have complex structures
3. **Start fresh**: Close the program, clean all temp files and folder that could have been created, delete previous final version if you want to start over and start over with Step 1

---

**A la chasse!!!**

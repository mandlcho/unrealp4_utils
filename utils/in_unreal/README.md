# P4 Context Menu for Unreal Engine

**🎮 NO BUILD REQUIRED!** Pure Python solution - works immediately!

## What You Get

Right-click menu in Unreal's Content Browser:
- **📁 Show in P4** - Opens file in P4V
- **📜 View History** - Opens P4V history to diff revisions

## How to Diff Blueprints Visually

```
Unreal Content Browser
    ↓
Right-click BP_Player.uasset
    ↓
"📜 View History"
    ↓
P4V opens with file selected
    ↓
History tab → Select 2 revisions → Right-click → Diff
    ↓
🎉 Visual blueprint diff opens!
```

## Quick Setup (2 minutes)

### 1. Run Setup Tool

Double-click:
```
utils/in_unreal/RunP4Setup.bat
```

### 2. Install

1. If project not auto-detected, click **Browse** and select your project folder
2. Click **🚀 Install Context Menu**
3. **Restart Unreal Engine**

### 3. Done!

Right-click any `.uasset` in Content Browser and choose:
- **Show in P4** - Opens P4V
- **View History** - Opens P4V history

## Requirements

- ✅ Unreal Engine 5.x
- ✅ Python Editor Script Plugin (usually enabled by default)
- ✅ Perforce (P4V) installed

**❌ NO C++ BUILDING REQUIRED!**

## How It Works

This is a **pure Python** solution:
- No C++ plugins to compile
- No engine rebuilds
- Just Python scripts in `Content/Python/`

The menu uses `p4vc` command (comes with P4V) to open files.

## Troubleshooting

### Menu doesn't appear
- Make sure Python Editor Script Plugin is enabled:
  - Edit → Plugins → Search "Python" → Enable "Python Editor Script Plugin"
- Restart Unreal Engine

### "Show in P4" doesn't open P4V
- Make sure P4V is installed and in your system PATH
- Try running `p4vc` from command prompt to verify

### Can't diff in P4V
- Make sure file is checked into Perforce (has revision history)
- In P4V History tab, select **2 different revisions** (not working copy)
- Right-click one of the selected revisions → **Diff** (not Diff Against)

## Files Installed

In your project:
- `Content/Python/p4_menu.py` - The menu logic
- `Content/Python/init_unreal.py` - Auto-loads the menu
- `Config/DefaultEngine.ini` - Configures Python startup

**Nothing else! No plugins, no building!**

---

**Want P4V to open diffs in Unreal's native viewer?**

For visual blueprint diffs in P4V, also run:
```
utils/in_perforce/RunP4UassetDiffSetup.bat
```

(This one requires building a tiny plugin, but gives you the full visual diff experience)

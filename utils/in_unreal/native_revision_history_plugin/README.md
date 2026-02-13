# Native Revision History Plugin

This is the strongest path to get a reliable right-click revision-history entry in Unreal.

## What it does

- Adds `Open Native Revision History` to `Content Browser -> Asset right-click -> SourceControl`
- Calls Unreal's native Source Control history UI directly (C++), not console command fallbacks

## Install

1. Copy `UAssetRevisionHistory` folder into your project `Plugins/` directory.
2. Regenerate project files and build editor.
3. Ensure Source Control is connected to Perforce in Unreal.
4. Restart editor.

Then right-click a `.uasset` and choose `Open Native Revision History`.

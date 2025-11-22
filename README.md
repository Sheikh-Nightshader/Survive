# Survive a Doom-Style Terminal Raycaster (Python / Termux)

Survive is a small first-person raycasting game written in Python.  
It runs directly in the terminal (Android-Termux, Linux, macOS). The game draws a classic Doom-like 3D view using ASCII characters.

You can walk around, shoot monsters, pick up ammo/health, and explore a generated map.

## Features
- ASCII 3D raycasting engine  
- Random map generation  
- Monsters that chase you  
- Ammo + health pickups  
- Shooting system  
- Runs smoothly inside Termux  
- Uses only Python + curses

## Requirements
Linux/Termux already includes curses.

## Controls
```
W – Move forward
S – Move backward
A – Turn left
D – Turn right
Space – Shoot
G - Toggle Gun visibility (1.4+)
1-4 - Cycle Weapons (1.4+)
Q – Quit
```

## Config / Tweaks
You can edit these inside the script:

| Variable | Meaning |
|----------|---------|
| `FOV` | Field of view |
| `DEPTH` | View distance |
| `MAP_WIDTH`, `MAP_HEIGHT` | Map size |
| `MAX_MONSTERS_BASE` | Monster count |
| `SCREEN_WIDTH`, `SCREEN_HEIGHT` | Terminal output size |

Increasing `DEPTH` makes walls visible from farther away.

## Warning
This is a simple learning project.  
Not optimized and may use more CPU on bigger maps or higher view distance.  
Use at your own risk.

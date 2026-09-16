# FS25 Dev Tools

Small development/reverse-engineering toolkit for Farming Simulator 25.

## Current module: Object Inspector

The first proof of concept is intentionally small. Its job is to answer one question reliably:

> What physics/collision node is under the player's crosshair, and how is it configured?

This is primarily intended for comparing FS25 pedestrians, traffic vehicles and other world objects while researching collision behaviour.

## Controls

The mod title is **Dev Tools**, so FS25 should group all of its actions under a dedicated **Dev Tools** section in the Controls menu.

Default bindings:

- **F8** — Inspect object under the crosshair
- **F9** — Repeat the last successful object dump

Both actions are normal FS25 input actions and can be rebound in the Controls menu.

## What an inspection writes to `log.txt`

- hit node ID and node name
- raycast hit position and distance
- surface normal
- shape/sub-shape identifiers
- rigid body type
- collision enabled state
- trigger state
- whether the node is added to physics
- compound/compound-child state
- collision group and mask (decimal + hex)
- `g_currentMission:getNodeObject(...)` association when available
- parent-node chain (up to 8 parents)

A short in-game notification confirms whether the dump succeeded or whether the raycast hit nothing.

## Test plan

1. Copy the `FS25_DevTools` folder into the FS25 `mods` directory (an unpacked folder is fine for local development/testing).
2. Enable **Dev Tools** for a single-player save.
3. Open the Controls menu and verify that a **Dev Tools** section exists and that the two actions can be rebound.
4. Look directly at a traffic vehicle and press **F8**.
5. Look directly at a pedestrian and press **F8**.
6. Compare the two `[DevTools:ObjectInspector] OBJECT DUMP` blocks in `log.txt`.

### Important interpretation

If a pedestrian produces **no raycast hit at all**, that result is useful: it strongly suggests the visible pedestrian has no rigid-body shape in the collision mask seen by the raycast. The next step would then be inspecting the pedestrian system itself or using an overlap/custom detection approach.

If both objects produce hits, compare their rigid-body type, collision group and collision mask first.

## Scope of v0.1.0.0

This is a diagnostic PoC, not a finished user mod. It intentionally does **not**:

- modify collision masks
- change pedestrian behaviour
- spawn decals/effects
- write or modify `game.xml`
- add a custom settings tab yet

The settings-tab idea is kept for later, when multiple Agriculture Science / Dev Tools modules actually need settings.

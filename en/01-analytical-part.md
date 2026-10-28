# 1. Analytical Part

## 1.1. Current State

### How the Task Is Solved Today (AS-IS)

There is no ready-made "capture a place — get a level" path. People assemble it themselves from several tools. The process is shown in the activity diagram (Image A.2.1).

The steps, participants and losses of the current process are given in Table 1.1.

Table 1.1. Steps of the current process and losses

| Step | Who | Tool | Where time and data are lost |
|------|-----|------|------------------------------|
| 1. Capture the place | Level author | Phone scanner: Polycam, Scaniverse, KIRI Engine | The app does not say whether the capture is suitable for a game level |
| 2. Export the model | Level author | OBJ, FBX or GLB export; some formats only on a paid plan [@polycamReview] | A dense model with debris along the edges and no game budget |
| 3. Clean up and simplify | Level author or 3D artist | Blender | Manual work that needs skills. Scale is easily lost on export |
| 4. Build a collision mesh | Same | Blender or engine | A separate simplified mesh made by hand. A splat does not support the character, so the collision mesh is built separately anyway [@polycam] |
| 5. Import into the engine and walk | Developer | Godot, Unity, Unreal | Walkability is visible only here. Errors from step 1 or 4 are found at the very end |
| 6. Redo | Everyone | All tools | The same result cannot be reproduced: every step is manual |

**Who is involved.** Most often a single person: an indie developer, a level designer, a model maker or a student. In a studio, steps 3–4 may be done by a 3D artist, which adds file hand-offs between people.

**Where time is lost.** Steps 3–4: manual cleanup, simplification and collision mesh building. Steps 5–6: a capture defect is found last, and the cycle starts again.

**Where data is lost.** The metric scale measured by the sensor is lost during export and manual rescaling. Information about how the capture was taken (camera path, depth) does not reach the model. Afterwards it is impossible to explain why the level came out bad.

### Illustrative Example

The persona Anya (section 2.2) takes part in a 48-hour game jam. The theme is "small world", and she wants to build a level from her desk with books and a mug. She scans the desk in Polycam and gets a good-looking model of several hundred thousand triangles. Godot imports it, but the character falls through: the model has no separate collision mesh, and the desk edges are ragged. Anya opens Blender, cleans the edges by hand, simplifies the model and builds an invisible collision mesh from cubes. On export the scale is lost, and the character ends up the size of the mug. After the second attempt it turns out that one book was missing from the capture: Anya moved too fast. The level takes half a day of the 48-hour jam, and in the end she replaces the desk with cubes.

The example shows three losses: time spent on manual fixing, a capture defect found late, and lost scale. These are what the product addresses.

### How It Will Be (TO-BE)

A person walks around the area with a phone for 10–30 seconds. The app checks the recording at once and either sends it to the server or asks for a retake with a clear reason. The server builds the map itself: a visual mesh, a separate lightweight collision mesh and a report, keeping the sensor scale. The person walks the map in the browser and downloads the package into the engine. Manual steps 3–4 and the late check in step 5 disappear (Image A.2.2).

## 1.2. Review of Sources

The review uses 33 sources, 10 of them scientific. The sources fall into four groups: reconstruction methods, scene representation, standards and regulations, market and analogs.

**Reconstruction methods.** The classic path from depth to surface is described by Curless and Levoy [@curless1996] and in KinectFusion [@newcombe2011]: depth maps with a known camera position are accumulated in a volumetric grid, from which the surface is extracted with marching cubes [@lorensen1987]. The method is robust to noise in a single frame but depends entirely on pose accuracy: trajectory errors smear the surface. Two product decisions follow. Camera poses are mandatory, and without them the build is rejected. The capture area is small, so the accumulated trajectory error does not have time to grow. Quadric error simplification [@garland1997] reduces a mesh to a set number of triangles with controlled loss of shape — the basis of the strict visual mesh and collision mesh budgets.

**Sensor accuracy.** An evaluation of the iPhone 12 Pro LiDAR [@luetzenburg2021] shows centimetre accuracy on small objects captured from up to a few metres. This is consistent with choosing a small zone of about 80 × 80 cm and capturing from a low height. Depth Anything V2 [@yang2024] estimates depth from a single frame with a neural network; this is an estimate, not a sensor measurement, so in the product it is only a disabled fallback mode.

**Scene representation.** Gaussian splatting [@kerbl2023] brought photorealistic real-time scene viewing, and scanners adopted it quickly [@scaniverse; @polycam; @luma]. But a splat has no surface a character can walk on: even Polycam's Unreal guide takes the character's collision from a separate mesh [@polycam]. Video2Game [@xia2024] is the work closest to the product: video turns into a scene with collision for the character that runs in a browser. However, it requires training a neural representation for each scene and remains a research pipeline rather than a service. Conclusion for the product: a beautiful image and a game-ready collision mesh are different tasks, and the product solves the second.

**Standards and regulations.** glTF 2.0 [@gltf] sets metres as the unit and Y as the up axis and is read by browsers and engines, which makes the package portable without conversion. The GDPR [@gdpr] requires a legal basis, data minimisation and the right to erasure: a capture of a room may accidentally include people. WCAG 2.1 [@wcag] sets a measurable accessibility level for the web client. The requirements elicitation techniques come from BABOK v3 [@babok].

What each group of sources implies for the requirements in Chapter 2 is shown in Table 1.2.

Table 1.2. Conclusions from the sources for the requirements

| Sources | What follows | Where in the requirements |
|---------|--------------|---------------------------|
| Depth fusion [@newcombe2011; @curless1996], Open3D [@zhou2018] | Depth maps with known poses fuse into a surface; without poses there is no result. Ready implementations are open (MIT) | Poses are mandatory, otherwise rejection: US-3.2; licences: 2.8 |
| Marching cubes [@lorensen1987], quadric simplification [@garland1997] | The surface is built automatically, and the triangle count can be strictly limited | Map budget: KPI-4, US-3.3 |
| iPhone 12 Pro LiDAR [@luetzenburg2021], devices [@lidar; @lidarIphone] | Centimetre accuracy on a small area; depth is available only on Apple Pro devices | 80 × 80 cm zone, iOS platform: 2.3 |
| Gaussian splatting [@kerbl2023], splats in engines [@polycam; @luma] | A splat has no physical surface; the collision mesh is added as a separate model | Separate collision mesh: US-5.1; splats out of scope |
| Depth Anything V2 [@yang2024] | Single-frame depth is a neural estimate, not a measurement | Build without LiDAR is a disabled mode: 2.3 |
| Video2Game [@xia2024] | Video becomes an interactive scene with collision, at the cost of per-scene training; this is research, not a product | Walk check in the browser: US-4.1; no per-scene network training |
| glTF 2.0 [@gltf], RoomPlan [@roomplan] | An open format with metres and Y up; RoomPlan builds a room plan, not the surface of an area | GLB package and manifest: US-5.2 |
| GDPR [@gdpr], WCAG 2.1 [@wcag], BABOK [@babok] | Legal basis, minimisation, erasure; AA accessibility; elicitation techniques | 2.8, NFR-9; methods in the Introduction |
| Market [@fortnite2024; @roblox10k; @steam2025], analogs [@marble; @scaniverse; @polycam; @kiri; @realityscan; @luma] | There are many game creators and more every year; scanners deliver a model, not a level | Segments: 2.2; analogs: 1.3 |

**Conclusion.** Surface reconstruction and simplification technologies are mature [@newcombe2011; @curless1996; @lorensen1987; @garland1997; @zhou2018]. The phone sensor is accurate on a small area [@luetzenburg2021]. The novelty of the product lies not in the algorithms but in joining them into a verifiable path from capture to a walkable level with an honest rejection.

## 1.3. Analysis of Analogs

Nine solutions were reviewed. Commercial: Polycam [@polycam] (subscription of about $27 per month [@polycamReview]), Scaniverse [@scaniverse] (Niantic Spatial), KIRI Engine [@kiri] ($50–80 per year), RealityScan [@realityscan] (Epic Games, export via Sketchfab to Unreal), Luma [@luma] (splats, Unreal plugin), World Labs Marble [@marble] (generates a 3D world from text, photos or video and exports a collider mesh as GLB), and the Apple RoomPlan API [@roomplan], which builds a room plan from walls and furniture. Research and open: Video2Game [@xia2024] and the manual path with COLMAP [@schonberger2016], Open3D [@zhou2018] and Blender.

**Polycam** is a widely used scanner with LiDAR and photogrammetry. Its strengths are model quality and a wide choice of formats. Turning its output into a level takes manual work: there is no collision mesh, the model is dense, and some formats require a paid plan [@polycamReview].

**Scaniverse** is a free Niantic Spatial scanner with meshes and splats. In 2026 it added a package for robot simulators in which the mesh is derived from the splat [@scaniverse; @scaniverseUsdz]. This is a step towards a simulation-ready scene, but not towards a lightweight game level.

**KIRI Engine** targets artists: retopology, PBR materials, export to Blender and Unreal [@kiri]. The result is an asset for further work, not a walkable area.

**RealityScan** by Epic Games turns photos of an object into a 3D model and takes it into the Epic ecosystem: Sketchfab and Unreal [@realityscan].

**Luma** produces photorealistic splats and an Unreal plugin [@luma]. A splat has no surface for a character [@kerbl2023], and the vendor does not claim metric scale.

**World Labs Marble** is closest in output: it exports a separate collider mesh as GLB [@marble]. But the world is generated by a model rather than measured, so its scale is not real; the vendor does not claim a walkability check or rejection of an unsuitable capture [@marble].

**Apple RoomPlan** builds a room plan from walls, doors and furniture [@roomplan]. This is a diagram of a room, not the surface of a desk or a model.

**Video2Game** shows that the "video → walkable scene" path is possible [@xia2024], but it requires training for each scene and is not a product.

**The manual path** with COLMAP [@schonberger2016], Open3D [@zhou2018] and Blender gives full control but requires skills and time and cannot be repeated with a single command.

### Comparison by Criteria

The criteria are derived from the losses of the current process (Table 1.1): each step where time or data is lost has one criterion, and the last one shows where the analogs are stronger.

- **Rejection** (step 1) — rejection with a reason for a capture unsuitable for a level.
- **Budget** (steps 2–3) — the model fits a game budget without manual simplification.
- **Metres** (step 3) — the result keeps the real scale.
- **Collision** (step 4) — a separate lightweight mesh the character walks on.
- **Walk** (step 5) — walkability can be checked before import into the engine.
- **Repeat** (step 6) — processing the same capture again gives the same result.
- **Image** — high image and texture quality.

The analogs are assessed from public descriptions and documentation [@polycam; @scaniverse; @kiri; @realityscan; @luma; @marble; @xia2024]. The NVC Maps column shows target values: the product is under development. The results are summarised in Table 1.3.

<!-- landscape -->

Table 1.3. Comparison of analogs by criteria

| Criterion | Polycam | Scaniverse | KIRI Engine | RealityScan | Luma | World Labs Marble | Video2Game | NVC Maps (target, planned) |
|-----------|---------|------------|-------------|-------------|------|-------------------|------------|----------------------------|
| Rejection (step 1) | — | — | — | — | — | — | — | ✓ |
| Budget (steps 2–3) | — | — | ~ | — | — | — | — | ✓ |
| Metres (step 3) | ✓ | ✓ | ✓ | — | — | ✕ | — | ✓ |
| Collision (step 4) | ✕ | ~ | — | — | ✕ | ✓ | ✓ | ✓ |
| Walk (step 5) | — | — | — | — | — | ~ | ✓ | ✓ |
| Repeat (step 6) | — | — | — | — | — | — | — | ✓ |
| Image | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✕ |

Legend: ✓ — yes; ~ — partly; ✕ — no; — — not claimed by the vendor. Notes: Scaniverse exports a mesh for robot simulators [@scaniverseUsdz]; KIRI Engine performs retopology [@kiri]; World Labs Marble has a physics example in the browser [@marble]; for Polycam and Luma the character's collision is added as a separate mesh [@polycam; @kerbl2023].

<!-- /landscape -->

### What Is Missing

1. **A collision mesh in metres.** Scanners with LiDAR keep the scale but do not claim a separate collision mesh, and in Polycam it is added by hand [@polycam]. World Labs Marble exports a collider mesh, but its world is generated by a model, and its scale is not real.
2. **A walkability check before the engine.** Only the research project Video2Game claims it, and World Labs Marble partly; scanners do not claim such a check.
3. **An honest rejection.** No solution claims rejecting a capture unsuitable for a level with a reason.
4. **Repeatability and a game budget.** No solution claims repeatable results and automatic fitting into a game budget.

**Where the analogs are stronger.** Image quality, textures, scene size (room, street), Android support. The product deliberately gives way here: its goal is a result that is fit for a game.

## 1.4. Chapter Conclusions

The identified problems and what the new solution must be able to do are summarised in Table 1.4.

Table 1.4. Problems and their links to epics and KPIs

| No. | Problem | What the new solution must do | Epic | KPI |
|-----|---------|-------------------------------|------|-----|
| P1 | A bad capture looks like a good one; the defect is found in the engine | Check the recording on the phone and reject it with a reason | E1, E3 | KPI-3 |
| P2 | The collision mesh and simplification are done by hand | Build the visual mesh and a lightweight collision mesh automatically | E3, E5 | KPI-1, KPI-4 |
| P3 | Walkability is visible only in the engine | Let the user walk the map in the browser | E4 | KPI-1, KPI-2 |
| P4 | The sensor scale is lost along the way | Keep metres and record units and axes in the manifest | E5 | KPI-1 |
| P5 | The path from capture to level is long and not repeatable | Accept the capture, build the map on the server, show the status | E2, E3 | KPI-2 |
| P6 | Without a LiDAR phone the product cannot be checked | Open the reference jobs via a test link | E6 | KPI-1, KPI-3 |

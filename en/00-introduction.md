# Introduction

## Relevance and Problem

**Who has the problem.** People who build small games and prototypes without a 3D artist: indie developers and game jam participants, level designers at small studios, makers of tabletop models and dioramas, game development teachers and students. More than 18,000 games were released on Steam in 2025 [@steam2025]. In Fortnite, the number of map creators grew from 24,000 to 70,000 during 2024 [@fortnite2024]. By the end of 2025, more than 35,000 Roblox creators were in its payout programme [@roblox10k].

**What the problem is.** A person wants to build a level from a real place: a corner of a desk, a patch of floor, a model. A phone with a LiDAR depth sensor captures such a place in metres [@luetzenburg2021; @lidar]. But scanning apps deliver a model for viewing, not a level [@scaniverse; @polycam; @kiri; @realityscan]. A character cannot walk on it straight away. The walkable surface, mesh simplification, scale and the walkability check are all done by hand in a 3D editor and a game engine. Without 3D modelling skills the real place never reaches the prototype; with those skills it costs a lot of manual work. A bad capture also looks like a good one: the scanner always produces a model, and the defect shows up only in the engine.

**Why now.** Every iPhone Pro since the iPhone 12 Pro and the iPad Pro have a LiDAR sensor [@lidar; @lidarIphone]. Browsers and popular game engines open the glTF 2.0 format [@gltf]. The number of people who make games and maps is growing [@fortnite2024; @roblox10k; @steam2025]. The methods an automatic build relies on — volumetric depth fusion, surface extraction and mesh simplification — are well established [@newcombe2011; @curless1996; @lorensen1987; @garland1997]. What is missing is a product that joins them into a "capture it — walk the level" path.

**Solution.** NVC Maps is a service that turns a short capture of a small area taken on an iPhone with a depth sensor into a game level. The phone app records and checks the capture, the server builds a visual mesh and a separate collision mesh for the character, and in the browser the map can be walked before it is taken into a game engine. An unsuitable capture is rejected with a reason.

## Goal and Objectives

**Goal.** Shorten the path from capturing a real area to a walkable game level to a single walk-around with a phone, without manual geometry fixing.

**Objectives.**

1. Identify where time and data are lost in the current path from capture to level.
2. Determine what existing scanners and research solutions lack for producing a walkable level directly.
3. Set measurable success indicators with baseline and target values.
4. Describe what the user does, what the system checks, and when it rejects a build.
5. Define the set of reference captures and checks used to accept the result, together with legal constraints and risks.

## Object and Subject

**Object** — the process of creating a game level from a real place: from capture to the first check of the level in a game engine.

**Subject** — the automatable part of this process: checking the capture, building the map with a separate collision mesh for the character, checking walkability in the browser and delivering the package for game engines.

## Methods

The requirements were gathered as follows:

- **Document analysis.** The project's technical specification and pipeline blueprint, the glTF 2.0 specification [@gltf], ARKit and RoomPlan documentation [@roomplan], the GDPR [@gdpr], WCAG 2.1 [@wcag].
- **Literature review.** Research on surface reconstruction, mesh simplification and turning video into interactive scenes [@xia2024; @newcombe2011; @curless1996; @lorensen1987; @garland1997; @kerbl2023; @luetzenburg2021; @yang2024; @zhou2018].
- **Benchmarking of analogs.** Comparison of nine solutions based on public descriptions, documentation and prices [@polycam; @scaniverse; @kiri; @realityscan; @luma; @marble; @roomplan; @xia2024] (section 1.3).
- **Proto-persona.** The persona is based on the document and market analysis. No user interviews were conducted; validating the persona with real people is listed as a risk (section 2.9).

The techniques follow BABOK v3 [@babok]: document analysis, benchmarking and market analysis, process modelling, user stories, MoSCoW prioritisation.

## Glossary

| Term | Meaning |
|------|---------|
| Capture | A recording of an area on the phone: video, camera poses, metadata and depth frames in one file |
| Camera poses | Where the phone was and where it pointed at each moment of the recording |
| Visual mesh (`map.glb`) | The part of the map the player sees |
| Reconstruction method | How the server obtained the surface; for a suitable capture, LiDAR depth fusion |
| Collision mesh (`collision.glb`) | An invisible simplified mesh the character walks on |
| Map package | Five files: visual mesh, collision mesh, manifest, bounds, report |
| Job | One map build on the server with the status "queued", "building", "ready" or "rejected" |
| Rejection | The service's answer "the map cannot be built" with a reason instead of a map |
| Reference capture | One of four saved captures used for acceptance: two suitable and two unsuitable |
| Walk check | Walking a character on the collision mesh in the browser before the package is delivered |

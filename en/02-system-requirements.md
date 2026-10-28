# 2. System Requirements

## 2.1. Vision and Goals

### Vision

NVC Maps turns a short video of a real place into a game level. A person walks around a small area with an iPhone, and the service builds a map a character can walk on, checks it in the browser and delivers it as a file for any engine. A bad capture gets an honest rejection with a reason instead of a broken map.

### Business Goals

The business goals are listed in Table 2.1.

Table 2.1. Business goals

| ID | Goal |
|----|------|
| BG-1 | Remove manual geometry fixing from the path between capture and a walkable level |
| BG-2 | Shorten the time from capture to the first check of the level |
| BG-3 | Never pass off an unsuitable capture as a finished map |
| BG-4 | Deliver a map that fits a game budget straight away |

### KPIs

Goal achievement is measured by four KPIs (Table 2.2).

Table 2.2. KPIs: baseline and target values

| ID | Indicator | Baseline (today) | Target | How to measure |
|----|-----------|------------------|--------|----------------|
| KPI-1 | Share of suitable reference captures that give a walkable level without manual fixing | 0%: scanners do not deliver a collision mesh for the character (section 1.3) | 100% on reference captures S1, S2 | Run of the reference captures, walk check: the character stands ≥ 5 s and crosses the map edge to edge |
| KPI-2 | Time from sending a capture to the first walk check | 2–4 h on the manual AS-IS path (author's estimate, steps 2–5 of section 1.1) | ≤ 15 min | Time between sending and opening the map in the browser on the reference captures |
| KPI-3 | Share of unsuitable captures rejected with a reason | 0%: scanners produce a model for any capture | 100% on reference captures N1, N2 | Run of the reference captures, reason text in the report |
| KPI-4 | Map weight | Dense scan without simplification: hundreds of thousands of triangles (author's estimate for the manual path, section 1.1) | Visual mesh ≤ 50,000 triangles; collision mesh ≤ 25% of the visual mesh and ≥ 100 faces | Metrics in the build report |

## 2.2. Stakeholders and Users

### Stakeholders

The stakeholders, their interests and influence are given in Table 2.3.

Table 2.3. Stakeholders: interest and influence

| Stakeholder | Interest | Interest (H/M/L) | Influence (H/M/L) |
|-------------|----------|------------------|-------------------|
| Users: indie developers, level designers, model makers, teachers and students | Get a walkable level from a real place quickly | H | H |
| Product owner and team | The product solves the users' pain and runs without manual intervention; the team operates the service and the test link | H | H |
| Apple: iOS, ARKit, LiDAR, App Store | The app follows the App Store rules and asks for camera access clearly | L | H |
| Game engines and the glTF standard: Godot, Unity, Unreal, Khronos Group | Correct files in an open format | L | H |
| Data protection supervision (GDPR) | Faces and other people's premises do not enter the data without a legal basis | L | H |
| Hosting provider | Resources within the plan and limits | L | M |
| Authors of open libraries and models: Open3D, PyTorch, Depth Anything | Licences are respected | L | M |
| Competitors: Polycam, Scaniverse, KIRI, RealityScan, Luma, World Labs | They set users' expectations of a scanner | M | M |
| Communities: itch.io and game jams, game development courses, Fortnite Creative, Roblox | Tools that speed up game creation; a channel to users | M | L |
| Player on the finished map | Not to fall through the floor | H | L |
| Owner of the captured place | To know about the capture and be able to refuse | H | L |
| A person who accidentally appears in the frame | Not to end up in someone else's materials | H | L |

Release scope and success criteria are agreed with the H/H groups. The rules of the L/H groups are followed as constraints: App Store, glTF, GDPR. The interests of the H/L groups are protected by product rules: the walk check, capture rules, and no close-up faces.

### System Users (Actors)

- **Capture operator** — captures the area, passes the recording check, sends the capture.
- **Map builder** — follows the jobs, reads the report, walks the map in the browser.
- **Game developer** — downloads the package and takes it into the engine.
- **Service team** — issues and replaces the test link to the reference jobs.

Usually the first three roles are played by one person. The use case diagram is Image A.2.4.

### Persona

The persona is based on the document and market analysis (Introduction, "Methods"). Validating it in interviews is listed as a risk (R6).

**Anya, 24, indie developer.** Makes small games in Godot in her spare time and takes part in 48–72-hour game jams. Takes 3D models from free libraries and finds Blender hard. Owns an iPhone 15 Pro.

- **Goal:** get a level with real texture within a couple of hours of a jam, for example from her own desk.
- **Pain:** the scanner gives a good-looking model, but the character cannot walk on it; building the collision mesh takes an evening she does not have at a jam.
- **How the product helps:** a 30-second walk around the desk, a walk check in the browser, GLB straight into Godot.

## 2.3. Project Scope

### In Scope

- Capture on an iPhone or iPad with LiDAR: a zone of about 80 × 80 cm, walk-around, recording check, upload to the server.
- Map build at sensor scale: visual mesh, lightweight collision mesh, manifest, bounds, report.
- Rejection with a reason for an unsuitable capture instead of arbitrary geometry.
- Capture intake, job queue, status, package storage.
- Browser: capture upload, list of own jobs, report, walking on the collision mesh next to a capture frame, package download.
- Browser sign-in via a one-time link from the phone; a test link to four reference jobs.
- An open description of the exchange: what is accepted and what is returned.

### Out of Scope

- A full game and a mandatory Unreal demo.
- Scaling the map for a specific character.
- Textures, a second level of detail, splats.
- Training an own depth model; a build without LiDAR affects the release only as a disabled mode.
- Android as a release platform.
- An admin panel, user accounts, roles, viewing other users' maps.

### Assumptions and Constraints

The project's assumptions and constraints are given in Table 2.4.

Table 2.4. Assumptions and constraints

| Type | Description | Consequence |
|------|-------------|-------------|
| Resources | One developer builds the product | If time runs short, Should and Could stories are dropped first (section 2.5) |
| Deadlines | The first release date is fixed by the project calendar | Scope is limited to Must stories; everything else comes after the release |
| Devices | Capture requires an iPhone Pro or iPad Pro with LiDAR [@lidar; @lidarIphone]; the simulator and the browser provide no depth | Without a device the product is checked with the four reference captures and the test link |
| Data access | Only the author's own captures and four reference captures are used: two suitable, two unsuitable. No third-party datasets | No organisation's consent is needed (statements); verification is limited to the reference captures |
| API and platform | Depth and poses are available only through ARKit on the device [@arkit]; the map format is glTF 2.0 [@gltf] | Release platform is iOS; package in GLB |
| Compute | Area size is limited by server compute: 80 × 80 cm by default | Quality thresholds are set for this size |

## 2.4. Solution Concept

The solution has four parts (Image A.2.3):

1. **Capture app on the iPhone.** Records video, camera poses, metadata and LiDAR depth, checks the recording and sends it to the server. The server address and the user's key are stored in the app.
2. **Intake service.** Accepts a capture from the phone or the browser, queues a job, stores jobs, metrics and file links. Sending the same capture again returns the existing job.
3. **Build pipeline.** A separate server process takes a job from the queue, builds the five-file package and puts it in storage. For an unsuitable capture it records a rejection with a reason.
4. **Web client.** Shows the user's jobs, the report and walking on the collision mesh next to a capture frame. Sign-in is via a one-time link from the phone or a reusable test link to the reference jobs.

External systems: ARKit on the device, hosting with a database and file storage, game engines that open the package.

### Alternatives

Two alternatives are compared in Table 2.5.

Table 2.5. Comparison of concept alternatives

| Criterion | A. Build on the phone | B. Build on the server and check in the browser (chosen) |
|-----------|-----------------------|-----------------------------------------------------------|
| Compute | Limited by phone resources: depth fusion and simplification of the whole surface run on the device | The server builds without device limits; area size is configurable |
| Repeatability | The result depends on the phone model and app version | One builder and one configuration for all captures |
| Check without a phone | Impossible: the product cannot be checked without a LiDAR device | Reference jobs via the test link |
| Walk check | Only on the phone, small and inconvenient | In the browser on a large screen next to a capture frame |
| Privacy | Data never leaves the phone | Data is stored on the server: a legal basis and erasure are needed (2.8) |
| Cost | No server costs | Hosting costs |

**Rationale.** Option B wins on repeatability, checking without a device and convenience of the walk check, which directly supports KPI-1 to KPI-3. Its drawbacks — privacy and cost — are covered by the requirements in 2.8 and by risks R4 and R5.

## 2.5. Functional Requirements

### Epics

The epics and their links to business goals and KPIs are given in Table 2.6.

Table 2.6. Epics and their links to goals

| Epic | Name | Business goal | KPI |
|------|------|---------------|-----|
| E1 | Capture and recording check | BG-3 | KPI-3 |
| E2 | Upload and jobs | BG-2 | KPI-2 |
| E3 | Build, report and quality | BG-1, BG-3, BG-4 | KPI-1, KPI-3, KPI-4 |
| E4 | Walk check in the browser | BG-1, BG-2 | KPI-1, KPI-2 |
| E5 | Package for the engine | BG-1, BG-4 | KPI-1, KPI-4 |
| E6 | Service operation | BG-2 | KPI-1, KPI-3 |

Acceptance criteria are written in the Given / When / Then format. The full backlog in one table is in Appendix 1.

Mock-ups of the key stories US-1.2, US-2.3, US-3.1 and US-4.1 are shown in Image 2.1; all screens are on the project website.

![Image 2.1. Mock-ups of the key stories](wireframes/shots/key-stories-en.png)

### E1. Capture and Recording Check

The epic's stories and acceptance criteria are in Table 2.7.

Table 2.7. Stories of epic E1. Capture and recording check

| ID | Story | Acceptance criteria | MoSCoW |
|----|-------|---------------------|--------|
| US-1.1 | **Recording the zone.** **As a** capture operator, **I want** to record an area on a phone with LiDAR **so that** I get a capture with depth in metres. | 1) **Given** a phone with LiDAR and the camera tracking its position, **when** the operator starts recording, **then** a 0.8 × 0.8 m zone is fixed on the floor. 2) **Given** the recording has stopped, **when** the capture is saved, **then** it contains video, camera poses, metadata and depth frames. 3) **Given** the camera is not yet tracking its position, **when** the operator tries to start recording, **then** the "Record" button is disabled and the hint "AR is starting — move the camera slowly over the floor" is shown. 4) **Given** recording has run for 30 s, **when** the time is up, **then** recording stops automatically. | Must |
| US-1.2 | **Recording check before upload.** **As a** capture operator, **I want** to know at once whether the recording is usable **so that** I do not send a defective capture and can retake it on the spot. | 1) **Given** a recording of 10–30 s, a camera path ≥ 0.28 m, a view-angle change ≥ 90°, a zone width ≤ 0.92 m and a gap between poses ≤ 0.5 s, **when** the check finishes, **then** "Map ready" and the "Send" button are shown. 2) **Given** a recording shorter than 10 s, **when** the check finishes, **then** "The recording must last 10 to 30 seconds" is shown. 3) **Given** a camera path shorter than 0.28 m, **when** the check finishes, **then** "Walk around the zone" is shown. 4) **Given** a view-angle change under 90°, **when** the check finishes, **then** "The views are too similar — walk around and show all sides" is shown. 5) **Given** a zone wider than 0.92 m, **when** the check finishes, **then** "The zone is too large — capture an area of about 80×80 cm" is shown. 6) **Given** a gap between poses longer than 0.5 s, **when** the check finishes, **then** "The gap between frames is too large — retake more smoothly" is shown. 7) **Given** any check has failed, **when** the operator views the result, **then** only "Retake" is available instead of "Send". | Must |
| US-1.3 | **Walk-around hint.** **As a** capture operator, **I want** to see during recording how much more to walk **so that** I capture the area on the first attempt. | 1) **Given** recording has run for 5 s or more, **when** the camera path is shorter than 0.28 m, **then** the hint "Don't stand still — walk slowly around the zone" is shown. | Should |

### E2. Upload and Jobs

The epic's stories and acceptance criteria are in Table 2.8.

Table 2.8. Stories of epic E2. Upload and jobs

| ID | Story | Acceptance criteria | MoSCoW |
|----|-------|---------------------|--------|
| US-2.1 | **Upload from the phone.** **As a** capture operator, **I want** to send the recording to the server with one button **so that** the build starts without a manual command. | 1) **Given** the check has passed, **when** the operator taps "Send", **then** a job with the status "queued" is created. 2) **Given** the upload failed because of the network, **when** the error arrives, **then** the reason is shown as text and the upload can be repeated. 3) **Given** a job for this capture already exists, **when** the operator sends the same capture again after a network error, **then** the same job is returned and no second build starts. 4) **Given** the user already has three builds running, **when** they send another capture, **then** no job is created and "Wait for the current builds to finish: there are already three" is shown. | Must |
| US-2.2 | **Upload from the browser.** **As a** map builder, **I want** to upload a saved capture through a browser form **so that** I can build a map without a phone. | 1) **Given** the upload form is open, **when** a file without video, poses or metadata is selected, **then** the missing parts are shown before sending. 2) **Given** the capture is complete, **when** the builder submits the form, **then** a job is created and the job list opens. 3) **Given** the file is larger than 400 MB, **when** the builder submits the form, **then** no job is created and "The capture file is larger than 400 MB" is shown. | Must |
| US-2.3 | **My jobs in the browser.** **As a** map builder, **I want** to open all my jobs in the browser with one button on the phone **so that** I can view reports and maps on a large screen. | 1) **Given** the user has jobs, **when** they tap "Open in browser", **then** the browser opens a list of all their jobs with date and status. 2) **Given** the one-time link has already been opened or more than 10 minutes have passed, **when** it is opened again, **then** the list does not open and "The link has already been opened or has expired" is shown. 3) **Given** another browser without a session, **when** the address of someone else's job is opened, **then** the map and report are not shown and "A link from the phone or a test link is required" is shown. | Must |
| US-2.4 | **Status filter.** **As a** map builder, **I want** to filter jobs by status **so that** I quickly find ready maps and rejections. | 1) **Given** the job list is open, **when** the "ready" filter is selected, **then** only ready jobs are shown. | Should |
| US-2.5 | **Deleting a capture from the phone.** **As a** capture operator, **I want** to delete an unneeded capture from "My maps" **so that** I free up phone storage. | 1) **Given** a capture card in "My maps", **when** the operator confirms deletion, **then** the capture files are deleted from the phone. | Could |

### E3. Build, Report and Quality

The epic's stories and acceptance criteria are in Table 2.9; the build rejection reasons with thresholds and messages are in Table 2.10.

Table 2.9. Stories of epic E3. Build, report and quality

| ID | Story | Acceptance criteria | MoSCoW |
|----|-------|---------------------|--------|
| US-3.1 | **Build report.** **As a** map builder, **I want** the report to show the status, reconstruction method and metrics **so that** I decide by numbers rather than by eye. | 1) **Given** the build succeeded, **when** the builder opens the report, **then** the status "ready", the reconstruction method "LiDAR depth fusion", the triangle counts of the visual and collision meshes and the file sizes are shown. 2) **Given** the build was rejected, **when** the builder opens the report, **then** instead of metrics the status "rejected" and the reason text from Table 2.10 are shown. | Must |
| US-3.2 | **Rejection with a reason.** **As a** map builder, **I want** an unsuitable capture to be rejected with a clear reason **so that** I do not mistake a defect for a map. | 1) **Given** the capture violates any condition in Table 2.10, **when** the build finishes, **then** the job status is "rejected" and the reason is the text from the same row of Table 2.10. 2) **Given** the status is "rejected", **when** the builder opens the job, **then** no placeholder geometry is delivered, and viewing and download are unavailable. 3) **Given** the capture meets all conditions in Table 2.10, **when** the build finishes, **then** the status is "ready" and there is no rejection. | Must |
| US-3.3 | **Map within the game budget.** **As a** game developer, **I want** to receive the map within budget **so that** I do not simplify it by hand. | 1) **Given** the reconstructed surface exceeds the budget, **when** the build runs, **then** the system itself simplifies the visual mesh to 50,000 triangles and the collision mesh to 25% of the visual mesh faces. 2) **Given** the build succeeded, **when** the package is written, **then** the visual mesh is ≤ 50,000 triangles and ≤ 25 MB, and the collision mesh is ≥ 100 faces and ≤ 8 MB. 3) **Given** the budget is still not met after simplification, for example the collision mesh has fewer than 100 faces or the visual mesh file is larger than 25 MB, **when** the build finishes, **then** the status is "rejected" with the reason "The map did not fit the game budget; no package was issued". | Must |
| US-3.4 | **Comparing a repeated build.** **As a** map builder, **I want** to compare a repeated build of the same capture with the first one **so that** I can confirm the result is reproducible. | 1) **Given** two builds of the same capture, **when** the builder compares the reports, **then** the reconstruction method is the same and the triangle counts differ by no more than 15%. | Should |

Table 2.10. Build rejection reasons

| Condition | Threshold | Reason shown to the user |
|-----------|-----------|--------------------------|
| No camera poses in the capture | The pose file is missing or empty | "The capture has no camera poses: retake the area" |
| Poses do not match the video | No pose within 0.25 s of a video frame | "Camera poses are damaged or do not match the video: retake the area" |
| Depth frames are damaged | Depth frames cannot be read or do not match the video in time | "LiDAR depth frames are damaged or do not match the video" |
| Zone not found | The zone centre was not recorded, or nothing remains inside the 80 × 80 cm square above the supporting surface | "The 80×80 cm zone was not found in the capture: walk around the area again" |
| Surface not reconstructed | Depth fusion produced an empty surface | "The surface could not be reconstructed: retake the area more slowly" |
| No walkable surface | The build report has the status "rejected" | "The capture produced no walkable surface: retake the area" |
| Map budget not met | Any threshold of US-3.3 is not met after simplification | "The map did not fit the game budget; no package was issued" |
| Build too long | The build runs longer than 15 minutes | "The build did not finish in time: retake a shorter area" |
| Service failure | Any other build error | "The build stopped because of a service error. Send the capture again later" |

### E4. Walk Check in the Browser

The epic's stories and acceptance criteria are in Table 2.11.

Table 2.11. Stories of epic E4. Walk check in the browser

| ID | Story | Acceptance criteria | MoSCoW |
|----|-------|---------------------|--------|
| US-4.1 | **Walking the map.** **As a** map builder, **I want** to walk a character on the finished map in the browser **so that** I check walkability without a game engine. | 1) **Given** the build succeeded, **when** the builder opens the viewer, **then** the character stands on the collision mesh for at least 5 s and does not fall through. 2) **Given** the viewer is open, **when** the builder moves the character along the zone diagonal from one corner to the opposite corner (about 1.1 m), **then** the character completes the route without falling through or getting stuck. 3) **Given** the build was rejected or is still running, **when** the builder opens the viewer, **then** the map does not load, and the job status and the rejection reason, if any, are shown. | Must |
| US-4.2 | **Capture frame next to the map.** **As a** map builder, **I want** to see a capture frame next to the model **so that** I can compare the map with the real place. | 1) **Given** the viewer is open, **when** the map has loaded, **then** a capture frame from the same camera is shown next to it. 2) **Given** another browser without a session, **when** the address of a frame of someone else's job is opened, **then** the frame is not served. | Must |
| US-4.3 | **Character height in the viewer.** **As a** map builder, **I want** to change the character height in the viewer **so that** I can try the map for different games. | 1) **Given** the viewer is open, **when** the builder changes the character height, **then** the character changes, while the map geometry and the package files do not. | Should |

### E5. Package for the Engine

The epic's stories and acceptance criteria are in Table 2.12.

Table 2.12. Stories of epic E5. Package for the engine

| ID | Story | Acceptance criteria | MoSCoW |
|----|-------|---------------------|--------|
| US-5.1 | **Package download.** **As a** game developer, **I want** to download a five-file package **so that** I can open the map in my engine. | 1) **Given** the build succeeded, **when** the developer clicks "Download", **then** they receive `map.glb`, `collision.glb`, `manifest.json`, `bounds.json`, `report.json`. 2) **Given** the package has been downloaded, **when** both GLB files are opened in a glTF viewer, **then** they open without errors. 3) **Given** the job is still queued, building or rejected, **when** the developer requests the package, **then** no files are served and "A package exists only for a ready job" is shown. | Must |
| US-5.2 | **Real scale and package description.** **As a** game developer, **I want** to receive the map in sensor metres with an axis description **so that** I can set the character scale myself. | 1) **Given** the package has been downloaded, **when** the developer reads the manifest, **then** it states metres, Y up, the fact of centring and a scale of 1. 2) **Given** the package has been built, **when** the map and capture sizes are compared, **then** the geometry scale has not changed. 3) **Given** the manifest units are not metres or the scale is not 1, **when** the package is checked, **then** the package is not issued. | Must |
| US-5.3 | **Godot instructions.** **As a** game developer, **I want** short instructions on opening the package in Godot **so that** I do not have to figure out the import myself. | 1) **Given** the report is open, **when** the developer follows the "How to open in Godot" link, **then** the steps for importing the visual and collision meshes are shown. | Should |

### E6. Service Operation

The epic's stories and acceptance criteria are in Table 2.13.

Table 2.13. Stories of epic E6. Service operation

| ID | Story | Acceptance criteria | MoSCoW |
|----|-------|---------------------|--------|
| US-6.1 | **Test link to the reference jobs.** **As** the service team, **we want** to issue a reusable link to four reference jobs **so that** the product can be checked without a LiDAR phone. | 1) **Given** a test link has been issued, **when** it is opened in any browser, **then** only the four reference jobs with reports and walking are shown. 2) **Given** the test link is open, **when** the list is viewed, **then** users' personal jobs are not shown. 3) **Given** the test link is open, **when** someone tries to upload a new capture, **then** no job is created and "The test link only allows viewing the reference jobs" is shown. | Must |
| US-6.2 | **Replacing the test link.** **As** the service team, **we want** to replace the test link **so that** access via the old one is closed. | 1) **Given** the link has been replaced, **when** the new one is opened, **then** the four reference jobs are shown. 2) **Given** the link has been replaced, **when** the old one is opened, **then** the jobs do not open and "A link from the phone or a test link is required" is shown. | Must |

### Priorities

A summary of priorities is given in Table 2.14.

Table 2.14. MoSCoW priorities

| Priority | Stories | Why |
|----------|---------|-----|
| Must | US-1.1, US-1.2, US-2.1–US-2.3, US-3.1–US-3.3, US-4.1, US-4.2, US-5.1, US-5.2, US-6.1, US-6.2 | Without them KPI-1 to KPI-4 cannot be reached |
| Should | US-1.3, US-2.4, US-3.4, US-4.3, US-5.3 | Improve convenience and checking; dropped first if time runs short |
| Could | US-2.5 | A small convenience on the phone |
| Won't | A full game, a mandatory Unreal demo, an own depth model, Android, an admin panel and user accounts, map scaling | Out of the release scope (2.3) |

### Traceability: Goal → Epic → Story

The links between goals, epics and stories are shown in Table 2.15.

Table 2.15. Traceability: goal → epic → story

| Goal | KPI | Epic | Stories |
|------|-----|------|---------|
| BG-1 No manual fixing | KPI-1 | E3, E4, E5 | US-3.1, US-3.3, US-4.1, US-4.2, US-5.1, US-5.2 |
| BG-2 Faster to the check | KPI-2 | E2, E4, E6 | US-2.1–US-2.4, US-4.1, US-6.1, US-6.2 |
| BG-3 Honest rejection | KPI-3 | E1, E3 | US-1.1–US-1.3, US-3.1, US-3.2 |
| BG-4 Game budget | KPI-4 | E3, E5 | US-3.3, US-3.4, US-5.2 |

## 2.6. Use Case Scenarios

### UC-1. Capture and Send an Area

- **Actor:** capture operator.
- **Precondition:** an iPhone or iPad with LiDAR, the app installed, camera access granted.
- **Result:** a build job has been created and is queued.

**Main flow**

1. The operator opens "Scan" and points the phone at the floor.
2. The system shows a 0.8 × 0.8 m zone frame.
3. The operator starts recording and walks around the zone for 10–30 s.
4. The operator stops recording.
5. The system checks the duration, path, view-angle change, poses and depth and shows "Ready".
6. The operator taps "Send".
7. The system sends the capture to the server; the server creates a job and returns its status "queued".

**Alternative flow A1. The check fails.** At step 5 the system shows the reason in one sentence and "Retake". The operator returns to step 1. Sending this recording is unavailable.

**Alternative flow A2. Connection lost during upload.** At step 7 the connection drops. The operator taps "Send" again. The server recognises the capture and returns the job already created; no second build starts.

The activity diagram of the scenario is Image A.2.7, and the system sequence diagram is Image A.2.5.

### UC-2. Check the Map in the Browser

- **Actor:** map builder.
- **Precondition:** the user has at least one submitted job; the phone app stores the user's key.
- **Result:** the builder has walked the map and downloaded the package.

**Main flow**

1. The builder taps "Open in browser" on the phone.
2. The system issues a one-time link and opens the browser.
3. Using the link, the system creates a session and shows the user's job list.
4. The builder opens a ready job; the system shows the report.
5. The builder opens the viewer; the system loads the collision mesh and a capture frame.
6. The builder walks the character from edge to edge.
7. The builder clicks "Download"; the system serves the five-file package via a short-lived link.

**Alternative flow A1. The link has expired.** At step 3 the link has already been opened or has expired. The system shows an empty sign-in page. The builder returns to step 1, and the phone issues a new link.

**Alternative flow A2. The build was rejected.** At step 4 the status is "rejected". The system shows the reason; viewing and download are unavailable. The builder moves to UC-1 to retake the area.

The system sequence diagram is Image A.2.6.

## 2.7. Non-Functional Requirements

The non-functional requirements with measurable indicators are given in Table 2.16.

Table 2.16. Non-functional requirements

| ID | Category | Requirement | Indicator and value | KPI, stories |
|----|----------|-------------|---------------------|--------------|
| NFR-1 | Performance | Building a reference capture | ≤ 10 min from queuing to the status "ready" or "rejected" | KPI-2; US-2.1, US-3.1 |
| NFR-2 | Performance | Opening the map viewer | ≤ 10 s until the character can be controlled on a 50 Mbit/s connection | KPI-2; US-4.1 |
| NFR-3 | Performance | Package file size | `map.glb` ≤ 25 MB, `collision.glb` ≤ 8 MB | KPI-4; US-3.3 |
| NFR-4 | Reliability | Build repeatability | Same reconstruction method, triangle count difference ≤ 15% | KPI-1; US-3.4 |
| NFR-5 | Security | Access to jobs | The list, report, viewer and files are served only to the owner's session: 0 successful openings of someone else's job in testing | US-2.3, US-6.1 |
| NFR-6 | Security | Link lifetime | The one-time link works once and for ≤ 10 min; a file link for ≤ 15 min | US-2.3, US-5.1 |
| NFR-7 | Security | Secrets | 0 passwords and keys in the service image and repository; secrets are set by the hosting | — |
| NFR-8 | Availability | Uptime | ≥ 99% per calendar month by external monitoring | KPI-2 |
| NFR-9 | Usability | Web client | Compliance with WCAG 2.1 AA [@wcag]: text contrast ≥ 4.5 : 1, all forms can be completed with the keyboard | US-2.2, US-2.3 |
| NFR-10 | Usability | Phone | Touch targets ≥ 44 pt; a rejection reason is one sentence of ≤ 120 characters | US-1.2 |

## 2.8. Legal and Ethical Requirements

### Personal Data

Which data may be personal and on what basis it is processed is shown in Table 2.17.

Table 2.17. Personal data and legal bases for processing

| Data | Why it may be personal | Basis under the GDPR [@gdpr] | Requirement |
|------|------------------------|------------------------------|-------------|
| User key on the phone | A pseudonymous identifier of a person | Art. 6(1)(b): performance of the service at the user's request | The key is not linked to a name, e-mail or phone number |
| Video and depth of the area | A person or someone else's premises may accidentally appear in the frame | Art. 6(1)(b) for the capture author; Art. 6(1)(f), legitimate interest, for people who accidentally appear in the frame | Only a floor, desk or model is captured; a recording with a close-up face is not published; audio is not needed for the build and is not stored |
| IP addresses in server logs | A network identifier | Art. 6(1)(f): service security | Logs are kept for ≤ 30 days |

- **Minimisation and retention.** Captures and packages are kept for ≤ 90 days after the last opening and then deleted.
- **Right to erasure (Art. 17).** A user can request deletion of their jobs by the e-mail address given on the website. The request is fulfilled within ≤ 30 days by job number: the GDPR allows one month for a response [@gdpr]. There is no separate panel for this (2.3).
- **Transparency (Art. 13).** The app and the website show a short notice: what data is collected, why, how long it is kept and how to delete it.
- **Place owner.** The user confirms that they are capturing their own place or a place with the owner's permission.

### Consent of Interview Participants

No interviews or surveys were conducted for this work (Introduction, "Methods"). Participant consent is therefore not required. If interviews are held to validate the persona (R6), participants sign consent to recording and processing of their answers.

### Licences

Open3D [@zhou2018] and trimesh [@trimeshRepo] are under MIT, and PyTorch [@pytorchRepo] under BSD-3-Clause: they are used with their copyright notices kept. Of the Depth Anything V2 models, only Small under Apache-2.0 is used [@depthAnythingRepo]; the larger models under a non-commercial licence are not used. glTF 2.0 [@gltf] is an open royalty-free standard. The reference captures were made by the author, so no third-party rights are affected.

### Standards

- **WCAG 2.1 AA** [@wcag] for the web client (NFR-9).
- **glTF 2.0** [@gltf] for the map package (US-5.1, US-5.2).
- **App Store Review Guidelines** [@appStoreGuidelines]: a clear explanation of why the app needs the camera.

## 2.9. Risks

The project risks are assessed in Table 2.18.

Table 2.18. Project risks

| ID | Risk | Probability | Impact | Mitigation | Dependency |
|----|------|-------------|--------|------------|------------|
| R1 | The map is unrecognisable or has holes | M | H | A small zone, mandatory poses and depth, rejection instead of arbitrary geometry | LiDAR quality [@luetzenburg2021], fusion algorithms [@newcombe2011; @curless1996] |
| R2 | The collision mesh does not support the character | M | H | Walk check before the package is issued; a collision budget of at least 100 faces | US-4.1, US-3.3 |
| R3 | The reviewer or user has no LiDAR phone | H | M | Four reference captures and the test link | US-6.1; device access (2.3) |
| R4 | The build needs more resources than the hosting provides | M | M | Configurable zone size, frame count limit, queue | Hosting provider |
| R5 | Personal data enters the frame or is kept longer than needed | L | H | Capture rules, 90-day retention, deletion on request | Requirements 2.8, GDPR [@gdpr] |
| R6 | The persona and pains do not match real users: no interviews were held | M | H | Validate the persona in 5 interviews with indie developers before the next release; monitor the KPIs | Methods (Introduction) |
| R7 | App Store rules or the ARKit API change | L | H | Follow Apple updates; the capture format is documented openly, and a capture can be uploaded from the browser | Apple |

Probability and impact: H — high, M — medium, L — low.

## 2.10. Chapter Conclusions

**What the requirements fix.** A vision and four business goals with KPIs, baseline and target values. Stakeholders, actors and a persona. The release scope, assumptions and constraints. A solution concept with a context diagram and a rationale for the choice. Six epics and 20 user stories with MoSCoW priorities; every Must story has a positive and a negative acceptance criterion in the Given / When / Then format. Build rejection reasons are defined by thresholds and message texts. Two use case scenarios with alternative flows and sequence diagrams. Ten measurable NFRs, legal requirements and seven risks.

**How the result is verified.** The evaluation criteria match the KPIs of section 2.1 and are checked on the four reference captures via the test link:

- **KPI-1:** reference captures S1 and S2 give a walkable level without manual fixing — the character stands ≥ 5 s and crosses edge to edge (US-4.1).
- **KPI-2:** from upload to the walk check takes ≤ 15 min (NFR-1, NFR-2).
- **KPI-3:** reference captures N1 and N2 are rejected with a reason text (US-3.2).
- **KPI-4:** visual mesh ≤ 50,000 triangles, collision mesh ≤ 25% and ≥ 100 faces, files within NFR-3 (US-3.3).

The release is not accepted if success was achieved by a placeholder, the map is fixed by hand after the build, the geometry is rescaled, the character falls through the collision mesh, or an unsuitable capture produced a successful build.

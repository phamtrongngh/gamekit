---
name: free-game-asset-scout
description: Find, compare, license-check, rank, and optionally download free game assets from the web for the current game project. Use this skill whenever the user asks to search online for free game assets, asset packs, 3D models, textures, materials, HDRIs, rigs, animations, Mixamo clips, Godot-ready assets, Kenney/Quaternius/Poly Haven/ambientCG/OpenGameArt/Sketchfab/itch.io assets, or wants an agent to evaluate whether online assets match the project's art style, mesh quality, rigging, animation needs, license, or Godot import requirements before using them. Prefer this skill before downloading third-party assets into a project.
---

# Free Game Asset Scout

Use this skill to scout free third-party game assets, judge whether they fit the current project, and produce a decision-ready report before anything is downloaded. The default policy is prototype-broad: prototype-only or non-commercial candidates may appear in reports, but they must be flagged as release blockers.

This skill is for finding and evaluating existing assets. If the user wants AI-generated bitmap assets, use `game-asset-imagegen`. If the user wants to create or process 3D models through Tripo3D, use `tripo3d-game-assets`.

## Default Rules

- Always inspect the project context before searching, unless there is no local project to inspect.
- Always verify license information from the asset page or official source before recommending an asset.
- Always report candidates and ask for explicit confirmation before downloading.
- Never download during the first scout/report pass.
- Reject assets with unclear provenance, contradictory license terms, ripped franchise/IP content, or no usable license.
- Treat non-commercial, no-derivatives, editorial-only, marketplace-restricted, or prototype-only assets as release blockers.
- Do not treat search snippets, mirrors, reposts, or generated summaries as license proof.

## Reference Files

Read only the references needed for the task:

- `references/source-map.md`: source selection, strengths, caveats, and source-specific search guidance.
- `references/license-policy.md`: prototype-broad license rules, release blockers, attribution, and download records.
- `references/fit-rubric.md`: 100-point scoring rubric, report template, manifest schema, and Godot import checklist.

## Workflow

### 1. Inspect Project Context

Look for project facts that affect asset fit:

```bash
find . -name project.godot -o -name "*.tscn" -o -name "*.scn" -o -name "*.glb" -o -name "*.gltf" -o -name "*.fbx" -o -name "*.obj"
find . -maxdepth 4 -type d \( -iname "*asset*" -o -iname "*texture*" -o -iname "*material*" -o -iname "*animation*" \)
rg -n "Godot|viewport|style|low.?poly|PBR|mobile|target|character|animation|license|third_party" .
```

If a Godot project exists, note:

- Godot version or config hints from `project.godot`.
- Existing import formats and asset folders.
- Visual style: low-poly, stylized, pixel, realistic, horror, fantasy, sci-fi, UI-heavy, etc.
- Camera/use case: first person, third person, top-down, side-scroller, cinematic, UI.
- Technical needs: GLB/GLTF/FBX/OBJ, PBR textures, rigged humanoid, animation clips, collision-ready props, texture resolution, platform budget.

If no project exists, infer from the user's prompt, attached images, prior conversation, README files, or requested engine. State the missing context as an assumption in the report.

### 2. Build Search Targets

Turn the request into concrete asset queries:

- Asset role: prop, environment kit, texture/material, HDRI, character, rig, animation, UI, VFX, audio.
- Visual constraints: style, palette, realism level, theme, era, genre, scale, silhouette.
- Technical constraints: Godot-friendly format, rig type, animation names, PBR maps, poly budget, texture size.
- License constraints: default prototype-broad policy unless the user asks for stricter terms such as CC0 only.

Prefer sources from `references/source-map.md`. Use targeted search queries with source names and license terms, such as:

```text
site:kenney.nl hospital 3d assets CC0
site:quaternius.com low poly zombie animation CC0
site:polyhaven.com medical prop 3d model CC0
site:ambientcg.com hospital floor material CC0
site:opengameart.org Godot horror hospital 3D CC0 OR CC-BY
site:sketchfab.com downloadable hospital bed glb Creative Commons
site:itch.io free low poly hospital asset pack license
```

### 3. Verify Each Candidate

For each promising candidate, open the original asset page and verify:

- Asset name, author, source URL, preview URL, direct download or account requirement.
- File formats and whether GLB/GLTF/FBX/OBJ/PNG/WAV/etc. are available.
- License name, license URL or page text, attribution requirements, commercial/prototype restrictions, redistribution restrictions, AI/training restrictions if relevant.
- Rig, skeleton, animation clips, root motion, retargeting notes, and whether the model is humanoid or custom.
- PBR maps, texture resolution, poly/triangle count, LODs, scale, modularity, and whether materials are engine-specific.

If any key facts are missing, keep the candidate only if it is useful as a low-confidence lead. Mark missing facts clearly and do not recommend downloading.

### 4. Score And Rank

Use the rubric in `references/fit-rubric.md`:

- License/provenance: 20
- Art style match: 20
- Godot/import compatibility: 20
- Mesh/material/texture quality: 15
- Rig/animation suitability: 15
- Integration cost: 10

Verdicts:

- `strong_fit`: score 80-100 and no release blocker.
- `usable`: score 65-79 and no release blocker.
- `prototype_only`: score 50-64, or any non-commercial/prototype-only/release-blocked license.
- `reject`: score below 50, unclear license, ripped IP risk, unusable format, or contradictory terms.

Do not inflate scores to make weak candidates look acceptable. If there are no good assets, say so and explain the closest alternatives.

### 5. Report Before Download

Return a ranked report before downloading. Include:

- Project/context inference.
- Search scope and sources checked.
- Ranked candidates table with name, source URL, preview URL, type, formats, license, attribution, score, verdict, risks, and Godot import notes.
- Score breakdown for top candidates.
- Release/prototype warnings.
- Recommended next action, phrased as a request for explicit user approval before download.

Use this compact table shape when practical:

```markdown
| Rank | Asset | Source | Type | Formats  | License | Score | Verdict    | Main Risk |
| ---- | ----- | ------ | ---- | -------- | ------- | ----: | ---------- | --------- |
| 1    | ...   | ...    | ...  | GLB, FBX | CC0     |    88 | strong_fit | none      |
```

Then add short per-asset notes for integration details that do not fit in the table.

### 6. Download Only After Approval

Download only when the user explicitly confirms a specific candidate by rank, name, or URL. Save under:

```text
assets/third_party/<source_slug>/<asset_slug>/
+-- raw/
+-- source/
+-- third_party_asset_manifest.json
```

Save license/readme/source evidence when available:

- License file or page text in `source/`.
- Source URL and author information.
- Attribution text if required.
- A copy of the report score and warnings.

Create a manifest matching the schema in `references/fit-rubric.md`. Include file hashes for downloaded files when feasible.

After download, report the saved paths and any manual import steps. Do not integrate or replace project assets unless the user explicitly asks for integration.

## Output Tone

Be direct and conservative. The user needs practical sourcing judgment, not a list of every search hit. Prefer fewer high-quality candidates with clear license and integration notes over a large noisy list.

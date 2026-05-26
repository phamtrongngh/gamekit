# Fit Rubric

Score candidates on a 100-point scale. Be conservative: a candidate that is easy to download but hard to integrate should not outrank a slightly less pretty asset that is cleanly licensed, Godot-friendly, and style-consistent.

## Score Breakdown

### License And Provenance: 20

- 20: CC0/public domain or clearly commercial-safe terms from original source.
- 16-18: CC-BY or permissive license with manageable attribution.
- 10-15: usable but conditional license, account/download restrictions, or share-alike/copyleft concerns.
- 1-9: prototype-only, non-commercial, ambiguous commercial terms, weak provenance.
- 0: no license, contradictory terms, ripped IP risk, or unsafe source.

### Art Style Match: 20

- 20: matches project style, palette, proportions, detail level, and genre.
- 16-18: close match with small material/color adjustments.
- 10-15: usable with restyling, decimation, or texture edits.
- 1-9: major clash but useful as placeholder.
- 0: visually incompatible.

### Godot/Import Compatibility: 20

- 20: GLB/GLTF or Godot-ready files, textures included, documented import path.
- 16-18: FBX/OBJ/Blend available with normal conversion path.
- 10-15: usable format but likely material/scale/animation cleanup needed.
- 1-9: proprietary/engine-specific package requiring significant extraction.
- 0: no usable source files or impossible import path.

### Mesh, Material, And Texture Quality: 15

- 15: clean topology or appropriate scan quality, PBR maps where needed, sensible resolution and scale.
- 11-14: minor cleanup, missing LODs, or manageable texture adjustments.
- 6-10: heavy mesh, inconsistent textures, missing maps, or optimization required.
- 1-5: severe cleanup needed.
- 0: unusable geometry/materials.

### Rig And Animation Suitability: 15

- 15: rig/animations match requested skeleton and clip needs.
- 11-14: retargeting or clip cleanup likely but reasonable.
- 6-10: rig exists but is undocumented/custom or missing key clips.
- 1-5: static asset for an animated need, or animation mismatch.
- 0: no relevant rig/animation and not useful for the request.

For static props or materials, assign this category based on animation relevance:

- 15 if animation is irrelevant and the asset fully satisfies its static role.
- 8-12 if the request may later need animated variants.
- 0-5 if the user explicitly requested animation and the asset lacks it.

### Integration Cost: 10

- 10: drop-in or minimal import settings.
- 8-9: minor folder cleanup, material remap, or scale adjustment.
- 5-7: needs Blender conversion, decimation, retargeting, or atlas cleanup.
- 1-4: requires significant manual work.
- 0: integration cost defeats the asset value.

## Verdicts

|  Score | Verdict          | Meaning                                              |
| -----: | ---------------- | ---------------------------------------------------- |
| 80-100 | `strong_fit`     | Best candidate; recommend after license check.       |
|  65-79 | `usable`         | Good enough, with noted cleanup or style compromise. |
|  50-64 | `prototype_only` | Useful placeholder or blocked by policy.             |
|   0-49 | `reject`         | Do not use.                                          |

Hard caps:

- Any non-commercial, personal-use, editorial-only, or ambiguous license caps the verdict at `prototype_only`.
- Any ripped IP/provenance failure is `reject`, regardless of score.
- Any missing license is `reject` unless the report labels it only as a lead and does not recommend download.

## Report Template

```markdown
## Project Fit Summary

<engine/style/technical assumptions>

## Search Scope

<sources checked and query strategy>

## Ranked Candidates

| Rank | Asset | Source | Type | Formats | License | Score | Verdict | Main Risk |
| ---- | ----- | ------ | ---- | ------- | ------- | ----: | ------- | --------- |

## Top Candidate Notes

### 1. <Asset>

- Source: <url>
- Preview: <url>
- Score: <license/provenance> + <style> + <Godot> + <quality> + <rig/animation> + <integration> = <total>
- Attribution: <required text or none>
- Godot notes: <format/import/scale/material/retargeting notes>
- Risks: <release blockers, cleanup, missing info>

## Recommendation

<download none yet; ask for explicit approval by rank/name/URL>
```

## Download Manifest Schema

Create `third_party_asset_manifest.json` next to downloaded raw files:

```json
{
  "asset_name": "asset display name",
  "asset_slug": "asset_slug",
  "source": "source name",
  "source_url": "https://example.com/asset",
  "preview_url": "https://example.com/preview.jpg",
  "author": "author name",
  "downloaded_at": "YYYY-MM-DDTHH:MM:SSZ",
  "approved_by_user": "verbatim user approval or brief summary",
  "license": {
    "name": "CC0",
    "url": "https://example.com/license",
    "requires_attribution": false,
    "attribution_text": "",
    "release_blocker": false,
    "notes": "verified from original asset page"
  },
  "fit_score": {
    "license_provenance": 20,
    "art_style": 18,
    "godot_import": 18,
    "mesh_material_texture": 13,
    "rig_animation": 15,
    "integration_cost": 8,
    "total": 92,
    "verdict": "strong_fit"
  },
  "files": [
    {
      "path": "raw/example.glb",
      "sha256": "..."
    }
  ],
  "warnings": [],
  "godot_import_notes": "Use GLB import; inspect material roughness after import."
}
```

## Godot Import Checklist

- Prefer GLB/GLTF for Godot 4 when available.
- FBX can work but may need importer settings, scale checks, material fixes, or Blender conversion.
- OBJ is acceptable for static meshes but usually loses rig/animation and may need material cleanup.
- Confirm texture paths and PBR maps after import.
- Check scene scale against existing project units.
- For characters, verify skeleton, bone naming, clip list, root motion, and retargeting plan.
- For mobile/low-end targets, check triangle count, texture resolution, draw calls, and LOD availability.
- Do not import source files into final project folders until license/manifest records are saved.

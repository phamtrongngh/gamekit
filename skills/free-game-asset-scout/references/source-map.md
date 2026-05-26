# Source Map

Use this reference to choose where to search first. Source policies change, so always verify license and download rules on the current original asset page before recommending or downloading.

## Official Reference Links

- Kenney support/license notes: https://kenney.nl/support
- Poly Haven license: https://polyhaven.com/license
- ambientCG license: https://docs.ambientcg.com/license/
- OpenGameArt FAQ: https://opengameart.org/node/5571
- Sketchfab glTF/downloadable asset overview: https://sketchfab.com/features/gltf
- Adobe Mixamo FAQ: https://helpx.adobe.com/creative-cloud/faq/mixamo-faq.html
- Godot 3D import formats: https://docs.godotengine.org/en/latest/tutorials/assets_pipeline/importing_3d_scenes/available_formats.html

## Default Source Priority

### Kenney

- Best for: CC0 game asset packs, 2D sprites, UI, low-poly 3D, effects, prototyping kits.
- Strengths: consistent packs, game-focused, simple licensing, easy provenance.
- Caveats: style is often clean/stylized and may not fit realistic or horror scenes without edits.
- License default to verify: Kenney asset pages/support commonly state public domain/CC0 for game assets.
- Good searches:
  - `site:kenney.nl/assets low poly hospital`
  - `site:kenney.nl/assets ui icons`
  - `Kenney CC0 3D props glb`

### Quaternius

- Best for: low-poly 3D packs, characters, creatures, props, modular environment kits, animation packs.
- Strengths: game-ready low-poly style, often includes FBX/GLB/Blender files and sometimes animations.
- Caveats: low-poly house style may clash with realistic/PBR projects.
- License default to verify: commonly CC0/public domain on official pages.
- Good searches:
  - `site:quaternius.com low poly zombie animation`
  - `site:quaternius.com universal animation library`
  - `site:quaternius.com hospital 3d`

### Poly Haven

- Best for: high-quality CC0 HDRIs, textures, and realistic 3D models.
- Strengths: strong provenance, high-quality PBR assets, clear CC0 policy.
- Caveats: assets are often realistic and may need optimization for mobile or stylized projects.
- License default to verify: official Poly Haven license states CC0 for assets.
- Good searches:
  - `site:polyhaven.com hospital 3d model`
  - `site:polyhaven.com floor tiles texture`
  - `site:polyhaven.com hdr hospital interior`

### ambientCG

- Best for: CC0 PBR materials and tileable textures.
- Strengths: clear PBR map sets, good for floors, walls, fabric, concrete, plastic, metal.
- Caveats: mostly materials, not full props or animation.
- License default to verify: official ambientCG license states CC0.
- Good searches:
  - `site:ambientcg.com vinyl floor hospital`
  - `site:ambientcg.com plastic material`
  - `site:ambientcg.com ceiling tile material`

### OpenGameArt

- Best for: broad free/open game art, sprites, audio, UI, 3D, effects.
- Strengths: game-focused, many licenses, useful for prototypes and niche searches.
- Caveats: license varies per asset and can include GPL/CC-BY-SA/CC-BY/CC0; quality and provenance vary.
- License handling: verify each asset's listed license and author. Flag copyleft/share-alike or attribution requirements.
- Good searches:
  - `site:opengameart.org horror hospital 3d`
  - `site:opengameart.org Godot animation CC0`
  - `site:opengameart.org medical UI CC-BY`

### Sketchfab

- Best for: specific 3D models, scans, downloadable GLB/GLTF/FBX/OBJ models under Creative Commons or marketplace terms.
- Strengths: huge model variety and previews.
- Caveats: license varies, many models are not game-ready, scans can be heavy, and some content has IP/provenance risk.
- License handling: only evaluate downloadable models with clear license on the original page. Be suspicious of branded/franchise/ripped content.
- Good searches:
  - `site:sketchfab.com downloadable hospital bed glb Creative Commons`
  - `site:sketchfab.com downloadable medical monitor low poly`
  - `site:sketchfab.com CC0 hospital cart 3D`

### itch.io

- Best for: indie asset packs, pixel art, UI, low-poly packs, free/prototype assets.
- Strengths: many game-specific packs and complete themed kits.
- Caveats: license is author-defined and inconsistent; "free" does not imply release-safe.
- License handling: inspect the asset page and included license text. Flag single-project, non-commercial, no-redistribution, or ambiguous terms.
- Good searches:
  - `site:itch.io free low poly hospital asset pack license`
  - `site:itch.io free horror hospital assets`
  - `site:itch.io free Godot 3D assets CC0`

### Mixamo

- Best for: humanoid characters, auto-rigging workflows, and humanoid animation clips.
- Strengths: good motion library, useful for prototypes, common FBX workflow.
- Caveats: Adobe ID/login required; terms are service-specific; animations may need retargeting and cleanup in Godot.
- License handling: verify Adobe Mixamo FAQ/terms and note that content should not be redistributed as a standalone asset pack.
- Good searches:
  - `Mixamo idle walk run animations Godot FBX`
  - `Mixamo commercial use FAQ`
  - `Godot Mixamo retargeting FBX`

## Source Selection By Need

| Need                               | Search First           | Search Next          |
| ---------------------------------- | ---------------------- | -------------------- |
| Stylized low-poly 3D props         | Kenney, Quaternius     | itch.io, OpenGameArt |
| Realistic PBR props                | Poly Haven, Sketchfab  | OpenGameArt          |
| PBR materials/textures             | ambientCG, Poly Haven  | OpenGameArt          |
| HDRIs/lighting                     | Poly Haven             | ambientCG            |
| Humanoid animations                | Mixamo, Quaternius     | OpenGameArt          |
| UI/sprites/icons                   | Kenney, itch.io        | OpenGameArt          |
| Niche object matching a screenshot | Sketchfab, OpenGameArt | itch.io, Poly Haven  |

## Red Flags

- Asset names containing famous game/movie/anime/franchise names.
- "Free download" pages that are mirrors, scrapers, or reposts without original author/license.
- Missing license, "personal use only", "editorial use only", or "do not redistribute" terms.
- Marketplace previews where source files are not actually downloadable.
- High-poly scan models with no LODs for mobile/runtime use.
- Rigged assets with no skeleton details or animation preview.
- Texture/material packs without PBR map details when PBR is required.

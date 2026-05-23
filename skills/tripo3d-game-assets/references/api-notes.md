# Tripo3D API Notes

These notes summarize the official Tripo OpenAPI docs researched on 2026-05-23. If an API response contradicts this file, re-open the current docs and update the skill.

## Base request model

- Base URL: `https://api.tripo3d.ai/v2/openapi`
- Auth header: `Authorization: Bearer <TRIPO_API_KEY>`
- Submit most tasks with `POST /task`.
- Query results with `GET /task/{task_id}` using the same API key that created the task.
- Successful API responses use `code: 0`; errors include `code`, `message`, and `suggestion`.
- Every response includes `X-Tripo-Trace-ID`; log it for debugging and support.

## Task lifecycle

Ongoing statuses:

- `queued`
- `running`

Final statuses:

- `success`
- `failed`
- `banned`
- `expired`
- `cancelled`
- `unknown`

Common output fields include:

- `model`
- `base_model`
- `pbr_model`
- `generated_image`
- `rendered_image`
- `generate_multiview_image.front_view_url`
- `generate_multiview_image.left_view_url`
- `generate_multiview_image.back_view_url`
- `generate_multiview_image.right_view_url`

The docs say result download URLs expire quickly, typically after five minutes. Download immediately after success.

## Upload options

- Direct quick upload accepts images only: WebP, JPEG, PNG, max 20 MB.
- STS upload is the recommended upload route for image files and model files.
- File objects generally accept exactly one of `file_token`, `url`, or `object`.
- The `object` form uses `{ "bucket": "tripo-data", "key": "<resource_uri>" }`.
- `import_model` uses model files and requires the model itself to be under 150 MB.

## Main task map

| Need | Task type | Current preferred version | Notes |
| --- | --- | --- | --- |
| Basic image from text | `text_to_image` | versionless | Cheap draft image generation. |
| Advanced image/reference edit | `generate_image` | default or explicit image model | Supports templates such as `asset_extraction`, `character_completion`, `t_pose`, `head_extraction`, `3d_enhance`, `variants`, `print_clay`, `figure`. |
| Generate four views from one image | `generate_multiview_image` | versionless | Concurrency limit is low; use before `multiview_to_model`. |
| Edit generated views | `edit_multiview_image` | versionless | Edits view-specific prompts: `front`, `left`, `back`, `right`. |
| Text to 3D low-poly | `text_to_model` | `P1-20260311` | Stronger low-poly topology; `face_limit` range 48-20000. |
| Text to 3D high fidelity | `text_to_model` | `v3.1-20260211` or `v3.0-20250812` | H3 line with advanced geometry and texture controls. |
| Single image to 3D | `image_to_model` | P1 or H3 | H3 for fidelity, P1 for low-poly structured mesh. |
| Multiview to 3D | `multiview_to_model` | P1 or H3 | File order is `[front, left, back, right]`; front required; at least two views. |
| Existing model into pipeline | `import_model` | versionless | Use for downstream texture, mesh editing, animation, conversion. |
| Re-texture/PBR | `texture_model` | `v3.0-20250812` | Previous model task must be Turbo-v1.0 or over v2.0 generation. |
| Segment mesh into parts | `mesh_segmentation` | `v1.0-20250506` | Produces part names for selective workflows. |
| Complete segmented mesh | `mesh_completion` | `v1.0-20250506` on linked page; overview advertises newer P-v2 | Run after segmentation; verify current docs before selecting P-v2. |
| Smart low-poly | `highpoly_to_lowpoly` | `P-v2.0-20251225` | Face limit 500-20000; 500-10000 for quad. |
| Pre-rig validation | `animate_prerigcheck` | v2 current | Returns `riggable` and `rig_type`. |
| Auto rig | `animate_rig` | `v2.5-20260210` | `out_format` is `glb` or `fbx`; `spec` is `tripo` or `mixamo`. |
| Retarget animation | `animate_retarget` | versionless | Preset motions; one `animation` or up to five `animations`. |
| Convert/export | `convert_model` | versionless | GLTF, USDZ, FBX, OBJ, STL, 3MF. |

## Important parameters

Generation:

- `model_seed`: repeatable geometry seed for v2.0+ and Turbo-v1.0+.
- `texture_seed`: repeatable texture seed for v2.0+ and Turbo-v1.0+.
- `face_limit`: target/maximum face count; exact range depends on task/version.
- `texture`: default `true`; `false` saves credits on untextured drafts.
- `pbr`: default `true`; if `true`, texture is effectively enabled.
- `texture_quality`: `standard` or `detailed`; detailed costs more.
- `geometry_quality`: `standard` or `detailed` in H3.
- `smart_low_poly`: H3 direct low-poly generation; better for less complex inputs.
- `quad`: enables quad output and forces FBX in H3 generation.
- `generate_parts`: creates segmented editable parts, but is incompatible with texture/PBR/quad.
- `auto_size`: real-world scaling in meters; only for textured models.
- `export_uv=false`: speeds generation and defers UV unwrapping to texturing.

Texture:

- `texture_prompt.text`, `texture_prompt.image`, and `texture_prompt.images` are mutually exclusive.
- `texture_prompt.style_image` can guide style.
- `part_names` targets segmented parts.
- `bake=true` combines advanced material effects into base textures.

Animation:

- Pre-rig `rig_type` values include `biped`, `quadruped`, `hexapod`, `octopod`, `avian`, `serpentine`, and `aquatic`.
- Retarget presets include `preset:idle`, `preset:walk`, `preset:run`, `preset:dive`, `preset:climb`, `preset:jump`, `preset:slash`, `preset:shoot`, `preset:hurt`, `preset:fall`, `preset:turn`, `preset:quadruped:walk`, `preset:hexapod:walk`, `preset:octopod:walk`, `preset:serpentine:march`, and `preset:aquatic:march`.

Conversion:

- `pivot_to_center_bottom=true` is useful for game placement.
- `texture_size` can reduce texture resolution for runtime budgets.
- `texture_format=PNG` is the default for FBX and is Unity-friendly.
- `with_animation=true` includes skeletal/animation structure where supported.
- `pack_uv=true` packs parts into one UV layout and single texture map.
- `export_orientation` supports `+x`, `-x`, `-y`, `+y`.
- `fbx_preset` supports `blender`, `3dsmax`, `mixamo`.

## Rate limits and backoff

Tripo uses concurrency limits by task group, not just raw task type.

- P1 text/image/multiview model generation: 5 concurrent tasks.
- Other text/image/multiview model generation: 10 concurrent tasks.
- `refine_model`: 5 concurrent tasks.
- Animation tasks: 10 concurrent tasks.
- `generate_multiview_image` and `edit_multiview_image`: 1 concurrent task.
- Other task types: 10 concurrent tasks.
- Image upload has a 10 QPS limit.

When the API returns code `2000` or HTTP 429, use the `Retry-After` header when present and exponential backoff otherwise.

## Common errors

- `1002`: authentication failed.
- `1004`: invalid parameter.
- `1007`: too many requests in a short time.
- `2000`: exceeded generation concurrency limit.
- `2001`: task not found, often wrong task id or different API key.
- `2004`: unsupported image type.
- `2005`, `2006`, `2007`: upstream/original task is not valid or not successful.
- `2008`: content policy rejection.
- `2010`: insufficient credits.
- `2011`: pre-rig check task lacks model.
- `2012`: input is not a rig task.
- `2015`, `2016`, `2017`: deprecated or invalid version/type; re-check docs.
- `2018`: model too complex to remesh.
- `2019`: uploaded file not found.

## Official docs used

- Introduction: `https://docs.tripo3d.ai/get-started/introduction.html`
- Quick start/auth: `https://docs.tripo3d.ai/get-started/quick-start.html`
- Overview: `https://docs.tripo3d.ai/get-started/overview.html`
- Task query: `https://docs.tripo3d.ai/task-query/get-your-task-result.html`
- Upload docs: `https://docs.tripo3d.ai/file-upload/upload-in-sts.html`, `https://docs.tripo3d.ai/file-upload/quick-upload-directly.html`
- Generation docs: `https://docs.tripo3d.ai/model-generation/text-to-model-p1-20260311.html`, `https://docs.tripo3d.ai/model-generation/text-to-model-v3-0-v3-1.html`, `https://docs.tripo3d.ai/model-generation/image-to-model-p1-20260311.html`, `https://docs.tripo3d.ai/model-generation/image-to-model-v3-0-v3-1.html`, `https://docs.tripo3d.ai/model-generation/multiview-to-model-v3-0-v3-1.html`
- Texture docs: `https://docs.tripo3d.ai/texture/texture-model-v3-0-20250812.html`
- Mesh docs: `https://docs.tripo3d.ai/mesh-editing/mesh-segmentation-v1-0-20250506.html`, `https://docs.tripo3d.ai/mesh-editing/mesh-completion-v1-0-20250506.html`, `https://docs.tripo3d.ai/mesh-editing/smart-low-poly-p-v2-0-20251225.html`
- Animation docs: `https://docs.tripo3d.ai/animation/pre-rig-check-v2-0-20250506.html`, `https://docs.tripo3d.ai/animation/rig-v2-5-20260210.html`, `https://docs.tripo3d.ai/animation/retarget.html`
- Conversion docs: `https://docs.tripo3d.ai/export/conversion.html`
- Official SDK: `https://github.com/VAST-AI-Research/tripo-python-sdk`

# Payload Recipes

All payloads below are submitted to `POST https://api.tripo3d.ai/v2/openapi/task`.
Save each payload next to the generated asset before submitting it.

Image policy for gamekit: do not use Tripo image-generation tasks. If an input image needs to be created, cleaned, restyled, completed, converted to T-pose, or expanded into multiview references, use `skills/game-asset-imagegen/SKILL.md`, save the image output in the workspace, then upload or reference it in an `image_to_model` or `multiview_to_model` payload.

## Smart Mesh P1 low-poly prop from text

Use for collectibles, weapons, furniture, small environment props, mobile assets, and drafts where clean topology matters more than maximum detail. This is the preferred API route when the user explicitly asks for Smart Mesh, P1, structured topology, or real-time game mesh output.

```json
{
  "type": "text_to_model",
  "prompt": "A stylized low-poly fantasy wooden treasure chest, readable silhouette, game prop, no text, no logo",
  "negative_prompt": "blurry, melted, broken hinges, unreadable shape",
  "model_version": "P1-20260311",
  "face_limit": 6000,
  "texture": true,
  "pbr": true,
  "auto_size": true,
  "model_seed": 12345,
  "texture_seed": 67890
}
```

## H3 direct smart low-poly generation

Use when the user needs H3 prompt fidelity or advanced controls but still wants low-poly hand-crafted topology. Keep the input less complex and set an explicit `face_limit`.

```json
{
  "type": "text_to_model",
  "prompt": "A stylized fantasy blacksmith workstation with an anvil, tools, and warm glowing forge details, readable game prop silhouette, no text",
  "negative_prompt": "blurry, noisy, watermark, labels, excessive tiny parts",
  "model_version": "v3.1-20260211",
  "texture": true,
  "pbr": true,
  "geometry_quality": "standard",
  "texture_quality": "standard",
  "smart_low_poly": true,
  "face_limit": 12000,
  "auto_size": true,
  "export_uv": true
}
```

## High-fidelity model from text

Use for hero props, larger environment pieces, or assets where fidelity matters. Start with standard quality, then pay for detailed modes only after the draft shape is approved.

```json
{
  "type": "text_to_model",
  "prompt": "A high-fidelity stylized sci-fi generator core for a third-person action game, clean readable shape, emissive blue panels, no text",
  "negative_prompt": "flat image, blurry, noisy, watermark, labels",
  "model_version": "v3.1-20260211",
  "texture": true,
  "pbr": true,
  "geometry_quality": "standard",
  "texture_quality": "standard",
  "face_limit": 50000,
  "auto_size": true,
  "export_uv": true
}
```

## Single image to model

Use `object` when you uploaded through STS. Use `file_token` for direct image upload. Use `url` only for public image URLs.

```json
{
  "type": "image_to_model",
  "file": {
    "type": "png",
    "object": {
      "bucket": "tripo-data",
      "key": "uploads/example_reference.png"
    }
  },
  "model_version": "v3.1-20260211",
  "texture": true,
  "pbr": true,
  "enable_image_autofix": true,
  "texture_alignment": "geometry",
  "orientation": "align_image",
  "geometry_quality": "standard"
}
```

## Prepare a riggable character reference with game-asset-imagegen

Run this before 3D generation when a character is not in a clean rigging pose. This is not a Tripo payload; it is prompt guidance for `game-asset-imagegen`.

```text
Use case: reference-guided generation
Asset type: character reference for 3D model generation
Primary request: Convert the provided character concept into a clean full-body T-pose or A-pose reference suitable for Tripo image_to_model.
Input images: Image 1 is the identity/costume reference.
Composition/framing: full body, front view, symmetrical neutral stance, arms clear of torso, feet visible, centered.
Transparency/background: plain flat background.
Constraints: preserve costume, colors, facial identity, proportions, and silhouette. No text, labels, logo, watermark, or cropped limbs.
```

Save the final PNG under the asset pack, upload/reference it, then use it in `image_to_model`.

## Multiview references from game-asset-imagegen, then model

Step 1: use `game-asset-imagegen` to create or clean a four-view turnaround. This is not a Tripo image-generation task.

```text
Use case: reference-guided generation
Asset type: four-view turnaround sheet for 3D model generation
Primary request: Create front, left, back, and right orthographic views of the same asset for Tripo multiview_to_model.
Composition/framing: four separate clean images or a clearly separable 4-cell sheet, consistent scale, consistent lighting, neutral pose.
Constraints: preserve identity across views. No perspective camera, labels, text, shadows crossing cells, decorative borders, logo, or watermark.
```

Step 2: upload/reference the resulting front/left/back/right images, then model from direct file inputs.

```json
{
  "type": "multiview_to_model",
  "files": [
    {
      "type": "png",
      "object": {
        "bucket": "tripo-data",
        "key": "uploads/asset_front.png"
      }
    },
    {
      "type": "png",
      "object": {
        "bucket": "tripo-data",
        "key": "uploads/asset_left.png"
      }
    },
    {
      "type": "png",
      "object": {
        "bucket": "tripo-data",
        "key": "uploads/asset_back.png"
      }
    },
    {
      "type": "png",
      "object": {
        "bucket": "tripo-data",
        "key": "uploads/asset_right.png"
      }
    }
  ],
  "model_version": "v3.1-20260211",
  "texture": true,
  "pbr": true,
  "texture_alignment": "geometry",
  "geometry_quality": "standard"
}
```

If supplying images directly, use exactly four file entries in `[front, left, back, right]` order. You may omit a non-front view by omitting its token/object/url, but do not use fewer than two images.

## Direct low-poly post-process

Use after H3/P1/imported model generation when you need a strict game mesh budget.

```json
{
  "type": "highpoly_to_lowpoly",
  "original_model_task_id": "<source_model_task_id>",
  "model_version": "P-v2.0-20251225",
  "face_limit": 8000,
  "quad": false,
  "bake": true
}
```

If Tripo rejects `P-v2.0-20251225`, re-check the current Smart Low Poly docs and use the currently documented `model_version`.

## Segment, edit parts, complete

Step 1: segment the model and save part names from the result.

```json
{
  "type": "mesh_segmentation",
  "original_model_task_id": "<source_model_task_id>",
  "model_version": "v1.0-20250506"
}
```

Step 2: retexture selected parts.

```json
{
  "type": "texture_model",
  "original_model_task_id": "<segmented_or_source_model_task_id>",
  "model_version": "v3.0-20250812",
  "texture_prompt": {
    "text": "dark worn steel with bright orange edge glow, stylized game material"
  },
  "part_names": ["blade", "guard"],
  "texture": true,
  "pbr": true,
  "texture_quality": "standard",
  "texture_alignment": "geometry",
  "bake": true
}
```

Step 3: complete the selected segmented parts when needed.

```json
{
  "type": "mesh_completion",
  "original_model_task_id": "<segmented_model_task_id>",
  "model_version": "v1.0-20250506",
  "part_names": ["left_arm", "right_arm"]
}
```

The overview page advertises a newer mesh completion model. If the linked task page exposes a newer version, prefer the newer version and update this recipe.

## Texture an existing model task

Use this when shape is approved but material direction changes.

```json
{
  "type": "texture_model",
  "original_model_task_id": "<source_model_task_id>",
  "model_version": "v3.0-20250812",
  "texture_prompt": {
    "text": "hand-painted stylized mossy stone, warm highlights, readable at small size"
  },
  "texture": true,
  "pbr": true,
  "texture_seed": 24680,
  "texture_quality": "standard",
  "texture_alignment": "geometry",
  "bake": true
}
```

## Rig and retarget

Step 1: pre-rig check.

```json
{
  "type": "animate_prerigcheck",
  "original_model_task_id": "<source_model_task_id>"
}
```

Step 2: rig with the returned or expected rig type.

```json
{
  "type": "animate_rig",
  "original_model_task_id": "<source_model_task_id>",
  "model_version": "v2.5-20260210",
  "out_format": "glb",
  "rig_type": "biped",
  "spec": "tripo"
}
```

Step 3: apply up to five preset animations.

```json
{
  "type": "animate_retarget",
  "original_model_task_id": "<rig_task_id>",
  "out_format": "glb",
  "animations": ["preset:idle", "preset:walk", "preset:run"],
  "animate_in_place": true,
  "bake_animation": true,
  "export_with_geometry": true
}
```

## Convert for engine import

Godot/web preview GLB:

```json
{
  "type": "convert_model",
  "original_model_task_id": "<source_or_animated_task_id>",
  "format": "GLTF",
  "face_limit": 12000,
  "texture_size": 2048,
  "texture_format": "PNG",
  "pivot_to_center_bottom": true,
  "with_animation": true,
  "pack_uv": true,
  "bake": true,
  "export_orientation": "+x"
}
```

Unity/Unreal FBX:

```json
{
  "type": "convert_model",
  "original_model_task_id": "<source_or_animated_task_id>",
  "format": "FBX",
  "texture_size": 2048,
  "texture_format": "PNG",
  "pivot_to_center_bottom": true,
  "with_animation": true,
  "bake": true,
  "fbx_preset": "blender"
}
```

Do not use OBJ, STL, or 3MF for rigged models. Do not use STL if textures matter.

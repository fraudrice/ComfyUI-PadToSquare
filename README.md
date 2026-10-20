# ComfyUI-PadToSquare

A ComfyUI node that pads an image to a square by extending its shorter side, keeping the image centered.

## Pad Image To Square

Found under **image → transform**.

**Inputs**

| Name | Type | Description |
|---|---|---|
| `image` | IMAGE | Image (or batch) to pad. |
| `longest_side` | INT, optional | Resize so the longest side equals this before padding. `0` keeps the original size. |
| `upscale_method` | choice, optional | Resampling used when resizing: `lanczos` (default), `bicubic`, `bilinear`, `area`, `nearest-exact`. |

**Outputs**

| Name | Type | Description |
|---|---|---|
| `image` | IMAGE | The square image, padded with black. |
| `inverted_mask` | MASK | `1` over the original image area, `0` over the padding. |

## Getting the original image back

Connect the padded image and `inverted_mask` to KJNodes' **Image Crop By Mask** to cut the image back out of the square.
If a node in between changes the image size, resize the mask by the same factor first so the crop box lines up.

## Install

```bash
cd ComfyUI/custom_nodes
git clone https://codeberg.org/friedrice/ComfyUI-PadToSquare.git
```

Restart ComfyUI. There are no extra dependencies.

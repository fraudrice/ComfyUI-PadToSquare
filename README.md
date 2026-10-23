# ComfyUI-PadToSquare

ComfyUI nodes to pad an image to a square by extending its shorter side, keeping the image centered,
and to crop the original image back out afterwards.

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

## Crop Image By Mask (PadToSquare)

Found under **image → transform**. Crops an image to the bounding box of a mask, so connecting the
padded image and `inverted_mask` cuts the original image back out of the square.

If a node in between changes the image size, connect the mask unchanged: the crop box is scaled from
the mask's size to the image's size, so it still lines up.

**Inputs**

| Name | Type | Description |
|---|---|---|
| `image` | IMAGE | Image (or batch) to crop. |
| `mask` | MASK | Mask whose area above `0.5` sets the crop box. An empty mask leaves the image uncropped. |

**Outputs**

| Name | Type | Description |
|---|---|---|
| `image` | IMAGE | The cropped image. |

This node is modelled on **Image Crop By Mask** from [KJNodes](https://github.com/kijai/ComfyUI-KJNodes)
by kijai, which works as a drop-in alternative. It is a separate implementation, not a copy of KJNodes' code.

## Install

```bash
cd ComfyUI/custom_nodes
git clone https://github.com/fraudrice/ComfyUI-PadToSquare.git
```

Restart ComfyUI. There are no extra dependencies.

## License

MIT. See [LICENSE](LICENSE).

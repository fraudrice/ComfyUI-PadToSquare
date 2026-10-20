import torch

import comfy.utils


class PadImageToSquare:
    """
    Pads the shorter side of an image so it becomes square, keeping the image centered.
    If longest_side is set, the image is first resized so its longest side equals it.
    Also returns a mask that is 1 over the original image and 0 over the padding, which
    "Image Crop By Mask" can use to cut the original image back out.
    """

    upscale_methods = ["lanczos", "bicubic", "bilinear", "area", "nearest-exact"]

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "image": ("IMAGE",),
            },
            "optional": {
                "longest_side": ("INT", {
                    "default": 0, "min": 0, "max": 16384, "step": 1,
                    "tooltip": "Resize so the longest side equals this before padding. 0 keeps the original size.",
                }),
                "upscale_method": (s.upscale_methods, {"default": "lanczos"}),
            },
        }

    RETURN_TYPES = ("IMAGE", "MASK")
    RETURN_NAMES = ("image", "inverted_mask")
    OUTPUT_TOOLTIPS = (
        "The square, padded image.",
        "1 over the original image area, 0 over the padding.",
    )
    FUNCTION = "pad"
    CATEGORY = "image/transform"
    DESCRIPTION = "Pads an image to a square, optionally resizing it so its longest side matches a given size."

    def pad(self, image, longest_side=0, upscale_method="lanczos"):
        batch, height, width, channels = image.shape

        if longest_side > 0 and max(height, width) != longest_side:
            scale = longest_side / max(height, width)
            width = max(1, round(width * scale))
            height = max(1, round(height * scale))
            image = comfy.utils.common_upscale(
                image.movedim(-1, 1), width, height, upscale_method, "disabled"
            ).movedim(1, -1)

        size = max(height, width)
        top = (size - height) // 2
        left = (size - width) // 2

        padded = torch.zeros((batch, size, size, channels), dtype=image.dtype, device=image.device)
        padded[:, top:top + height, left:left + width, :] = image

        mask = torch.zeros((batch, size, size), dtype=torch.float32, device=image.device)
        mask[:, top:top + height, left:left + width] = 1.0

        return (padded, mask)


NODE_CLASS_MAPPINGS = {
    "PadImageToSquare": PadImageToSquare,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "PadImageToSquare": "Pad Image To Square",
}

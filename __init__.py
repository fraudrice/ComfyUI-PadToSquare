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


class CropImageByMask:
    """
    Crops an image to the bounding box of a mask, e.g. the inverted_mask from Pad Image To Square,
    to cut the original image back out of the square. Modelled on KJNodes' Image Crop By Mask
    (https://github.com/kijai/ComfyUI-KJNodes). If the mask and image differ in size, the box is
    scaled to the image, so the image can be resized between padding and cropping.
    """

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "image": ("IMAGE",),
                "mask": ("MASK",),
            },
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)
    OUTPUT_TOOLTIPS = ("The image cropped to the area where the mask is above 0.5.",)
    FUNCTION = "crop"
    CATEGORY = "image/transform"
    DESCRIPTION = "Crops an image to the bounding box of a mask, scaling the box if the mask and image sizes differ."

    def crop(self, image, mask):
        batch, height, width, _ = image.shape
        if mask.dim() == 2:
            mask = mask.unsqueeze(0)
        mask_height, mask_width = mask.shape[-2:]

        crops = []
        for i in range(batch):
            area = mask[min(i, mask.shape[0] - 1)] > 0.5
            rows = torch.nonzero(area.any(dim=1)).flatten()
            cols = torch.nonzero(area.any(dim=0)).flatten()
            if rows.numel() == 0:
                # Empty mask: nothing to crop to, keep the whole image.
                crops.append(image[i])
                continue

            top = round(rows[0].item() * height / mask_height)
            bottom = round((rows[-1].item() + 1) * height / mask_height)
            left = round(cols[0].item() * width / mask_width)
            right = round((cols[-1].item() + 1) * width / mask_width)
            crops.append(image[i, top:bottom, left:right, :])

        if any(crop.shape != crops[0].shape for crop in crops):
            raise ValueError("Masks in the batch produce crops of different sizes, which cannot be batched together.")

        return (torch.stack(crops),)


NODE_CLASS_MAPPINGS = {
    "PadImageToSquare": PadImageToSquare,
    "PadToSquareCropByMask": CropImageByMask,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "PadImageToSquare": "Pad Image To Square",
    "PadToSquareCropByMask": "Crop Image By Mask (PadToSquare)",
}

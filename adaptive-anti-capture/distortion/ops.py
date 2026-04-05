import cv2
import numpy as np


def pixelate(region, pixel_size: int):
    h, w = region.shape[:2]
    small_w = max(1, w // pixel_size)
    small_h = max(1, h // pixel_size)
    small = cv2.resize(region, (small_w, small_h), interpolation=cv2.INTER_LINEAR)
    return cv2.resize(small, (w, h), interpolation=cv2.INTER_NEAREST)


def mask_block(region, ratio: float = 0.2):
    out = region.copy()
    h, w = out.shape[:2]
    mask_h = max(1, int(h * ratio))
    mask_w = max(1, int(w * ratio))
    y = max(0, (h - mask_h) // 2)
    x = max(0, (w - mask_w) // 2)
    out[y:y + mask_h, x:x + mask_w] = 0
    return out


def flicker(region):
    noise = np.random.randint(0, 32, region.shape, dtype=np.uint8)
    return cv2.add(region, noise)

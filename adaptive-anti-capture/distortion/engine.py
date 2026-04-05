from .ops import pixelate, mask_block, flicker


def distort(frame, boxes, level="medium", cfg=None):
    cfg = cfg or {}
    for (x1, y1, x2, y2) in boxes:
        roi = frame[y1:y2, x1:x2]
        if roi.size == 0:
            continue

        if level == "low":
            roi = pixelate(roi, cfg.get("low_pixel_size", 16))
        elif level == "medium":
            roi = pixelate(roi, cfg.get("medium_pixel_size", 10))
            roi = mask_block(roi, cfg.get("medium_mask_ratio", 0.20))
        else:
            roi = pixelate(roi, cfg.get("high_pixel_size", 6))
            roi = mask_block(roi, cfg.get("high_mask_ratio", 0.40))
            roi = flicker(roi)

        frame[y1:y2, x1:x2] = roi
    return frame

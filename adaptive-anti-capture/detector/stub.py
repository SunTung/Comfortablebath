def detect_regions(frame):
    """Return a simple central box as a placeholder sensitive region."""
    h, w, _ = frame.shape
    return [(int(w * 0.30), int(h * 0.30), int(w * 0.70), int(h * 0.60))]

import time
import cv2
import numpy as np
import mss
import yaml

from detector.stub import detect_regions
from distortion.engine import distort
from risk.scorer import RiskScorer
from ui.overlay import show


def load_config(path: str = "adaptive-anti-capture/config.yaml"):
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def main():
    cfg = load_config()
    scorer = RiskScorer(
        increase_on_suspected=cfg["risk"]["increase_on_suspected"],
        decay_idle=cfg["risk"]["decay_idle"],
        medium_threshold=cfg["risk"]["medium_threshold"],
        high_threshold=cfg["risk"]["high_threshold"],
    )

    with mss.mss() as sct:
        monitor = sct.monitors[1]

        while True:
            raw = np.array(sct.grab(monitor))
            frame = cv2.cvtColor(raw, cv2.COLOR_BGRA2BGR)

            suspected = cfg["capture"]["suspected_default"]
            boxes = detect_regions(frame) if suspected else []
            frame = distort(frame, boxes, level=scorer.current_level(), cfg=cfg["distortion"])
            score = scorer.update(suspected=suspected)

            show(frame, info=f"risk={score} level={scorer.current_level()}")

            key = cv2.waitKey(1) & 0xFF
            if key == 27:
                break
            if key == ord('t'):
                cfg["capture"]["suspected_default"] = not cfg["capture"]["suspected_default"]

    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()

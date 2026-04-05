import cv2
import numpy as np
import mss
import yaml

from detector.stub import detect_regions
from distortion.engine import distort
from risk.scorer import RiskScorer


def load_config(path: str = "adaptive-anti-capture/config.yaml"):
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def draw_boxes(frame, boxes):
    out = frame.copy()
    for x1, y1, x2, y2 in boxes:
        cv2.rectangle(out, (x1, y1), (x2, y2), (0, 255, 255), 2)
    return out


def main():
    cfg = load_config()
    suspected = cfg["capture"]["suspected_default"]
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
            boxes = detect_regions(frame) if suspected else []
            protected = distort(frame.copy(), boxes, level=scorer.current_level(), cfg=cfg["distortion"])
            preview = draw_boxes(protected, boxes)
            score = scorer.update(suspected=suspected)

            cv2.putText(preview, f"risk={score} level={scorer.current_level()} suspected={suspected}", (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 255, 255), 2, cv2.LINE_AA)
            cv2.putText(preview, "ESC exit | T toggle suspected", (20, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (220, 220, 220), 1, cv2.LINE_AA)
            cv2.imshow("Adaptive Anti-Capture Demo", preview)

            key = cv2.waitKey(1) & 0xFF
            if key == 27:
                break
            if key == ord('t'):
                suspected = not suspected

    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()

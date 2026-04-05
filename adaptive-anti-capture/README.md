# Adaptive Anti-Capture Prototype

A concept prototype for **display-layer information protection**.

This project demonstrates a defensive pipeline:

`Capture -> Detect sensitive regions -> Distort locally -> Score risk -> Adjust`

## Goals

- Protect high-value screen regions instead of damaging the full screen
- Degrade information usability during suspected capture events
- Keep the architecture pluggable so organizations can train their own models

## Non-goals

- This is **not** a full anti-malware product
- This repo does **not** ship a production detection model
- This repo does **not** provide stealthy system-wide interference tooling

## Structure

- `app.py`: runnable demo entry point
- `config.yaml`: simple thresholds and distortion settings
- `detector/stub.py`: placeholder detector
- `distortion/`: local distortion engine
- `risk/scorer.py`: lightweight risk scoring logic
- `ui/overlay.py`: simple annotated preview window

## Run

```bash
pip install -r requirements.txt
python adaptive-anti-capture/app.py
```

Press `ESC` to exit.

## Future work

- Replace stub detector with a custom lightweight region detector
- Add application-specific UI-tree or DOM signals
- Integrate external risk signals from endpoint security tools
- Benchmark OCR degradation and latency

## Safety note

This prototype is intended for **defensive research, teaching, and authorized internal integration** only.
Model weights for high-precision sensitive-region detection are intentionally not included.

# Architecture

## Pipeline

1. Capture current frame
2. Detect sensitive regions using a pluggable detector
3. Apply local distortion to the detected regions
4. Update a lightweight risk score
5. Adjust distortion level according to current risk

## Design goals

- Prefer local distortion over full-screen corruption
- Keep the detection layer replaceable
- Keep the risk logic simple and auditable in the prototype
- Leave high-precision model training to downstream integrators

## Prototype limits

- Uses a stub detector by default
- Does not include trained model weights
- Does not implement platform-specific capture-event hooks

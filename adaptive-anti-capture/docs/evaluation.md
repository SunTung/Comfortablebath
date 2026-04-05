# Evaluation

## What to measure

### 1. Latency
- End-to-end frame processing time
- Target: keep the prototype responsive enough for manual testing

### 2. Region quality
- Whether the detector marks the intended sensitive region
- Whether distortion stays local instead of corrupting the whole screen

### 3. Usability degradation
- Compare manual readability before and after distortion
- Optional: measure OCR success rate on protected regions

### 4. False positive cost
- How often the prototype stays in a protected state when it should not
- How disruptive the chosen distortion level is for the user

## Suggested experiments

1. Run the stub detector on multiple window sizes
2. Compare low / medium / high distortion modes
3. Test with short-lived and persistent suspected states
4. Replace the stub detector with a custom detector and compare behavior

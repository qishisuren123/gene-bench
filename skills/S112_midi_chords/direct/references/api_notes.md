# MIDI note number mapping
Note 60 = Middle C (C4)
note % 12 gives pitch class: 0=C, 1=C#, 2=D, ..., 11=B
note // 12 gives octave number (note 60 → octave 5 in scientific pitch)

# Interval computation for chord detection
Given sorted pitch classes [p0, p1, p2, ...]:
intervals = [(p[i+1] - p[i]) % 12 for i in range(len(p)-1)]

# Chord templates (ascending intervals from root)
CHORD_TEMPLATES = {
    "major": [4, 3],
    "minor": [3, 4],
    "diminished": [3, 3],
    "augmented": [4, 4],
    "dominant_7th": [4, 3, 3],
    "major_7th": [4, 3, 4],
    "minor_7th": [3, 4, 3],
    "power": [7],
}

# To handle inversions, try all rotations:
# For pitch classes [0, 4, 7] (C major):
# Rotation 1: [4, 7, 12] → intervals [3, 5] (first inversion)
# Rotation 2: [7, 12, 16] → intervals [5, 4] (second inversion)
# Must check all rotations against templates

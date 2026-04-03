# Example 1: Group MIDI notes into chords
import pandas as pd

df = pd.read_csv('midi_events.csv')
df = df.sort_values('time_ms').reset_index(drop=True)

NOTE_NAMES = ['C','C#','D','D#','E','F','F#','G','G#','A','A#','B']

def group_chords(events, max_gap=50):
    groups = []
    current = [events.iloc[0]]
    for i in range(1, len(events)):
        if events.iloc[i]['time_ms'] - current[-1]['time_ms'] <= max_gap:
            current.append(events.iloc[i])
        else:
            groups.append(current)
            current = [events.iloc[i]]
    groups.append(current)
    return groups

# Example 2: Classify chord from pitch classes
TEMPLATES = {
    "major": [4, 3], "minor": [3, 4],
    "diminished": [3, 3], "augmented": [4, 4],
    "dominant_7th": [4, 3, 3], "major_7th": [4, 3, 4], "minor_7th": [3, 4, 3],
}

def classify_chord(notes):
    pcs = sorted(set(n % 12 for n in notes))
    if len(pcs) < 2:
        return NOTE_NAMES[pcs[0]] if pcs else "rest", "single"
    # Try all rotations to find root position
    for rotation in range(len(pcs)):
        rotated = pcs[rotation:] + [p + 12 for p in pcs[:rotation]]
        intervals = [rotated[i+1] - rotated[i] for i in range(len(rotated)-1)]
        for name, template in TEMPLATES.items():
            if intervals == template:
                root = pcs[rotation]
                return NOTE_NAMES[root], name
    return NOTE_NAMES[pcs[0]], "unknown"

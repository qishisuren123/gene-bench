# MIDI Chord Detection and Classification

## Overview
This skill detects and classifies chords from MIDI note event data by grouping simultaneous notes, analyzing pitch class intervals, and building chord progression sequences with transition matrices.

## Workflow
1. Parse arguments for input CSV, output JSON, min-duration threshold, and max-gap for grouping simultaneous notes
2. Load MIDI events (time_ms, note, velocity, duration_ms, channel), sort by time
3. Group simultaneous notes: collect notes within max_gap ms of each other into chord candidates
4. For each chord group: extract pitch classes (note % 12), sort them, compute ascending intervals between consecutive pitch classes
5. Match interval pattern against chord templates (major, minor, diminished, augmented, seventh chords)
6. Name each chord using root note + type (e.g., "C major", "A minor 7th")
7. Build transition matrix counting sequential chord-type pairs
8. Estimate key signature by counting pitch class frequency and matching against major/minor scale templates

## Common Pitfalls
- **Pitch class extraction**: MIDI note numbers are absolute (0-127); must use `note % 12` to get pitch class, NOT treat as frequency
- **Chord inversions**: Notes [E4, G4, C5] and [C4, E4, G4] are both C major — must normalize to root position by trying all rotations of the pitch class set
- **Timing tolerance**: Notes rarely arrive at exactly the same time in MIDI; use max_gap window (e.g., 50ms) for grouping
- **Duplicate pitch classes**: Multiple notes of the same pitch class (octave doublings) should be collapsed before interval analysis
- **Empty chord groups**: After filtering by min-duration, some groups may have 0-1 notes; handle as "rest" or "single note"

## Error Handling
- Handle MIDI files with no note-on events gracefully
- Validate note range (0-127) and velocity range (0-127)
- Handle case where no chords are detected (all single notes)
- Ensure transition matrix handles unknown/unclassified chord types

## Quick Reference
- Pitch class: `pc = note % 12` (C=0, C#=1, ..., B=11)
- Note names: `['C','C#','D','D#','E','F','F#','G','G#','A','A#','B']`
- Major triad intervals: [4, 3] semitones from root
- Minor triad: [3, 4], Diminished: [3, 3], Augmented: [4, 4]
- Dominant 7th: [4, 3, 3], Major 7th: [4, 3, 4], Minor 7th: [3, 4, 3]

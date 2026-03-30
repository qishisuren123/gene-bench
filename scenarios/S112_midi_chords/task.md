Write a Python CLI script that detects and classifies chords from MIDI file data.

Input: A CSV file representing MIDI note events with columns: time_ms, note (MIDI number 0-127), velocity, duration_ms, channel.

Requirements:
1. Use argparse: --input CSV, --output JSON, --min-duration (default 100ms), --max-gap (default 50ms for simultaneous notes)
2. Load MIDI events and sort by time
3. Group simultaneous notes: notes within max_gap ms of each other form a chord
4. For each chord group, determine the chord type by analyzing intervals:
   - Major triad: intervals [4, 3] semitones (e.g., C-E-G)
   - Minor triad: intervals [3, 4] (e.g., C-Eb-G)
   - Diminished: intervals [3, 3]
   - Augmented: intervals [4, 4]
   - Seventh chords: [4, 3, 4] (major 7th), [4, 3, 3] (dominant 7th), [3, 4, 3] (minor 7th)
   - Power chord: interval [7]
   - Single note: no chord
5. Name chords using root note + type (e.g., "C major", "A minor 7th")
6. Compute chord progression and transition frequency matrix
7. Output JSON: n_events, n_chords, chord_sequence (list of {time_ms, notes, chord_name, root, type}), transition_matrix, key_signature_guess
8. Print summary: most common chord, chord diversity, estimated key

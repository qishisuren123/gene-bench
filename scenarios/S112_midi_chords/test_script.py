import sys, os, json, subprocess, tempfile

def create_test_csv(path):
    """创建 C major 调性的和弦进行: C-Am-F-G"""
    events = []
    t = 0
    # C major: C4(60), E4(64), G4(67)
    for note in [60, 64, 67]:
        events.append((t, note, 80, 400, 0))
    t += 500
    # A minor: A3(57), C4(60), E4(64)
    for note in [57, 60, 64]:
        events.append((t, note, 75, 400, 0))
    t += 500
    # F major: F3(53), A3(57), C4(60)
    for note in [53, 57, 60]:
        events.append((t, note, 85, 400, 0))
    t += 500
    # G major: G3(55), B3(59), D4(62)
    for note in [55, 59, 62]:
        events.append((t, note, 70, 400, 0))
    t += 500
    # G7 (dominant 7th): G3(55), B3(59), D4(62), F4(65)
    for note in [55, 59, 62, 65]:
        events.append((t, note, 72, 400, 0))
    t += 500
    # C major again
    for note in [60, 64, 67]:
        events.append((t, note, 80, 400, 0))
    t += 500
    # Single note
    events.append((t, 60, 90, 200, 0))
    t += 300
    # Power chord: C5(72), G5(79)
    for note in [72, 79]:
        events.append((t, note, 85, 400, 0))

    with open(path, "w") as f:
        f.write("time_ms,note,velocity,duration_ms,channel\n")
        for t_ms, note, vel, dur, ch in events:
            f.write(f"{t_ms},{note},{vel},{dur},{ch}\n")

with tempfile.TemporaryDirectory() as tmpdir:
    csv_path = f"{tmpdir}/midi.csv"
    out_json = f"{tmpdir}/chords.json"
    create_test_csv(csv_path)

    ran = False
    for args in [
        [sys.executable, "solution.py", "--input", csv_path, "--output", out_json],
        [sys.executable, "solution.py", "--input", csv_path, "--output", out_json, "--min-duration", "100", "--max-gap", "50"],
    ]:
        r = subprocess.run(args, capture_output=True, text=True, timeout=60, cwd=os.getcwd())
        if r.returncode == 0 or os.path.exists(out_json):
            ran = True
            break

    print(f"{'PASS' if ran else 'FAIL'}:L1_runs")
    if not os.path.exists(out_json):
        print("FAIL:L1_output_exists")
        for t in ["L1_valid_json","L2_has_chords","L2_chord_count","L2_c_major_detected","L2_minor_detected","L2_has_root","L2_has_transition","L2_seventh_detected","L2_has_key"]:
            print(f"FAIL:{t}")
        sys.exit(0)
    print("PASS:L1_output_exists")

    try:
        with open(out_json) as f:
            results = json.load(f)
        print("PASS:L1_valid_json")
    except:
        print("FAIL:L1_valid_json")
        sys.exit(0)

    chord_seq = results.get("chord_sequence", results.get("chords", []))
    if isinstance(chord_seq, list) and len(chord_seq) >= 4:
        print(f"PASS:L2_has_chords - {len(chord_seq)}")
    else:
        print(f"FAIL:L2_has_chords - {len(chord_seq) if isinstance(chord_seq, list) else 0}")

    # 和弦数量 (6-10)
    if 4 <= len(chord_seq) <= 12:
        print(f"PASS:L2_chord_count - {len(chord_seq)}")
    else:
        print(f"FAIL:L2_chord_count - {len(chord_seq)}")

    # 检测到 C major
    chord_names = [str(c.get("chord_name", c.get("name", ""))).lower() for c in chord_seq]
    c_major = any("c" in n and "major" in n and "minor" not in n for n in chord_names)
    if not c_major:
        c_major = any("c" in n and ("maj" in n or "M" in str(c.get("chord_name", c.get("name", "")))) for n, c in zip(chord_names, chord_seq))
    print(f"{'PASS' if c_major else 'FAIL'}:L2_c_major_detected")

    # 检测到 minor
    minor_found = any("minor" in n or "min" in n or "m" in str(c.get("type", "")) for n, c in zip(chord_names, chord_seq))
    print(f"{'PASS' if minor_found else 'FAIL'}:L2_minor_detected")

    # 有 root 字段
    has_root = any("root" in c for c in chord_seq) if chord_seq else False
    print(f"{'PASS' if has_root else 'FAIL'}:L2_has_root")

    # 有 transition matrix
    tm = results.get("transition_matrix", results.get("transitions", None))
    if tm is not None:
        print("PASS:L2_has_transition")
    else:
        print("FAIL:L2_has_transition")

    # 检测到七和弦
    seventh = any("7" in n or "seventh" in n or "dom" in n for n in chord_names)
    print(f"{'PASS' if seventh else 'FAIL'}:L2_seventh_detected")

    # 有 key signature guess
    key = results.get("key_signature_guess", results.get("key", results.get("estimated_key", None)))
    if key is not None:
        print(f"PASS:L2_has_key - {key}")
    else:
        print("FAIL:L2_has_key")

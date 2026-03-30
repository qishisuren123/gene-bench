import sys, os, subprocess, tempfile, csv

def create_test_fasta(path):
    """创建测试 FASTA 文件"""
    with open(path, "w") as f:
        # 富含 alpha-helix 的序列 (AELM repeat)
        f.write(">seq1_helix_rich\n")
        f.write("AELMAELMAELMAELMAELMKKKKAELMAELM\n")
        # 富含 beta-sheet 的序列 (VIY repeat)
        f.write(">seq2_sheet_rich\n")
        f.write("VIYVIYVIYVIYVIYFWLVIYVIYVIYVIY\n")
        # 混合序列
        f.write(">seq3_mixed\n")
        f.write("AELMGGGGVIYVIYGGGGAELMGGGGVIYVIY\n")
        # 短序列
        f.write(">seq4_short\n")
        f.write("ACDEFGHIK\n")

with tempfile.TemporaryDirectory() as tmpdir:
    fasta_path = f"{tmpdir}/test.fasta"
    out_csv = f"{tmpdir}/results.csv"
    create_test_fasta(fasta_path)

    # 尝试运行
    ran = False
    for args in [
        [sys.executable, "solution.py", "--input", fasta_path, "--output", out_csv],
        [sys.executable, "solution.py", "--input", fasta_path, "--output", out_csv, "--method", "chou_fasman"],
        [sys.executable, "solution.py", fasta_path, "--output", out_csv],
    ]:
        r = subprocess.run(args, capture_output=True, text=True, timeout=60, cwd=os.getcwd())
        if r.returncode == 0 or os.path.exists(out_csv):
            ran = True
            break

    if ran or os.path.exists(out_csv):
        print("PASS:L1_runs")
    else:
        print(f"FAIL:L1_runs - {r.stderr[-200:]}")

    if os.path.exists(out_csv):
        print("PASS:L1_output_exists")
    else:
        print("FAIL:L1_output_exists")
        for t in ["L1_valid_csv", "L2_has_sequences", "L2_has_structure", "L2_valid_percentages", "L2_helix_rich_detected", "L2_sheet_rich_detected", "L2_all_residues_assigned", "L2_short_seq_handled"]:
            print(f"FAIL:{t} - no output")
        sys.exit(0)

    # 验证 CSV
    try:
        with open(out_csv) as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        print("PASS:L1_valid_csv")
    except Exception as e:
        print(f"FAIL:L1_valid_csv - {e}")
        for t in ["L2_has_sequences", "L2_has_structure", "L2_valid_percentages", "L2_helix_rich_detected", "L2_sheet_rich_detected", "L2_all_residues_assigned", "L2_short_seq_handled"]:
            print(f"FAIL:{t} - invalid csv")
        sys.exit(0)

    # L2: 有 4 条序列
    if len(rows) >= 4:
        print(f"PASS:L2_has_sequences - {len(rows)} sequences")
    else:
        print(f"FAIL:L2_has_sequences - expected >=4, got {len(rows)}")

    # L2: 有 structure 字符串
    headers_lower = {k.lower(): k for k in rows[0].keys()} if rows else {}
    struct_key = None
    for candidate in ["structure_string", "structure", "ss", "secondary_structure"]:
        if candidate in headers_lower:
            struct_key = headers_lower[candidate]
            break
    if struct_key and any(rows[i].get(struct_key, "") for i in range(min(len(rows), 4))):
        print(f"PASS:L2_has_structure")
    else:
        print(f"FAIL:L2_has_structure - no structure column found")

    # L2: 百分比有效 (0-100)
    pct_keys = []
    for candidate in ["helix_pct", "sheet_pct", "coil_pct", "helix", "sheet", "coil",
                       "helix_percent", "sheet_percent", "coil_percent"]:
        if candidate in headers_lower:
            pct_keys.append(headers_lower[candidate])
    valid_pcts = True
    for row in rows:
        for k in pct_keys:
            try:
                v = float(row[k])
                if v < 0 or v > 100:
                    valid_pcts = False
            except (ValueError, KeyError):
                valid_pcts = False
    if pct_keys and valid_pcts:
        print(f"PASS:L2_valid_percentages - {len(pct_keys)} pct columns")
    else:
        print(f"FAIL:L2_valid_percentages")

    # L2: seq1 (helix-rich) 应有较高 helix 比例
    helix_key = None
    for c in ["helix_pct", "helix", "helix_percent"]:
        if c in headers_lower:
            helix_key = headers_lower[c]
            break
    if helix_key and len(rows) >= 1:
        try:
            h_pct = float(rows[0][helix_key])
            if h_pct > 20:
                print(f"PASS:L2_helix_rich_detected - helix={h_pct:.1f}%")
            else:
                print(f"FAIL:L2_helix_rich_detected - helix={h_pct:.1f}% (expected >20%)")
        except:
            print("FAIL:L2_helix_rich_detected - parse error")
    else:
        print("FAIL:L2_helix_rich_detected - no helix column")

    # L2: seq2 (sheet-rich) 应有较高 sheet 比例
    sheet_key = None
    for c in ["sheet_pct", "sheet", "sheet_percent"]:
        if c in headers_lower:
            sheet_key = headers_lower[c]
            break
    if sheet_key and len(rows) >= 2:
        try:
            s_pct = float(rows[1][sheet_key])
            if s_pct > 20:
                print(f"PASS:L2_sheet_rich_detected - sheet={s_pct:.1f}%")
            else:
                print(f"FAIL:L2_sheet_rich_detected - sheet={s_pct:.1f}% (expected >20%)")
        except:
            print("FAIL:L2_sheet_rich_detected - parse error")
    else:
        print("FAIL:L2_sheet_rich_detected - no sheet column")

    # L2: structure 字符串只包含 H, E, C
    if struct_key:
        all_valid = True
        for row in rows:
            ss = row.get(struct_key, "")
            if ss and not all(c in "HEChec" for c in ss):
                all_valid = False
        if all_valid:
            print("PASS:L2_all_residues_assigned")
        else:
            print("FAIL:L2_all_residues_assigned - invalid characters in structure string")
    else:
        print("FAIL:L2_all_residues_assigned")

    # L2: 短序列也能处理
    if len(rows) >= 4:
        seq4 = rows[3]
        length_key = None
        for c in ["length", "len", "seq_length"]:
            if c in headers_lower:
                length_key = headers_lower[c]
                break
        if length_key:
            try:
                if int(seq4[length_key]) == 9:
                    print("PASS:L2_short_seq_handled")
                else:
                    print(f"FAIL:L2_short_seq_handled - length={seq4[length_key]}")
            except:
                print("PASS:L2_short_seq_handled")  # 至少有输出
        else:
            print("PASS:L2_short_seq_handled")  # 有行即可
    else:
        print("FAIL:L2_short_seq_handled")

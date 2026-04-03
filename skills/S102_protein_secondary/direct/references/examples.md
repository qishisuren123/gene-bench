# Example 1: Parse FASTA and build propensity lookup
def parse_fasta(text):
    header, seq_lines = None, []
    for line in text.strip().split('\n'):
        if line.startswith('>'):
            header = line[1:].strip()
        else:
            seq_lines.append(line.strip())
    return header, ''.join(seq_lines)

# Chou-Fasman propensity values (subset)
HELIX_PROP = {
    'A': 1.42, 'R': 0.98, 'N': 0.67, 'D': 1.01, 'C': 0.70,
    'E': 1.51, 'Q': 1.11, 'G': 0.57, 'H': 1.00, 'I': 1.08,
    'L': 1.21, 'K': 1.16, 'M': 1.45, 'F': 1.13, 'P': 0.57,
    'S': 0.77, 'T': 0.83, 'W': 1.08, 'Y': 0.69, 'V': 1.06,
}
SHEET_PROP = {
    'A': 0.83, 'R': 0.93, 'N': 0.89, 'D': 0.54, 'C': 1.19,
    'E': 0.37, 'Q': 1.10, 'G': 0.75, 'H': 0.87, 'I': 1.60,
    'L': 1.30, 'K': 0.74, 'M': 1.05, 'F': 1.38, 'P': 0.55,
    'S': 0.75, 'T': 1.19, 'W': 1.37, 'Y': 1.47, 'V': 1.70,
}

# Example 2: Sliding window structure prediction
def predict_structure(sequence, window=6):
    result = []
    for i in range(len(sequence)):
        start = max(0, i - window // 2)
        end = min(len(sequence), i + window // 2 + 1)
        seg = sequence[start:end]
        avg_h = sum(HELIX_PROP.get(aa, 1.0) for aa in seg) / len(seg)
        avg_s = sum(SHEET_PROP.get(aa, 1.0) for aa in seg) / len(seg)
        if avg_h > 1.0 and avg_h >= avg_s:
            result.append('H')
        elif avg_s > 1.0:
            result.append('E')
        else:
            result.append('C')
    return ''.join(result)

seq = "ACDEFGHIKLMNPQRSTVWY"
print(predict_structure(seq))

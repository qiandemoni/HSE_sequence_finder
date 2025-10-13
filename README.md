# DNA/RNA Sequence Pattern Finder

[![Python Version](https://img.shields.io/badge/python-3.7%2B-blue)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-Apache%202.0-green.svg)](LICENSE)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

A Python tool for searching specific patterns in DNA/RNA sequences with support for mismatches, variable gap sizes, and comprehensive statistical analysis. Designed for promoter analysis, cis-regulatory element discovery, and transcription factor binding site identification.

---

## Features at a Glance

| Feature | Description |
|---------|-------------|
| **Pattern Matching** | Search for multiple sub-patterns with IUPAC wildcard support (`n` matches any nucleotide) |
| **Flexible Gap Analysis** | Systematically test spacer sizes (0-3 bp, configurable) between composite motifs |
| **Mismatch Tolerance** | Find matches with 0-2 mismatches (configurable), with position-specific tracking |
| **Visual Validation** | Excel output with **red-highlighted mismatches** for manual curation |
| **TSS-Relative Positioning** | Coordinates relative to transcription start site for functional interpretation |
| **Batch Processing** | Run multiple search tasks with different parameters and merge results |
| **Statistical Analysis** | 4D analysis (Pattern × Mismatch × Gap × Sequence) with publication-quality figures |
| **Publication-Ready Output** | Nature-quality visualizations (300 DPI, colorblind-friendly) |

---

## Quick Start (5 Minutes)

```bash
# 1. Clone repository
git clone https://github.com/qiandemoni/HSE_sequence_finder.git
cd HSE_sequence_finder

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run example search
python3 sequence_finder.py examples/sample_input.fasta output.xlsx \
    --patterns "nGAAn" "nTTCn" "nGAAn" \
    --gap-sizes 0 1 2 3 \
    --max-mismatches 2

# 4. Analyze results
python3 analyze_results.py output.xlsx analysis.xlsx

# 5. View results
# - output.xlsx: Search results with red-highlighted mismatches
# - analysis.xlsx: Statistical analysis
# - output_charts/: Publication-quality figures
```

---

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
  - [Single Task Mode](#single-task-mode)
  - [Batch Mode](#batch-mode)
  - [Results Analysis](#results-analysis)
- [Output Format](#output-format)
- [How It Works](#how-it-works)
- [Citation](#citation)
- [Contributing](#contributing)
- [Troubleshooting](#troubleshooting)
- [License](#license)

---

## Installation

### Requirements

- Python 3.7 or higher
- pip package manager

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Dependencies

```
biopython>=1.79    # FASTA parsing
openpyxl>=3.0.0    # Excel output
pandas>=1.3.0      # Analysis module
matplotlib>=3.3.0  # Visualization
numpy>=1.21.0      # Statistical analysis
```

---

## Usage

There are **three main tools**:

| Tool | Purpose | Input | Output |
|------|---------|-------|--------|
| `sequence_finder.py` | Single pattern search | FASTA + patterns | Excel with matches |
| `batch_sequence_finder.py` | Multiple searches | FASTA + JSON config | Merged Excel results |
| `analyze_results.py` | Statistical analysis | Excel results | Analysis + figures |

---

### Single Task Mode

Search for a single pattern combination across all sequences.

#### Basic Command

```bash
python3 sequence_finder.py <input.fasta> <output.xlsx> \
    --patterns "nGAAn" "nTTCn" "nGAAn"
```

#### Command-Line Arguments

| Argument | Required | Default | Description |
|----------|----------|---------|-------------|
| `input_fasta` | ✅ | - | Path to input FASTA file |
| `output_excel` | ✅ | - | Path to output Excel file |
| `--patterns` | ✅ | - | Space-separated pattern sequences (use `n` as wildcard) |
| `--gap-sizes` | ❌ | `0 1 2 3` | Space-separated gap sizes to test (in bp) |
| `--max-mismatches` | ❌ | `2` | Maximum allowed mismatches per match |

#### Examples

**Example 1: Default settings** (0-3 gaps, up to 2 mismatches)
```bash
python3 sequence_finder.py examples/sample_input.fasta output.xlsx \
    --patterns "nGAAn" "nTTCn" "nGAAn"
```

**Example 2: Strict matching** (only 1 mismatch, gaps 0-1 bp)
```bash
python3 sequence_finder.py input.fasta output.xlsx \
    --patterns "nGAAn" "nTTCn" "nGAAn" \
    --gap-sizes 0 1 \
    --max-mismatches 1
```

**Example 3: Custom patterns** (longer motifs, no wildcards)
```bash
python3 sequence_finder.py input.fasta output.xlsx \
    --patterns "ACGTACGT" "TGCATGCA" \
    --gap-sizes 0 1 2 3 4 5
```

---

### Batch Mode

Run multiple pattern searches with different parameters and merge results.

#### Basic Command

```bash
python3 batch_sequence_finder.py <config.json>
```

#### JSON Configuration Format

Create a JSON file (e.g., `my_config.json`):

```json
{
  "input_fasta": "examples/sample_input.fasta",
  "output_excel": "batch_results.xlsx",
  "output_mode": "single",
  "tasks": [
    {
      "name": "Task1_GAA_TTC_pattern",
      "patterns": ["nGAAn", "nTTCn", "nGAAn"],
      "gap_sizes": [0, 1, 2, 3],
      "max_mismatches": 2
    },
    {
      "name": "Task2_strict_matching",
      "patterns": ["nGAAn", "nTTCn", "nGAAn"],
      "gap_sizes": [0, 1],
      "max_mismatches": 1
    }
  ]
}
```

#### Configuration Fields

**Top-level fields:**
- `input_fasta` (required): Path to input FASTA file
- `output_excel` (required): Path to output Excel file
- `output_mode` (optional): `"single"` or `"multi"` (default: `"single"`)
  - `"single"`: All results in one sheet with Task Name column
  - `"multi"`: Separate sheet per task
- `tasks` (required): Array of task definitions

**Task fields:**
- `name` (optional): Task identifier (default: `"Task_1"`, `"Task_2"`, etc.)
- `patterns` (required): Array of pattern strings
- `gap_sizes` (optional): Array of gap sizes to test (default: `[0, 1, 2, 3]`)
- `max_mismatches` (optional): Maximum allowed mismatches (default: `2`)

#### Example

```bash
python3 batch_sequence_finder.py examples/config_example.json
```

---

### Results Analysis

Analyze search results to generate statistics and publication-quality figures.

#### Basic Command

```bash
python3 analyze_results.py <input.xlsx> <output_analysis.xlsx>
```

#### What It Analyzes

The analysis generates **4 analysis sheets** + **3 visualization charts**:

##### 1. Basic Counts Analysis
- Summary statistics (total matches, unique patterns, unique sequences)
- Matches by sequence ID (with percentages)
- Pattern × Sequence cross-tabulation
- Mismatch × Sequence distribution
- Gap × Sequence distribution
- **4D Analysis**: Pattern × Mismatch × Gap × Sequence (complete parameter interaction)

##### 2. Position Sensitivity Analysis (TSS-Focused)
- TSS position distribution (binned)
- TSS position by pattern and sequence
- **TSS Range Categories** (with legend):
  - Very Upstream (< -1000 bp)
  - Upstream (-1000 to -500 bp)
  - Near End (-500 to -100 bp)
  - Very Near End (-100 to 0 bp)

##### 3. Gap Sensitivity Analysis
- Gap size summary (match counts and percentages)
- Gap preferences by pattern
- **Optimal gap per pattern** (identifies best spacing)
- Gap × Sequence comparison table

##### 4. Mismatch Sensitivity Analysis
- Mismatch distribution
- Mismatch tolerance by pattern and sequence
- Gap × Mismatch interaction effects

##### 5. Visualizations (Nature-Quality Charts)

Three publication-ready charts saved to `output_charts/` folder:

1. **Gap Size Distribution by Sequence** (stacked bar chart)
   - File: `output_charts/3_Gap_Size_Distribution_by_Sequence.jpg`

2. **Pattern × Sequence Heatmap** (with count annotations)
   - File: `output_charts/4_Pattern_Sequence_Heatmap.jpg`

3. **TSS Range Categories by Sequence** (grouped bar chart)
   - File: `output_charts/7_TSS_Range_Categories_by_Sequence.jpg`

**Chart features:**
- 300 DPI resolution
- Colorblind-friendly palettes
- Arial/Helvetica fonts (Nature standard)
- Clean styling

#### Command-Line Options

```bash
python3 analyze_results.py <input.xlsx> <output.xlsx> [OPTIONS]
```

**Options:**
- `--position-bin SIZE`: Position bin size for TSS analysis (default: 100)
- `--no-charts`: Skip chart generation (faster processing)

#### Examples

**Example 1: Full analysis with charts**
```bash
python3 analyze_results.py results.xlsx analyzed.xlsx
```

**Example 2: Custom bin size**
```bash
python3 analyze_results.py results.xlsx analyzed.xlsx --position-bin 50
```

**Example 3: Skip charts (faster)**
```bash
python3 analyze_results.py results.xlsx analyzed.xlsx --no-charts
```

---

## Output Format

### Single Task Mode Output

Excel file with **7 columns**:

| Column | Description |
|--------|-------------|
| Sequence ID | Identifier from FASTA file |
| Found Subsequence | Matched sequence (**red-highlighted mismatches**) |
| Start Position | 1-based position in sequence |
| Transcript Start Site Position | Position relative to sequence end (negative = upstream) |
| Mismatch Count | Number of mismatches (0-2) |
| Gap Size | Number of nucleotides between patterns |
| Pattern | Input patterns used (e.g., `nGAAn, nTTCn, nGAAn`) |

**Note:** Red-highlighted bases in "Found Subsequence" indicate mismatch positions for easy manual validation.

### Batch Mode Output

**Single Sheet Mode** (`output_mode: "single"`): 8 columns (adds "Task Name" column)

**Multi-Sheet Mode** (`output_mode: "multi"`): Separate sheets per task (7 columns each)

---

## How It Works

### Algorithm: Exhaustive Sliding Window Search

1. **Pattern Assembly**: Patterns are concatenated with specified gap sizes
   - Example: `nGAAn` + (gap=2) + `nTTCn` + (gap=2) + `nGAAn` → `nGAAnnnnTTCnnnGAAn`

2. **Sliding Window**: The combined pattern slides across the entire sequence
   - Evaluates every possible starting position

3. **Mismatch Calculation**:
   - Wildcards (`n`) match any nucleotide (do NOT count as mismatches)
   - Specific bases (A, T, C, G) must match exactly or count as mismatches
   - Tracks mismatch positions for visualization

4. **Gap Testing**: Process repeats for each gap size (e.g., 0, 1, 2, 3 bp)

5. **TSS Coordinates**: Start positions converted to TSS-relative coordinates
   - Formula: `TSS Position = Start Position - Sequence Length`
   - Negative values indicate upstream positions

### Biological Rationale

- **Gap flexibility**: Transcription factor dimers/heterodimers exhibit spacing tolerance (±1-2 bp typical)
- **Mismatch tolerance**: Accounts for natural sequence variation and imperfect binding
- **TSS positioning**: Enables functional interpretation (proximal vs. distal elements)
- **Composite element search**: Many regulatory modules require multiple motifs in proximity

---

## Citation

If you use this software in your research, please cite:

```bibtex
@software{sequence_finder,
  title = {DNA/RNA Sequence Pattern Finder},
  author = {Qiande, Moni},
  year = {2025},
  url = {https://github.com/qiandemoni/HSE_sequence_finder},
  version = {1.0.0},
  license = {Apache-2.0}
}
```

Also see: [CITATION.cff](CITATION.cff) for machine-readable citation information.

### Related Publications

For methodology details, see: [docs/Methodology.md](docs/Methodology.md)

---

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for:
- How to report issues
- How to suggest features
- Code style guidelines
- Pull request process

---

## Troubleshooting

### Common Issues

**1. "ModuleNotFoundError: No module named 'Bio'"**
```bash
# Solution: Install biopython
pip install biopython>=1.79
```

**2. "Excel file output is empty"**
- Check that your FASTA file is properly formatted
- Verify patterns are correctly specified (use `n` for wildcards)
- Try reducing `--max-mismatches` or increasing `--gap-sizes` range

**3. "Charts not generating"**
```bash
# Solution: Install matplotlib
pip install matplotlib>=3.3.0

# Or skip charts:
python3 analyze_results.py input.xlsx output.xlsx --no-charts
```

**4. "No matches found"**
- Your patterns may be too strict
- Try: Increase `--max-mismatches` to 2 or 3
- Try: Expand `--gap-sizes` range (e.g., `0 1 2 3 4 5`)
- Verify your patterns are biologically plausible

**5. "Sequence too short for pattern"**
- Ensure your sequences are longer than: `pattern_length + (num_patterns-1) * max_gap_size`
- Example: 3 patterns of 5bp each with max gap=3 requires sequences ≥ 21bp

### Getting Help

- **Issues**: [GitHub Issues](https://github.com/qiandemoni/HSE_sequence_finder/issues)
- **Discussions**: [GitHub Discussions](https://github.com/qiandemoni/HSE_sequence_finder/discussions)
- **Email**: mqiande@ufl.edu

---

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

```
Copyright 2025 Qiande, Moni

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
```

---

## Acknowledgments

- Built using [Biopython](https://biopython.org/) for FASTA parsing
- Visualization powered by [Matplotlib](https://matplotlib.org/)
- Excel output via [openpyxl](https://openpyxl.readthedocs.io/)

---

**Last Updated**: October 2025
**Version**: 1.0.0

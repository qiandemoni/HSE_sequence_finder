#!/usr/bin/env python3
"""
DNA/RNA Sequence Pattern Finder

Description:
    Searches for patterns with variable gaps and mismatches in FASTA sequences.
    Supports IUPAC wildcards, TSS-relative positioning, and red-highlighted
    mismatch visualization in Excel output.

Author: Qiande, Moni
Email: mqiande@ufl.edu
License: Apache-2.0
Version: 1.0.0
Created: 2025
Last Modified: 2025-10-12

Usage:
    python3 sequence_finder.py input.fasta output.xlsx --patterns "nGAAn" "nTTCn"

For more information, see README.md
"""

import argparse
import sys
from typing import List, Tuple, Dict
from Bio import SeqIO
from openpyxl import Workbook
from openpyxl.styles import Font
from openpyxl.cell.text import InlineFont
from openpyxl.cell.rich_text import TextBlock, CellRichText


def parse_fasta(fasta_file: str) -> List[Tuple[str, str]]:
    """
    Parse FASTA file and return list of (id, sequence) tuples.

    Args:
        fasta_file: Path to FASTA file

    Returns:
        List of tuples containing (sequence_id, sequence_string)
    """
    sequences = []
    try:
        for record in SeqIO.parse(fasta_file, "fasta"):
            sequences.append((record.id, str(record.seq).upper()))
        print(f"Loaded {len(sequences)} sequences from {fasta_file}")
        return sequences
    except Exception as e:
        print(f"Error reading FASTA file: {e}")
        sys.exit(1)


def pattern_matches(sequence: str, pattern: str) -> bool:
    """
    Check if sequence matches pattern where 'n' is wildcard.

    Args:
        sequence: DNA sequence to check
        pattern: Pattern with 'n' as wildcard

    Returns:
        True if sequence matches pattern
    """
    if len(sequence) != len(pattern):
        return False

    for seq_char, pat_char in zip(sequence, pattern):
        if pat_char.lower() != 'n' and seq_char != pat_char:
            return False
    return True


def count_mismatches(sequence: str, pattern: str) -> Tuple[int, List[int]]:
    """
    Count mismatches between sequence and pattern, treating 'n' as wildcard.

    Args:
        sequence: DNA sequence to check
        pattern: Pattern with 'n' as wildcard (matches any nucleotide)

    Returns:
        Tuple of (mismatch_count, list_of_mismatch_positions)
    """
    if len(sequence) != len(pattern):
        return (float('inf'), [])

    mismatches = 0
    mismatch_positions = []

    for i, (seq_char, pat_char) in enumerate(zip(sequence, pattern)):
        if pat_char.lower() == 'n':
            # Wildcard always matches
            continue
        elif seq_char != pat_char:
            mismatches += 1
            mismatch_positions.append(i)

    return mismatches, mismatch_positions


def build_pattern_with_gaps(patterns: List[str], gap_size: int) -> str:
    """
    Build a combined pattern with specified gap size between sub-patterns.

    Args:
        patterns: List of pattern strings (e.g., ['nGAAn', 'nTTCn', 'nGAAn'])
        gap_size: Number of wildcard nucleotides between patterns

    Returns:
        Combined pattern string with gaps
    """
    gap = 'n' * gap_size
    return gap.join(patterns)


def search_pattern_in_sequence(
    seq_id: str,
    sequence: str,
    patterns: List[str],
    gap_size: int,
    max_mismatches: int = 2
) -> List[Dict]:
    """
    Search for pattern matches in a sequence with specified gap size.

    Args:
        seq_id: Sequence identifier
        sequence: DNA sequence to search
        patterns: List of sub-patterns
        gap_size: Gap size between patterns
        max_mismatches: Maximum allowed mismatches (0, 1, or 2)

    Returns:
        List of match dictionaries with keys: seq_id, subsequence, start_pos,
        tss_position, mismatch_count, gap_size, pattern, mismatch_positions
    """
    results = []

    # Build the complete pattern with gaps
    full_pattern = build_pattern_with_gaps(patterns, gap_size)
    pattern_length = len(full_pattern)
    seq_length = len(sequence)

    # Slide window across sequence
    for i in range(len(sequence) - pattern_length + 1):
        subseq = sequence[i:i + pattern_length]
        mismatch_count, mismatch_positions = count_mismatches(subseq, full_pattern)

        # Only keep matches with acceptable mismatch count
        if mismatch_count <= max_mismatches:
            start_pos = i + 1  # 1-based indexing
            tss_position = start_pos - seq_length  # Position relative to sequence end

            results.append({
                'seq_id': seq_id,
                'subsequence': subseq,
                'start_pos': start_pos,
                'tss_position': tss_position,
                'mismatch_count': mismatch_count,
                'gap_size': gap_size,
                'pattern': ', '.join(patterns),
                'mismatch_positions': mismatch_positions
            })

    return results


def create_rich_text_cell(text: str, mismatch_positions: List[int]) -> CellRichText:
    """
    Create rich text cell with red-colored characters at mismatch positions.

    Args:
        text: The full text string
        mismatch_positions: List of 0-based indices to color red

    Returns:
        CellRichText object with selective coloring
    """
    if not mismatch_positions:
        # No mismatches, return plain text
        return text

    # Create list of text blocks with appropriate formatting
    text_blocks = []
    mismatch_set = set(mismatch_positions)

    i = 0
    while i < len(text):
        if i in mismatch_set:
            # Start of mismatch segment
            j = i
            while j < len(text) and j in mismatch_set:
                j += 1
            # Add red text block
            text_blocks.append(
                TextBlock(InlineFont(color='FF0000'), text[i:j])
            )
            i = j
        else:
            # Start of normal segment
            j = i
            while j < len(text) and j not in mismatch_set:
                j += 1
            # Add normal text block
            text_blocks.append(
                TextBlock(InlineFont(color='000000'), text[i:j])
            )
            i = j

    return CellRichText(*text_blocks)


def write_results_to_excel(results: List[Dict], output_file: str):
    """
    Write results to Excel file with colored mismatches.

    Args:
        results: List of match dictionaries
        output_file: Path to output Excel file
    """
    wb = Workbook()
    ws = wb.active
    ws.title = "Pattern Matches"

    # Write header
    headers = ['Sequence ID', 'Found Subsequence', 'Start Position', 'Transcript Start Site Position',
               'Mismatch Count', 'Gap Size', 'Pattern']
    ws.append(headers)

    # Style header
    header_font = Font(bold=True)
    for cell in ws[1]:
        cell.font = header_font

    # Write results
    for result in results:
        row = [
            result['seq_id'],
            create_rich_text_cell(result['subsequence'], result['mismatch_positions']),
            result['start_pos'],
            result['tss_position'],
            result['mismatch_count'],
            result['gap_size'],
            result['pattern']
        ]
        ws.append(row)

    # Auto-adjust column widths
    for column in ws.columns:
        max_length = 0
        column_letter = column[0].column_letter
        for cell in column:
            try:
                if cell.value:
                    max_length = max(max_length, len(str(cell.value)))
            except:
                pass
        adjusted_width = min(max_length + 2, 50)
        ws.column_dimensions[column_letter].width = adjusted_width

    # Save workbook
    wb.save(output_file)
    print(f"Results written to {output_file}")


def main():
    """Main function to run the sequence pattern finder."""
    parser = argparse.ArgumentParser(
        description='Search for DNA/RNA sequence patterns with gaps and mismatches',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python sequence_finder.py input.fasta output.xlsx --patterns "nGAAn" "nTTCn" "nGAAn"
  python sequence_finder.py input.fasta output.xlsx --patterns "nGAAn" "nTTCn" "nGAAn" --max-mismatches 1
  python sequence_finder.py input.fasta output.xlsx --patterns "ACGT" "TGCA" --gap-sizes 0 1 2
        """
    )

    parser.add_argument('input_fasta', help='Input FASTA file')
    parser.add_argument('output_excel', help='Output Excel file (.xlsx)')
    parser.add_argument('--patterns', nargs='+', required=True,
                        help='Pattern sequences (e.g., "nGAAn" "nTTCn" "nGAAn")')
    parser.add_argument('--gap-sizes', nargs='+', type=int, default=[0, 1, 2, 3],
                        help='Gap sizes to test (default: 0 1 2 3)')
    parser.add_argument('--max-mismatches', type=int, default=2,
                        help='Maximum allowed mismatches (default: 2)')

    args = parser.parse_args()

    # Validate inputs
    if args.max_mismatches < 0:
        print("Error: max-mismatches must be non-negative")
        sys.exit(1)

    if any(gap < 0 for gap in args.gap_sizes):
        print("Error: gap sizes must be non-negative")
        sys.exit(1)

    # Convert patterns to uppercase
    patterns = [p.upper() for p in args.patterns]

    print(f"Searching for patterns: {patterns}")
    print(f"Gap sizes: {args.gap_sizes}")
    print(f"Max mismatches: {args.max_mismatches}")
    print()

    # Parse FASTA file
    sequences = parse_fasta(args.input_fasta)

    # Search for patterns
    all_results = []

    for gap_size in args.gap_sizes:
        print(f"Searching with gap size {gap_size}...")

        for seq_id, sequence in sequences:
            results = search_pattern_in_sequence(
                seq_id, sequence, patterns, gap_size, args.max_mismatches
            )
            all_results.extend(results)

        print(f"  Found {len([r for r in all_results if r['gap_size'] == gap_size])} matches")

    print(f"\nTotal matches found: {len(all_results)}")

    # Write results to Excel
    if all_results:
        write_results_to_excel(all_results, args.output_excel)
    else:
        print("No matches found. No output file created.")


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""
Analysis Script for DNA/RNA Sequence Pattern Finder Results

Description:
    Reads Excel output and generates 4 types of analysis with visualizations:
    1. Basic counts (pattern, mismatch, gap)
    2. Position sensitivity (TSS-focused)
    3. Gap sensitivity
    4. Mismatch sensitivity

    Also generates 3 publication-quality Nature-style charts (300 DPI, JPEG).

Author: Qiande, Moni
Email: mqiande@ufl.edu
License: Apache-2.0
Version: 1.0.0
Created: 2025
Last Modified: 2025-10-12

Usage:
    python3 analyze_results.py input.xlsx output_analysis.xlsx
    python3 analyze_results.py input.xlsx output.xlsx --no-charts

For more information, see README.md
"""

import argparse
import sys
import os
from typing import Dict
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment
from openpyxl.utils.dataframe import dataframe_to_rows


def load_results(excel_file: str) -> pd.DataFrame:
    """
    Load results from Excel file.

    Args:
        excel_file: Path to Excel file from sequence_finder.py or batch_sequence_finder.py

    Returns:
        DataFrame with all results
    """
    try:
        # Try to read first sheet
        df = pd.read_excel(excel_file, sheet_name=0)
        print(f"Loaded {len(df)} matches from {excel_file}")

        # Check if it's batch mode (has Task Name column) or single mode
        if 'Task Name' in df.columns:
            print("Detected batch mode output")
        else:
            print("Detected single task mode output")

        return df
    except Exception as e:
        print(f"Error loading Excel file: {e}")
        sys.exit(1)


def analyze_basic_counts(df: pd.DataFrame) -> Dict[str, pd.DataFrame]:
    """
    Analysis 1: Basic counts by pattern, mismatch, gap, and sequence ID.

    Returns:
        Dictionary of analysis DataFrames
    """
    analyses = {}

    # Summary statistics
    summary_data = {
        'Metric': ['Total Matches', 'Unique Patterns', 'Unique Sequences',
                   'Avg Mismatches', 'Avg Gap Size'],
        'Value': [
            len(df),
            df['Pattern'].nunique() if 'Pattern' in df.columns else 0,
            df['Sequence ID'].nunique() if 'Sequence ID' in df.columns else 0,
            round(df['Mismatch Count'].mean(), 2) if 'Mismatch Count' in df.columns else 0,
            round(df['Gap Size'].mean(), 2) if 'Gap Size' in df.columns else 0
        ]
    }
    analyses['Summary'] = pd.DataFrame(summary_data)

    # Matches by Sequence ID
    if 'Sequence ID' in df.columns:
        seq_counts = df.groupby('Sequence ID').size().reset_index(name='Match Count')
        seq_counts['Percentage'] = (seq_counts['Match Count'] / len(df) * 100).round(2)
        seq_counts = seq_counts.sort_values('Match Count', ascending=False)
        analyses['Matches by Sequence'] = seq_counts

    # Count by pattern
    if 'Pattern' in df.columns:
        pattern_counts = df.groupby('Pattern').size().reset_index(name='Count')
        pattern_counts['Percentage'] = (pattern_counts['Count'] / len(df) * 100).round(2)
        pattern_counts = pattern_counts.sort_values('Count', ascending=False)
        analyses['By Pattern'] = pattern_counts

    # Pattern × Sequence cross-tabulation
    if all(col in df.columns for col in ['Pattern', 'Sequence ID']):
        pattern_seq = df.groupby(['Sequence ID', 'Pattern']).size().reset_index(name='Count')
        pattern_seq_pivot = pattern_seq.pivot(index='Sequence ID', columns='Pattern', values='Count').fillna(0)
        pattern_seq_pivot = pattern_seq_pivot.astype(int)
        pattern_seq_pivot['Total'] = pattern_seq_pivot.sum(axis=1)
        pattern_seq_pivot = pattern_seq_pivot.sort_values('Total', ascending=False).reset_index()
        analyses['Pattern × Sequence'] = pattern_seq_pivot

    # Count by mismatch
    if 'Mismatch Count' in df.columns:
        mismatch_counts = df.groupby('Mismatch Count').size().reset_index(name='Count')
        mismatch_counts['Percentage'] = (mismatch_counts['Count'] / len(df) * 100).round(2)
        mismatch_counts = mismatch_counts.sort_values('Mismatch Count')
        analyses['By Mismatch'] = mismatch_counts

    # Mismatch × Sequence cross-tabulation
    if all(col in df.columns for col in ['Mismatch Count', 'Sequence ID']):
        mismatch_seq = df.groupby(['Sequence ID', 'Mismatch Count']).size().reset_index(name='Count')
        mismatch_seq_pivot = mismatch_seq.pivot(index='Sequence ID', columns='Mismatch Count', values='Count').fillna(0)
        mismatch_seq_pivot = mismatch_seq_pivot.astype(int)
        mismatch_seq_pivot.columns = [f'Mismatch_{int(c)}' for c in mismatch_seq_pivot.columns]
        mismatch_seq_pivot['Total'] = mismatch_seq_pivot.sum(axis=1)
        mismatch_seq_pivot = mismatch_seq_pivot.sort_values('Total', ascending=False).reset_index()
        analyses['Mismatch × Sequence'] = mismatch_seq_pivot

    # Count by gap size
    if 'Gap Size' in df.columns:
        gap_counts = df.groupby('Gap Size').size().reset_index(name='Count')
        gap_counts['Percentage'] = (gap_counts['Count'] / len(df) * 100).round(2)
        gap_counts = gap_counts.sort_values('Gap Size')
        analyses['By Gap Size'] = gap_counts

    # Gap × Sequence cross-tabulation
    if all(col in df.columns for col in ['Gap Size', 'Sequence ID']):
        gap_seq = df.groupby(['Sequence ID', 'Gap Size']).size().reset_index(name='Count')
        gap_seq_pivot = gap_seq.pivot(index='Sequence ID', columns='Gap Size', values='Count').fillna(0)
        gap_seq_pivot = gap_seq_pivot.astype(int)
        gap_seq_pivot.columns = [f'Gap_{int(c)}' for c in gap_seq_pivot.columns]
        gap_seq_pivot['Total'] = gap_seq_pivot.sum(axis=1)
        gap_seq_pivot = gap_seq_pivot.sort_values('Total', ascending=False).reset_index()
        analyses['Gap × Sequence'] = gap_seq_pivot

    # Cross-tabulation: Pattern × Mismatch × Gap (kept for reference)
    if all(col in df.columns for col in ['Pattern', 'Mismatch Count', 'Gap Size']):
        cross_tab = df.groupby(['Pattern', 'Mismatch Count', 'Gap Size']).size().reset_index(name='Count')
        cross_tab = cross_tab.sort_values(['Pattern', 'Gap Size', 'Mismatch Count'])
        analyses['Pattern × Mismatch × Gap'] = cross_tab

    # Cross-tabulation: Pattern × Mismatch × Gap × Sequence (4D analysis for sequence comparison)
    if all(col in df.columns for col in ['Sequence ID', 'Pattern', 'Mismatch Count', 'Gap Size']):
        cross_tab_seq = df.groupby(['Sequence ID', 'Pattern', 'Mismatch Count', 'Gap Size']).size().reset_index(name='Count')
        cross_tab_seq = cross_tab_seq.sort_values(['Sequence ID', 'Pattern', 'Gap Size', 'Mismatch Count'])
        analyses['Pattern × Mismatch × Gap × Sequence'] = cross_tab_seq

    return analyses


def analyze_position_sensitivity(df: pd.DataFrame, bin_size: int = 100) -> Dict[str, pd.DataFrame]:
    """
    Analysis 2: Position sensitivity - TSS positions relative to sequence end.

    Args:
        df: Results DataFrame
        bin_size: Size of position bins

    Returns:
        Dictionary of analysis DataFrames
    """
    analyses = {}

    # Focus on TSS Position if available
    if 'Transcript Start Site Position' in df.columns:
        tss_col = 'Transcript Start Site Position'

        # TSS position distribution (binned)
        # For TSS (negative values), bin towards more negative
        df['TSS Bin'] = (df[tss_col] // bin_size) * bin_size
        tss_dist = df.groupby('TSS Bin').size().reset_index(name='Count')
        tss_dist['Bin Range'] = tss_dist['TSS Bin'].apply(
            lambda x: f"{int(x)} to {int(x+bin_size-1)}"
        )
        tss_dist = tss_dist[['Bin Range', 'Count']].sort_values('Bin Range')
        analyses['TSS Position Distribution'] = tss_dist

        # TSS summary statistics
        tss_summary = pd.DataFrame({
            'Metric': [
                'Mean TSS Position',
                'Median TSS Position',
                'Most Upstream (Min)',
                'Most Downstream (Max)',
                'Std Deviation'
            ],
            'Value': [
                round(df[tss_col].mean(), 2),
                round(df[tss_col].median(), 2),
                int(df[tss_col].min()),
                int(df[tss_col].max()),
                round(df[tss_col].std(), 2)
            ]
        })
        analyses['TSS Position Summary'] = tss_summary

        # TSS position by pattern
        if 'Pattern' in df.columns:
            tss_by_pattern = df.groupby('Pattern')[tss_col].agg(['mean', 'median', 'std', 'min', 'max', 'count'])
            tss_by_pattern.columns = ['Mean TSS', 'Median TSS', 'Std Dev', 'Most Upstream', 'Most Downstream', 'Count']
            tss_by_pattern = tss_by_pattern.round(2).reset_index()
            tss_by_pattern = tss_by_pattern.sort_values('Mean TSS')  # Sort by position
            analyses['TSS Position by Pattern'] = tss_by_pattern

        # TSS position by sequence
        if 'Sequence ID' in df.columns:
            tss_by_seq = df.groupby('Sequence ID')[tss_col].agg(['count', 'mean', 'median', 'min', 'max'])
            tss_by_seq.columns = ['Match Count', 'Avg TSS', 'Median TSS', 'Most Upstream', 'Most Downstream']
            tss_by_seq = tss_by_seq.round(2).reset_index()
            tss_by_seq = tss_by_seq.sort_values('Match Count', ascending=False)
            analyses['TSS Position by Sequence'] = tss_by_seq

        # TSS position range analysis - PER SEQUENCE
        if 'Sequence ID' in df.columns:
            # Define range categories
            def categorize_tss(tss_val):
                if tss_val < -1000:
                    return 'Very Upstream'
                elif -1000 <= tss_val < -500:
                    return 'Upstream'
                elif -500 <= tss_val < -100:
                    return 'Near End'
                else:  # -100 to 0
                    return 'Very Near End'

            # Add range category to dataframe
            df['TSS Range'] = df[tss_col].apply(categorize_tss)

            # Create cross-tabulation: Sequence ID × TSS Range
            tss_range_seq = df.groupby(['Sequence ID', 'TSS Range']).size().reset_index(name='Count')
            tss_range_pivot = tss_range_seq.pivot(index='Sequence ID', columns='TSS Range', values='Count').fillna(0)
            tss_range_pivot = tss_range_pivot.astype(int)

            # Ensure column order (may not all exist)
            desired_order = ['Very Upstream', 'Upstream', 'Near End', 'Very Near End']
            existing_cols = [col for col in desired_order if col in tss_range_pivot.columns]
            tss_range_pivot = tss_range_pivot[existing_cols]

            # Rename columns to include numeric ranges
            column_mapping = {
                'Very Upstream': 'Very Upstream (< -1000)',
                'Upstream': 'Upstream (-1000 to -500)',
                'Near End': 'Near End (-500 to -100)',
                'Very Near End': 'Very Near End (-100 to 0)'
            }
            tss_range_pivot.rename(columns=column_mapping, inplace=True)

            # Update existing_cols to use new names
            existing_cols = [column_mapping.get(col, col) for col in existing_cols]

            # Add total and percentage columns
            tss_range_pivot['Total Matches'] = tss_range_pivot.sum(axis=1)

            # Add percentage columns for each range
            for col in existing_cols:
                tss_range_pivot[f'{col} %'] = (tss_range_pivot[col] / tss_range_pivot['Total Matches'] * 100).round(2)

            tss_range_pivot = tss_range_pivot.sort_values('Total Matches', ascending=False).reset_index()
            analyses['TSS Ranges by Sequence'] = tss_range_pivot

    # Fallback to Start Position if TSS not available
    elif 'Start Position' in df.columns:
        # Position distribution (binned)
        df['Position Bin'] = (df['Start Position'] // bin_size) * bin_size
        position_dist = df.groupby('Position Bin').size().reset_index(name='Count')
        position_dist['Bin Range'] = position_dist['Position Bin'].apply(
            lambda x: f"{x}-{x+bin_size-1}"
        )
        position_dist = position_dist[['Bin Range', 'Count']].sort_values('Bin Range')
        analyses['Position Distribution'] = position_dist

        # Average position by pattern
        if 'Pattern' in df.columns:
            avg_position = df.groupby('Pattern')['Start Position'].agg(['mean', 'std', 'min', 'max', 'count'])
            avg_position.columns = ['Avg Position', 'Std Dev', 'Min Position', 'Max Position', 'Count']
            avg_position = avg_position.round(2).reset_index()
            analyses['Position by Pattern'] = avg_position

    return analyses


def analyze_gap_sensitivity(df: pd.DataFrame) -> Dict[str, pd.DataFrame]:
    """
    Analysis 3: Gap sensitivity - how gap size affects match frequency.

    Returns:
        Dictionary of analysis DataFrames
    """
    analyses = {}

    if 'Gap Size' not in df.columns:
        return analyses

    # Match count by gap size
    gap_summary = df.groupby('Gap Size').size().reset_index(name='Count')
    gap_summary['Percentage'] = (gap_summary['Count'] / len(df) * 100).round(2)
    gap_summary = gap_summary.sort_values('Gap Size')
    analyses['Gap Size Summary'] = gap_summary

    # Gap sensitivity by pattern
    if 'Pattern' in df.columns:
        pattern_gap = df.groupby(['Pattern', 'Gap Size']).size().reset_index(name='Count')

        # Add percentage within each pattern
        pattern_totals = df.groupby('Pattern').size().reset_index(name='Total')
        pattern_gap = pattern_gap.merge(pattern_totals, on='Pattern')
        pattern_gap['Percentage'] = (pattern_gap['Count'] / pattern_gap['Total'] * 100).round(2)
        pattern_gap = pattern_gap[['Pattern', 'Gap Size', 'Count', 'Percentage']]
        pattern_gap = pattern_gap.sort_values(['Pattern', 'Gap Size'])
        analyses['Gap by Pattern'] = pattern_gap

        # Optimal gap size per pattern (gap with most matches)
        optimal_gaps = pattern_gap.loc[pattern_gap.groupby('Pattern')['Count'].idxmax()]
        optimal_gaps = optimal_gaps[['Pattern', 'Gap Size', 'Count']].rename(
            columns={'Gap Size': 'Optimal Gap Size', 'Count': 'Match Count'}
        )
        analyses['Optimal Gap per Pattern'] = optimal_gaps

    # Gap × Sequence cross-tabulation for comparison
    if 'Sequence ID' in df.columns:
        gap_seq = df.groupby(['Sequence ID', 'Gap Size']).size().reset_index(name='Count')
        gap_seq_pivot = gap_seq.pivot(index='Sequence ID', columns='Gap Size', values='Count').fillna(0)
        gap_seq_pivot = gap_seq_pivot.astype(int)
        gap_seq_pivot.columns = [f'Gap_{int(c)}' for c in gap_seq_pivot.columns]
        gap_seq_pivot['Total'] = gap_seq_pivot.sum(axis=1)

        # Add percentage columns
        for col in gap_seq_pivot.columns:
            if col.startswith('Gap_'):
                gap_seq_pivot[f'{col}_pct'] = (gap_seq_pivot[col] / gap_seq_pivot['Total'] * 100).round(2)

        gap_seq_pivot = gap_seq_pivot.sort_values('Total', ascending=False).reset_index()
        analyses['Gap × Sequence (Comparison)'] = gap_seq_pivot

    # Gap vs mismatch interaction
    if 'Mismatch Count' in df.columns:
        gap_mismatch = df.groupby(['Gap Size', 'Mismatch Count']).size().reset_index(name='Count')
        gap_mismatch_pivot = gap_mismatch.pivot(index='Gap Size', columns='Mismatch Count', values='Count').fillna(0)
        gap_mismatch_pivot = gap_mismatch_pivot.astype(int).reset_index()
        analyses['Gap × Mismatch'] = gap_mismatch_pivot

    return analyses


def analyze_mismatch_sensitivity(df: pd.DataFrame) -> Dict[str, pd.DataFrame]:
    """
    Analysis 4: Mismatch sensitivity - distribution and patterns of mismatches.

    Returns:
        Dictionary of analysis DataFrames
    """
    analyses = {}

    if 'Mismatch Count' not in df.columns:
        return analyses

    # Mismatch distribution
    mismatch_dist = df.groupby('Mismatch Count').size().reset_index(name='Count')
    mismatch_dist['Percentage'] = (mismatch_dist['Count'] / len(df) * 100).round(2)
    mismatch_dist = mismatch_dist.sort_values('Mismatch Count')
    analyses['Mismatch Distribution'] = mismatch_dist

    # Mismatch by pattern
    if 'Pattern' in df.columns:
        pattern_mismatch = df.groupby(['Pattern', 'Mismatch Count']).size().reset_index(name='Count')

        # Add percentage within each pattern
        pattern_totals = df.groupby('Pattern').size().reset_index(name='Total')
        pattern_mismatch = pattern_mismatch.merge(pattern_totals, on='Pattern')
        pattern_mismatch['Percentage'] = (pattern_mismatch['Count'] / pattern_mismatch['Total'] * 100).round(2)
        pattern_mismatch = pattern_mismatch[['Pattern', 'Mismatch Count', 'Count', 'Percentage']]
        pattern_mismatch = pattern_mismatch.sort_values(['Pattern', 'Mismatch Count'])
        analyses['Mismatch by Pattern'] = pattern_mismatch

        # Average mismatches per pattern
        avg_mismatch = df.groupby('Pattern')['Mismatch Count'].agg(['mean', 'std', 'min', 'max'])
        avg_mismatch.columns = ['Avg Mismatches', 'Std Dev', 'Min', 'Max']
        avg_mismatch = avg_mismatch.round(2).reset_index()
        analyses['Avg Mismatch per Pattern'] = avg_mismatch

    # Mismatch × Sequence cross-tabulation for comparison
    if 'Sequence ID' in df.columns:
        mismatch_seq = df.groupby(['Sequence ID', 'Mismatch Count']).size().reset_index(name='Count')
        mismatch_seq_pivot = mismatch_seq.pivot(index='Sequence ID', columns='Mismatch Count', values='Count').fillna(0)
        mismatch_seq_pivot = mismatch_seq_pivot.astype(int)
        mismatch_seq_pivot.columns = [f'Mismatch_{int(c)}' for c in mismatch_seq_pivot.columns]
        mismatch_seq_pivot['Total'] = mismatch_seq_pivot.sum(axis=1)

        # Add percentage columns
        for col in mismatch_seq_pivot.columns:
            if col.startswith('Mismatch_'):
                mismatch_seq_pivot[f'{col}_pct'] = (mismatch_seq_pivot[col] / mismatch_seq_pivot['Total'] * 100).round(2)

        # Add average mismatch per sequence
        seq_avg_mismatch = df.groupby('Sequence ID')['Mismatch Count'].mean().reset_index()
        seq_avg_mismatch.columns = ['Sequence ID', 'Avg_Mismatch']
        seq_avg_mismatch['Avg_Mismatch'] = seq_avg_mismatch['Avg_Mismatch'].round(2)
        mismatch_seq_pivot = mismatch_seq_pivot.merge(seq_avg_mismatch, on='Sequence ID')

        mismatch_seq_pivot = mismatch_seq_pivot.sort_values('Total', ascending=False).reset_index(drop=True)
        analyses['Mismatch × Sequence (Comparison)'] = mismatch_seq_pivot

    # Mismatch vs gap correlation
    if 'Gap Size' in df.columns:
        avg_mismatch_by_gap = df.groupby('Gap Size')['Mismatch Count'].mean().reset_index()
        avg_mismatch_by_gap.columns = ['Gap Size', 'Avg Mismatch Count']
        avg_mismatch_by_gap['Avg Mismatch Count'] = avg_mismatch_by_gap['Avg Mismatch Count'].round(2)
        analyses['Avg Mismatch by Gap'] = avg_mismatch_by_gap

    return analyses


def generate_charts(df: pd.DataFrame, output_dir: str = 'output_charts') -> Dict[str, str]:
    """
    Generate 3 publication-quality visualization charts for Nature paper.

    Args:
        df: Results DataFrame
        output_dir: Directory to save chart images

    Returns:
        Dictionary mapping chart names to file paths
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    chart_files = {}

    # Set publication-quality style for Nature paper
    plt.rcParams.update({
        'font.family': 'sans-serif',
        'font.sans-serif': ['Arial', 'Helvetica', 'DejaVu Sans'],
        'font.size': 36,
        'axes.labelsize': 13,
        'axes.titlesize': 15,
        'xtick.labelsize': 11,
        'ytick.labelsize': 11,
        'legend.fontsize': 11,
        'figure.titlesize': 15,
        'axes.linewidth': 1.5,
        'grid.linewidth': 0.5,
        'lines.linewidth': 2.0,
        'patch.linewidth': 1.0,
        'xtick.major.width': 1.5,
        'ytick.major.width': 1.5,
        'xtick.major.size': 5,
        'ytick.major.size': 5,
        'text.usetex': False,
        'savefig.dpi': 300,
        'savefig.bbox': 'tight',
        'savefig.pad_inches': 0.1,
    })

    # Chart 3: Gap Size Distribution by Sequence (stacked bar) - NATURE QUALITY
    if all(col in df.columns for col in ['Sequence ID', 'Gap Size']):
        print("   Generating Chart 1/3: Gap Size Distribution by Sequence...")

        fig, ax = plt.subplots(figsize=(6, 6), dpi=300)

        # Prepare data with cleaned sequence IDs
        df_chart = df.copy()
        df_chart['Sequence ID'] = df_chart['Sequence ID'].str.replace('Promoter_', 'p', regex=False)
        gap_pivot = df_chart.groupby(['Sequence ID', 'Gap Size']).size().unstack(fill_value=0)

        # Professional color scheme - colorblind-friendly
        colors = ['#0173B2', '#DE8F05', '#029E73', '#CC78BC'][:len(gap_pivot.columns)]

        # Create stacked bar chart
        gap_pivot.plot(kind='bar', stacked=True, ax=ax, color=colors,
                      edgecolor='white', linewidth=0.5, width=0.4)

        # Styling
        ax.set_xlabel('')  # Remove x-axis label
        ax.set_ylabel('Match Count', fontsize=13, fontweight='bold')

        # Legend formatting
        legend_labels = [f'Gap {int(i)}' for i in gap_pivot.columns]
        ax.legend(legend_labels, title='Gap Size', title_fontsize=11,
                 frameon=True, fancybox=False, shadow=False,
                 loc='upper right', fontsize=11)

        # Grid and spines
        ax.grid(axis='y', alpha=0.3, linestyle='-', linewidth=0.5)
        ax.set_axisbelow(True)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)

        # Rotate x-axis labels
        plt.xticks(rotation=45, ha='right')

        # Tight layout
        plt.tight_layout()

        # Save as high-res JPEG
        output_path = os.path.join(output_dir, '3_Gap_Size_Distribution_by_Sequence.jpg')
        plt.savefig(output_path, format='jpeg', dpi=300, bbox_inches='tight',
                   pil_kwargs={'quality': 95})
        chart_files['3_Gap_Size_Distribution_by_Sequence'] = output_path
        plt.close(fig)
        print(f"      Saved to: {output_path}")

    # Chart 4: Pattern × Sequence Heatmap - NATURE QUALITY
    if all(col in df.columns for col in ['Sequence ID', 'Pattern']):
        print("   Generating Chart 2/3: Pattern × Sequence Heatmap...")

        fig, ax = plt.subplots(figsize=(12, 8), dpi=300)

        # Prepare data with cleaned sequence IDs and pattern names
        df_chart = df.copy()
        df_chart['Sequence ID'] = df_chart['Sequence ID'].str.replace('Promoter_', 'p', regex=False)
        df_chart['Pattern'] = df_chart['Pattern'].str.replace('N', 'n', regex=False)
        pattern_seq_pivot = df_chart.groupby(['Sequence ID', 'Pattern']).size().unstack(fill_value=0)

        # Create heatmap with professional colormap
        im = ax.imshow(pattern_seq_pivot.values, cmap='YlOrRd', aspect='auto',
                      interpolation='nearest')

        # Set ticks and labels (pattern names already have lowercase n)
        ax.set_xticks(np.arange(len(pattern_seq_pivot.index)))
        ax.set_yticks(np.arange(len(pattern_seq_pivot.columns)))
        ax.set_xticklabels(pattern_seq_pivot.index, rotation=45, ha='right', fontsize=20)
        ax.set_yticklabels(pattern_seq_pivot.columns, fontsize=20)

        # Axis labels
        ax.set_ylabel('Pattern', fontsize=20, fontweight='bold', labelpad=10)
        ax.set_xlabel('')

        # Colorbar
        cbar = plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
        cbar.set_label('Match Count', rotation=270, labelpad=20, fontsize=20, fontweight='bold')
        cbar.ax.tick_params(labelsize=20)

        # Add text annotations
        for i in range(len(pattern_seq_pivot.index)):
            for j in range(len(pattern_seq_pivot.columns)):
                value = int(pattern_seq_pivot.values[i, j])
                # Choose text color based on background intensity
                text_color = 'white' if value > pattern_seq_pivot.values.max() * 0.6 else 'black'
                ax.text(j, i, value, ha="center", va="center",
                       color=text_color, fontsize=20, fontweight='bold')

        # Remove spines
        for spine in ax.spines.values():
            spine.set_visible(False)

        # Tight layout
        plt.tight_layout()

        # Save as high-res JPEG
        output_path = os.path.join(output_dir, '4_Pattern_Sequence_Heatmap.jpg')
        plt.savefig(output_path, format='jpeg', dpi=300, bbox_inches='tight',
                   pil_kwargs={'quality': 95})
        chart_files['4_Pattern_Sequence_Heatmap'] = output_path
        plt.close(fig)
        print(f"      Saved to: {output_path}")

    # Chart 7: TSS Range Categories by Sequence (grouped bar) - NATURE QUALITY
    if all(col in df.columns for col in ['Sequence ID', 'Transcript Start Site Position']):
        print("   Generating Chart 3/3: TSS Range Categories by Sequence...")

        # Categorize TSS
        def categorize_tss(tss_val):
            if tss_val < -1000:
                return 'Very Upstream'
            elif -1000 <= tss_val < -500:
                return 'Upstream'
            elif -500 <= tss_val < -100:
                return 'Near End'
            else:
                return 'Very Near End'

        df_temp = df.copy()
        df_temp['Sequence ID'] = df_temp['Sequence ID'].str.replace('Promoter_', 'p', regex=False)
        df_temp['TSS Range'] = df_temp['Transcript Start Site Position'].apply(categorize_tss)

        fig, ax = plt.subplots(figsize=(6, 6), dpi=300)

        # Prepare data
        tss_range_pivot = df_temp.groupby(['Sequence ID', 'TSS Range']).size().unstack(fill_value=0)

        # Ensure correct order
        desired_order = ['Very Upstream', 'Upstream', 'Near End', 'Very Near End']
        existing_cols = [col for col in desired_order if col in tss_range_pivot.columns]
        tss_range_pivot = tss_range_pivot[existing_cols]

        # Professional color scheme - sequential colorblind-friendly
        colors = ['#5E3C99', '#B2ABD2', '#FDB863', '#E66101'][:len(existing_cols)]

        # Create grouped bar chart
        tss_range_pivot.plot(kind='bar', ax=ax, color=colors,
                            edgecolor='white', linewidth=0.5, width=0.75)

        # Styling
        ax.set_xlabel('')  # Remove x-axis label
        ax.set_ylabel('Match Count', fontsize=13, fontweight='bold')

        # Legend formatting - use value ranges instead of descriptive names
        range_mapping = {
            'Very Upstream': '< -1000',
            'Upstream': '[-1000, -500)',
            'Near End': '[-500, -100)',
            'Very Near End': '[-100, 0)'
        }
        legend_labels = [range_mapping.get(col, col) for col in existing_cols]
        ax.legend(legend_labels, title='TSS Range (bp)', title_fontsize=11,
                 frameon=True, fancybox=False, shadow=False,
                 loc='upper right', fontsize=11)

        # Grid and spines
        ax.grid(axis='y', alpha=0.3, linestyle='-', linewidth=0.5)
        ax.set_axisbelow(True)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)

        # Rotate x-axis labels
        plt.xticks(rotation=45, ha='right')

        # Tight layout
        plt.tight_layout()

        # Save as high-res JPEG
        output_path = os.path.join(output_dir, '7_TSS_Range_Categories_by_Sequence.jpg')
        plt.savefig(output_path, format='jpeg', dpi=300, bbox_inches='tight',
                   pil_kwargs={'quality': 95})
        chart_files['7_TSS_Range_Categories_by_Sequence'] = output_path
        plt.close(fig)
        print(f"      Saved to: {output_path}")

    return chart_files




def write_analysis_to_excel(input_file: str, output_file: str, all_analyses: Dict[str, Dict[str, pd.DataFrame]]):
    """
    Write all analyses to Excel file with only analysis sheets (no original data).

    Args:
        input_file: Original Excel file (not used, kept for backward compatibility)
        output_file: Output Excel file with analysis
        all_analyses: Dictionary of analysis categories and their DataFrames
    """
    # Create new workbook (don't preserve original data)
    wb = Workbook()
    wb.remove(wb.active)  # Remove default sheet

    # Write each analysis category as a new sheet
    for category, analyses in all_analyses.items():
        sheet_name = category[:31]  # Excel sheet name limit

        # Remove sheet if it already exists
        if sheet_name in wb.sheetnames:
            del wb[sheet_name]

        # Create new sheet
        ws = wb.create_sheet(sheet_name)

        # Write all sub-analyses for this category
        current_row = 1

        for analysis_name, df in analyses.items():
            # Add TSS range definition legend before TSS Ranges by Sequence table
            if analysis_name == 'TSS Ranges by Sequence':
                legend_text = [
                    "TSS Range Definitions:",
                    "• Very Upstream: < -1000 bp from sequence end",
                    "• Upstream: -1000 to -500 bp from sequence end",
                    "• Near End: -500 to -100 bp from sequence end",
                    "• Very Near End: -100 to 0 bp from sequence end",
                    "",
                    "Note: Negative values indicate distance upstream from the 3' end of the sequence"
                ]
                for i, line in enumerate(legend_text):
                    cell = ws.cell(row=current_row + i, column=1, value=line)
                    if i == 0:
                        cell.font = Font(bold=True, size=11, italic=True)
                    else:
                        cell.font = Font(size=10, italic=True)
                current_row += len(legend_text) + 2

            # Write analysis title
            ws.cell(row=current_row, column=1, value=analysis_name)
            ws.cell(row=current_row, column=1).font = Font(bold=True, size=14)
            current_row += 2

            # Write DataFrame
            for r_idx, row in enumerate(dataframe_to_rows(df, index=False, header=True)):
                for c_idx, value in enumerate(row, start=1):
                    cell = ws.cell(row=current_row + r_idx, column=c_idx, value=value)

                    # Format header row
                    if r_idx == 0:
                        cell.font = Font(bold=True)
                        cell.alignment = Alignment(horizontal='center')

            current_row += len(df) + 3  # Add spacing between analyses

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
    print(f"\nAnalysis complete! Results saved to {output_file}")
    print(f"Added {len(all_analyses)} analysis sheets")


def main():
    """Main function to run analysis."""
    parser = argparse.ArgumentParser(
        description='Analyze DNA/RNA sequence pattern search results',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Generates 4 types of analysis + visualizations:
1. Basic Counts: Pattern, mismatch, and gap statistics (including 4D Pattern×Mismatch×Gap×Sequence)
2. Position Sensitivity: TSS position analysis with range definitions
3. Gap Sensitivity: How gap size affects matches
4. Mismatch Sensitivity: Distribution and patterns of mismatches
5. Visualizations: 3 Nature-quality charts saved as 300 DPI JPEG files in output_charts folder:
   - Gap Size Distribution by Sequence (stacked bar chart)
   - Pattern × Sequence Heatmap
   - TSS Range Categories by Sequence (grouped bar chart)

Usage:
  python3.9 analyze_results.py input.xlsx output_analyzed.xlsx
  python3.9 analyze_results.py batch_results.xlsx batch_analyzed.xlsx --position-bin 50
  python3.9 analyze_results.py results.xlsx analyzed.xlsx --no-charts
        """
    )

    parser.add_argument('input_excel', help='Input Excel file from sequence_finder or batch_sequence_finder')
    parser.add_argument('output_excel', help='Output Excel file with analysis sheets')
    parser.add_argument('--position-bin', type=int, default=100,
                        help='Position bin size for position sensitivity analysis (default: 100)')
    parser.add_argument('--no-charts', action='store_true',
                        help='Skip generating visualization charts to output_charts folder (faster processing)')

    args = parser.parse_args()

    print(f"Analyzing results from: {args.input_excel}")
    print(f"Position bin size: {args.position_bin}\n")

    # Load results
    df = load_results(args.input_excel)

    # Perform all analyses
    print("\n" + "="*60)
    print("Running analyses...")
    print("="*60)

    all_analyses = {}

    print("\n1. Basic Counts Analysis...")
    basic_counts = analyze_basic_counts(df)
    if basic_counts:
        all_analyses['1_Basic_Counts'] = basic_counts
        print(f"   Generated {len(basic_counts)} summary tables")

    print("\n2. Position Sensitivity Analysis...")
    position_analysis = analyze_position_sensitivity(df, args.position_bin)
    if position_analysis:
        all_analyses['2_Position_Sensitivity'] = position_analysis
        print(f"   Generated {len(position_analysis)} summary tables")

    print("\n3. Gap Sensitivity Analysis...")
    gap_analysis = analyze_gap_sensitivity(df)
    if gap_analysis:
        all_analyses['3_Gap_Sensitivity'] = gap_analysis
        print(f"   Generated {len(gap_analysis)} summary tables")

    print("\n4. Mismatch Sensitivity Analysis...")
    mismatch_analysis = analyze_mismatch_sensitivity(df)
    if mismatch_analysis:
        all_analyses['4_Mismatch_Sensitivity'] = mismatch_analysis
        print(f"   Generated {len(mismatch_analysis)} summary tables")

    # Generate visualization charts (unless --no-charts flag is set)
    if not args.no_charts:
        print("\n5. Generating Visualization Charts...")
        try:
            chart_files = generate_charts(df)
            if chart_files:
                print(f"   Generated {len(chart_files)} Nature-quality charts:")
                for chart_name, file_path in chart_files.items():
                    print(f"      - {file_path}")
        except Exception as e:
            print(f"   Warning: Chart generation failed: {e}")
            print(f"   Continuing with analysis tables only...")
    else:
        print("\n5. Skipping chart generation (--no-charts flag set)")

    # Write all analyses to Excel
    print("\n" + "="*60)
    print("Writing analysis to Excel...")
    print("="*60)
    write_analysis_to_excel(args.input_excel, args.output_excel, all_analyses)


if __name__ == '__main__':
    main()

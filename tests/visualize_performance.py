#!/usr/bin/env python3
"""
Visualize RAG MCQ Agent performance: Baseline vs Improved.
Shows the accuracy-latency trade-off in a publishable-quality scatter plot.
Uses Hippocratic AI branding and color scheme.
"""

import csv
import matplotlib.pyplot as plt
import os
import sys

# Add parent directory to path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

# Hippocratic AI color scheme
COLORS = {
    'cyan': '#31f2fe',
    'green': '#17cc45',
    'dark': '#32373c',
    'gray': '#9CA3AF'
}


def load_summary_data(csv_path: str):
    """Load summary data from CSV file."""
    data = {}
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['type'] not in ('baseline', 'parallel_processing'):
                continue

            data[row['type']] = {
                'accuracy_percentage': float(row['accuracy_percentage']),
                'avg_latency_seconds': float(row['avg_latency_seconds']),
                'total_questions': int(row['total_questions']),
                'correct_count': int(row['correct_count']),
                'questions_per_second': float(row['questions_per_second'])
            }
    return data


def create_visualization(data, output_path: str):
    """Create publishable-quality 2D scatter plot with Hippocratic AI branding."""

    # Define configurations and their visual properties
    configs = {
        'baseline': {
            'label': 'Baseline',
            'color': COLORS['green'],
            'marker': 'o',
            'size': 200,
            'zorder': 2
        },
        'parallel_processing': {
            'label': 'Improved',
            'color': COLORS['cyan'],
            'marker': 'o',
            'size': 200,
            'zorder': 5
        }
    }

    # Filter available configurations
    available_configs = {k: v for k, v in configs.items() if k in data}

    if not available_configs:
        print("Error: No valid configuration data found")
        return

    # Create figure with white background
    fig, ax = plt.subplots(figsize=(5, 5), facecolor='white')
    ax.set_facecolor('white')

    # Extract data for plotting
    latencies = []
    accuracies = []

    for config_key, config_props in available_configs.items():
        config_data = data[config_key]
        lat = config_data['avg_latency_seconds']
        acc = config_data['accuracy_percentage']

        latencies.append(lat)
        accuracies.append(acc)

        # Plot point
        ax.scatter(lat, acc,
                  s=config_props['size'],
                  c=config_props['color'],
                  marker=config_props['marker'],
                  edgecolors=COLORS['dark'],
                  linewidths=2,
                  label=config_props['label'],
                  zorder=config_props['zorder'])

        # Annotate the label above each point
        ax.annotate(
            config_props['label'],
            xy=(lat, acc),
            xytext=(0, 12),
            textcoords='offset points',
            ha='center',
            va='bottom',
            fontsize=10,
            fontweight='bold',
            color=COLORS['dark'],
            bbox=dict(boxstyle="round,pad=0.3", fc="white", ec=COLORS['gray'], lw=0.7, alpha=0.8)
        )

    # Set axis labels with Hippocratic AI styling
    ax.set_xlabel('Latency per question (s)',
                  fontsize=10,
                  fontweight='600',
                  color=COLORS['dark'])
    ax.set_ylabel('Accuracy (%)',
                  fontsize=10,
                  fontweight='600',
                  color=COLORS['dark'])

    # Add subtle grid
    ax.grid(True, alpha=0.15, linestyle='-', linewidth=0.8, color=COLORS['gray'])
    ax.set_axisbelow(True)

    # Set axis limits with appropriate padding
    x_range = max(latencies) - min(latencies)
    y_range = max(accuracies) - min(accuracies)

    x_margin = x_range * 0.15 if x_range > 0 else 0.1
    y_margin = max(y_range * 0.15, 5)

    ax.set_xlim(min(latencies) - x_margin, max(latencies) + x_margin)
    ax.set_ylim(min(accuracies) - y_margin, min(100, max(accuracies) + y_margin))

    # Customize legend with rounded corners
    # legend = ax.legend(loc='upper right',
    #                   fontsize=11,
    #                   framealpha=0.98,
    #                   edgecolor=COLORS['gray'],
    #                   fancybox=True,
    #                   shadow=False,
    #                   frameon=True,
    #                   borderpad=1,
    #                   labelspacing=0.8)
    # legend.get_frame().set_facecolor('white')
    # legend.get_frame().set_linewidth(1.5)

    # Customize spines
    for spine in ax.spines.values():
        spine.set_edgecolor(COLORS['gray'])
        spine.set_linewidth(1.2)

    # Customize ticks
    ax.tick_params(colors=COLORS['dark'], which='both', labelsize=11)

    # Add subtle footer with branding
    fig.text(0.99, -0.02, 'Hippocratic AI Coding Project',
            ha='right',
            va='bottom',
            fontsize=9,
            color=COLORS['gray'],
            style='italic',
            alpha=0.7)

    # Save with high quality
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white', edgecolor='none')
    print(f"✓ High-resolution visualization saved to: {output_path}")

    # Print comprehensive summary
    print("\n" + "="*70)
    print("RAG MCQ AGENT PERFORMANCE SUMMARY")
    print("="*70)

    for config_key in available_configs.keys():
        config_data = data[config_key]
        config_props = configs[config_key]

        print(f"\n{config_props['label']}:")
        print(f"  Accuracy:    {config_data['accuracy_percentage']:.1f}%")
        print(f"  Latency:     {config_data['avg_latency_seconds']:.3f}s")
        print(f"  Throughput:  {config_data['questions_per_second']:.2f} questions/sec")

    # Calculate and show improvements from baseline
    if 'baseline' in data:
        baseline = data['baseline']
        print(f"\n" + "-"*70)
        print("IMPROVEMENTS FROM BASELINE")
        print("-"*70)

        for config_key in available_configs.keys():
            if config_key == 'baseline':
                continue

            config_data = data[config_key]
            config_props = configs[config_key]

            acc_gain = config_data['accuracy_percentage'] - baseline['accuracy_percentage']
            lat_change = ((config_data['avg_latency_seconds'] - baseline['avg_latency_seconds'])
                         / baseline['avg_latency_seconds'] * 100)
            throughput_gain = config_data['questions_per_second'] / baseline['questions_per_second']

            print(f"\n{config_props['label']}:")
            print(f"  Accuracy:    {acc_gain:+.1f} pp ({acc_gain/baseline['accuracy_percentage']*100:+.1f}%)")
            print(f"  Latency:     {lat_change:+.1f}% ({abs(1/(1+lat_change/100)):.1f}× {'faster' if lat_change < 0 else 'slower'})")
            print(f"  Throughput:  {throughput_gain:.2f}× baseline")

    print("="*70 + "\n")

    plt.close()


if __name__ == "__main__":
    # Get paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    summary_path = os.path.join(script_dir, 'benchmark_results', 'summary.csv')
    output_path = os.path.join(script_dir, 'benchmark_results', 'performance_comparison.png')
    
    # Load data
    data = load_summary_data(summary_path)
    
    # Create visualization
    create_visualization(data, output_path)


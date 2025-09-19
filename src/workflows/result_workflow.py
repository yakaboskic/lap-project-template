#!/usr/bin/env python3
"""
Result Generation Workflow Template
Handles operations for the 'result' class in LAP pipeline

This workflow is designed to run with `uv run` for dependency management.
Commands should use: uv run --project /path/to/project src/workflows/result_workflow.py

This workflow generates reports, visualizations, and summaries from analysis results.
"""

import argparse
import logging
import sys
import json
from pathlib import Path
import pandas as pd

# Add modules directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "modules"))

# Import your custom modules (create these as needed)
# from plotting import create_report_plots
# from reporting import generate_html_report

def handle_stage_report(args):
    """Generate comprehensive HTML report"""
    logging.info("Generating HTML report")

    try:
        # Load analysis results
        logging.info(f"Loading analysis results from: {args.input_file}")
        df = pd.read_csv(args.input_file, sep='\t')

        # Check for corresponding JSON file with metadata
        json_file = Path(args.input_file).with_suffix('.json')
        metadata = {}
        if json_file.exists():
            with open(json_file, 'r') as f:
                metadata = json.load(f)

        # Generate HTML report
        html_content = generate_html_report(df, metadata, args.project_name)

        # Save HTML report
        output_path = Path(args.output_html)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(args.output_html, 'w') as f:
            f.write(html_content)

        # Generate plots if output plots file is specified
        if hasattr(args, 'output_plots') and args.output_plots:
            create_analysis_plots(df, args.output_plots)

        logging.info(f"Report generated successfully: {args.output_html}")

    except Exception as e:
        logging.error(f"Report generation failed: {e}")
        sys.exit(1)

def generate_html_report(df, metadata, project_name):
    """Generate HTML report content"""

    # Basic HTML template
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Analysis Report - {project_name}</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; }}
            h1, h2 {{ color: #333; }}
            table {{ border-collapse: collapse; width: 100%; }}
            th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
            th {{ background-color: #f2f2f2; }}
            .summary {{ background-color: #f9f9f9; padding: 20px; margin: 20px 0; }}
        </style>
    </head>
    <body>
        <h1>Analysis Report: {project_name}</h1>

        <div class="summary">
            <h2>Summary</h2>
            <p><strong>Total Results:</strong> {len(df)}</p>
    """

    if metadata:
        html += f"""
            <p><strong>Analysis Type:</strong> {metadata.get('analysis_type', 'Unknown')}</p>
            <p><strong>Significant Results:</strong> {metadata.get('n_significant_results', 'Unknown')}</p>
            <p><strong>Status:</strong> {metadata.get('analysis_status', 'Unknown')}</p>
        """

    html += """
        </div>

        <h2>Top Results</h2>
        <table>
    """

    # Add table headers
    if not df.empty:
        html += "<tr>"
        for col in df.columns:
            html += f"<th>{col}</th>"
        html += "</tr>"

        # Add top 10 rows
        for _, row in df.head(10).iterrows():
            html += "<tr>"
            for col in df.columns:
                value = row[col]
                # Format p-values in scientific notation if they're very small
                if col.lower().endswith('p_value') and isinstance(value, (int, float)) and value < 0.001:
                    html += f"<td>{value:.2e}</td>"
                else:
                    html += f"<td>{value}</td>"
            html += "</tr>"

    html += """
        </table>

        <h2>Analysis Details</h2>
        <p>This report was generated automatically by the LAP pipeline.</p>
        <p>For questions or issues, please contact the analysis team.</p>
    </body>
    </html>
    """

    return html

def create_analysis_plots(df, output_file):
    """Create analysis plots (placeholder implementation)"""
    logging.info(f"Creating plots: {output_file}")

    try:
        import matplotlib.pyplot as plt

        # Create a simple plot as an example
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

        # Plot 1: Distribution of p-values (if available)
        if 'p_value' in df.columns:
            ax1.hist(df['p_value'], bins=20, alpha=0.7)
            ax1.set_xlabel('P-value')
            ax1.set_ylabel('Frequency')
            ax1.set_title('Distribution of P-values')
        else:
            ax1.text(0.5, 0.5, 'No p-value column found', ha='center', va='center')
            ax1.set_title('P-value Plot Not Available')

        # Plot 2: Effect size distribution (if available)
        if 'effect_size' in df.columns:
            ax2.hist(df['effect_size'], bins=20, alpha=0.7, color='orange')
            ax2.set_xlabel('Effect Size')
            ax2.set_ylabel('Frequency')
            ax2.set_title('Distribution of Effect Sizes')
        else:
            ax2.text(0.5, 0.5, 'No effect_size column found', ha='center', va='center')
            ax2.set_title('Effect Size Plot Not Available')

        plt.tight_layout()

        # Save plots
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.close()

        logging.info(f"Plots saved to: {output_file}")

    except ImportError:
        logging.warning("matplotlib not available - skipping plot generation")
        # Create empty file to satisfy LAP dependencies
        Path(output_file).touch()
    except Exception as e:
        logging.error(f"Plot generation failed: {e}")
        # Create empty file to satisfy LAP dependencies
        Path(output_file).touch()

def main():
    """Main workflow entry point"""
    logging.basicConfig(
        level=logging.INFO,
        format='[%(levelname)s] %(asctime)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    parser = argparse.ArgumentParser(
        prog='result_workflow',
        description='Result generation workflow for LAP pipeline'
    )

    # Global options
    parser.add_argument('--verbose', action='store_true',
                      help='Enable verbose logging')

    # Create subparsers for different stages
    subparsers = parser.add_subparsers(dest='command', required=True,
                                     help='Available workflow stages')

    # Report generation stage
    parser_report = subparsers.add_parser('report',
                                        help='Generate HTML report')
    parser_report.add_argument('--input-file', required=True,
                             help='Analysis results file (TSV format)')
    parser_report.add_argument('--output-html', required=True,
                             help='Output HTML report file')
    parser_report.add_argument('--output-plots',
                             help='Output plots file (PDF format)')
    parser_report.add_argument('--project-name', required=True,
                             help='Project name for report title')

    # Parse arguments
    args = parser.parse_args()

    # Set up verbose logging if requested
    if hasattr(args, 'verbose') and args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Route to appropriate handler
    try:
        if args.command == 'report':
            handle_stage_report(args)
        else:
            parser.print_help()
            sys.exit(1)

    except KeyboardInterrupt:
        logging.info("Workflow interrupted by user")
        sys.exit(1)
    except Exception as e:
        logging.error(f"Workflow failed with unexpected error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
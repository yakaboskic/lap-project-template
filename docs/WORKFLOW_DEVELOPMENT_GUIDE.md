# Opinionated LAP Workflow Development Guide

This guide outlines the recommended approach for developing LAP pipelines using a workflow-based architecture that emphasizes modularity, maintainability, and atomic operations.

## Philosophy: Atomic Pipeline Development

### The Problem with Monolithic Commands

A common antipattern in pipeline development is creating commands that do too much:

```cfg
# ANTIPATTERN: Monolithic command
cmd analyze_and_plot_cmd=python analyze.py \
    --input !{input::data_file} \
    --do-complex-calculation \
    --generate-intermediate-results \
    --create-summary-stats \
    --make-plots \
    --output-html !{output::final_report}
```

**Problems:**
- If you want to modify just the plotting, you must re-run the entire expensive calculation
- Debugging is difficult - which step failed?
- No intermediate outputs to inspect
- Cannot parallelize or optimize individual steps
- Violates single responsibility principle

### The Solution: Atomic Workflow Stages

Break each major operation into atomic, single-purpose stages:

```cfg
# GOOD: Atomic stages
cmd calculate_results_cmd=python analyze.py \
    --input !{input::data_file} \
    --output !{output::calculation_results}; \
    class_level analysis

cmd generate_summary_cmd=python summarize.py \
    --input !{input::calculation_results} \
    --output !{output::summary_stats}; \
    class_level analysis

cmd create_plots_cmd=python plot.py \
    --input !{input::summary_stats} \
    --output !{output::plots_html}; \
    class_level analysis
```

**Benefits:**
- Each stage can be run independently
- Easy to modify plotting without recalculating
- Clear intermediate outputs for debugging
- Parallelizable where dependencies allow
- Testable in isolation

## Workflow Architecture Pattern

### One Workflow Per Class

Each LAP class should have a corresponding workflow script that handles all operations for that class:

```
src/
├── workflows/
│   ├── trait_analysis_workflow.py     # For 'trait' class
│   ├── model_validation_workflow.py   # For 'model' class
│   └── result_processing_workflow.py  # For 'result' class
└── modules/
    ├── statistics.py                   # Reusable statistical functions
    ├── plotting.py                     # Reusable plotting functions
    └── file_utils.py                   # File I/O utilities
```

### Workflow Structure Using Argparse Subparsers

Each workflow should use argparse subparsers to define stages:

```python
#!/usr/bin/env python3
"""
Trait Analysis Workflow
Handles all operations for the 'trait' class in LAP pipeline
"""

import argparse
import logging
import sys
from pathlib import Path

# Import reusable modules
sys.path.append(str(Path(__file__).parent.parent / "modules"))
from statistics import calculate_gwas_stats
from plotting import create_manhattan_plot
from file_utils import validate_input_file

def handle_stage_gwas_qc(args):
    """Stage 1: Perform GWAS quality control"""
    logging.info("Starting GWAS QC stage")

    # Validate inputs
    validate_input_file(args.input_file)

    # Perform QC
    qc_results = perform_gwas_qc(
        input_file=args.input_file,
        maf_threshold=args.maf_threshold,
        info_threshold=args.info_threshold
    )

    # Write output
    qc_results.to_csv(args.output_file, sep='\t', index=False)
    logging.info(f"QC complete. Results written to {args.output_file}")

def handle_stage_calculate_stats(args):
    """Stage 2: Calculate summary statistics"""
    logging.info("Calculating summary statistics")

    # Use imported module function
    stats = calculate_gwas_stats(args.input_file)

    # Write results
    with open(args.output_file, 'w') as f:
        json.dump(stats, f, indent=2)

def handle_stage_create_plots(args):
    """Stage 3: Generate visualization plots"""
    logging.info("Creating plots")

    # Create plots using reusable plotting module
    create_manhattan_plot(
        input_file=args.input_file,
        output_file=args.output_file,
        title=args.trait_name
    )

def handle_stage_all(args):
    """Run all stages in sequence"""
    logging.info("Running complete workflow")

    # This could orchestrate running all stages
    # with intermediate file management
    pass

def main():
    """Main workflow entry point"""
    logging.basicConfig(
        level=logging.INFO,
        format='[%(levelname)s] %(asctime)s - %(message)s'
    )

    parser = argparse.ArgumentParser(
        prog='trait_analysis_workflow',
        description='Trait analysis workflow for LAP pipeline'
    )

    # Global options
    parser.add_argument('--verbose', action='store_true', help='Enable verbose logging')

    # Create subparsers for different stages
    subparsers = parser.add_subparsers(dest='command', required=True)

    # Stage 1: GWAS QC
    parser_qc = subparsers.add_parser('gwas-qc', help='Perform GWAS quality control')
    parser_qc.add_argument('--input-file', required=True, help='Input GWAS file')
    parser_qc.add_argument('--output-file', required=True, help='QC output file')
    parser_qc.add_argument('--maf-threshold', type=float, default=0.01, help='MAF threshold')
    parser_qc.add_argument('--info-threshold', type=float, default=0.8, help='INFO threshold')

    # Stage 2: Calculate statistics
    parser_stats = subparsers.add_parser('calculate-stats', help='Calculate summary statistics')
    parser_stats.add_argument('--input-file', required=True, help='QC\'d GWAS file')
    parser_stats.add_argument('--output-file', required=True, help='Statistics output file')

    # Stage 3: Create plots
    parser_plot = subparsers.add_parser('create-plots', help='Generate visualization plots')
    parser_plot.add_argument('--input-file', required=True, help='Statistics file')
    parser_plot.add_argument('--output-file', required=True, help='Plot output file')
    parser_plot.add_argument('--trait-name', required=True, help='Trait name for title')

    # All stages
    parser_all = subparsers.add_parser('all', help='Run complete workflow')
    # Add all required arguments for complete workflow

    # Parse arguments
    args = parser.parse_args()

    # Set up verbose logging if requested
    if hasattr(args, 'verbose') and args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Route to appropriate handler
    if args.command == 'gwas-qc':
        handle_stage_gwas_qc(args)
    elif args.command == 'calculate-stats':
        handle_stage_calculate_stats(args)
    elif args.command == 'create-plots':
        handle_stage_create_plots(args)
    elif args.command == 'all':
        handle_stage_all(args)
    else:
        parser.print_help()
        sys.exit(1)

if __name__ == '__main__':
    main()
```

## LAP Integration Pattern

### Mapping LAP Commands to Workflow Stages

Each LAP command should map to exactly one workflow stage:

```cfg
# LAP config file commands using uv for Python environment management
local cmd gwas_qc_cmd=$run_uv_cmd src/workflows/trait_analysis_workflow.py gwas-qc \
    --input-file !{input::trait_gwas_file} \
    --output-file !{output::trait_qc_file} \
    --maf-threshold 0.01; \
    class_level trait

local cmd calculate_stats_cmd=$run_uv_cmd src/workflows/trait_analysis_workflow.py calculate-stats \
    --input-file !{input::trait_qc_file} \
    --output-file !{output::trait_stats_file}; \
    class_level trait

local cmd create_plots_cmd=$run_uv_cmd src/workflows/trait_analysis_workflow.py create-plots \
    --input-file !{input::trait_stats_file} \
    --output-file !{output::trait_plots_file} \
    --trait-name !{prop::trait}; \
    class_level trait
```

### File Dependency Chain

The atomic stages create a clear dependency chain:

```
trait_gwas_file → [gwas-qc] → trait_qc_file → [calculate-stats] → trait_stats_file → [create-plots] → trait_plots_file
```

This allows LAP to:
- Only run stages when inputs change
- Parallelize independent branches
- Resume from any point in the pipeline
- Provide clear intermediate outputs for debugging

## Module Development Guidelines

### Reusable Modules Structure

Create focused, reusable modules in `src/modules/`:

```python
# src/modules/statistics.py
"""Statistical analysis functions for LAP workflows"""

import pandas as pd
import numpy as np

def calculate_gwas_stats(gwas_file):
    """Calculate summary statistics from GWAS results"""
    df = pd.read_csv(gwas_file, sep='\t')

    stats = {
        'n_variants': len(df),
        'n_significant': len(df[df['P'] < 5e-8]),
        'lambda_gc': calculate_lambda_gc(df['P']),
        'mean_chi2': calculate_mean_chi2(df['P'])
    }

    return stats

def calculate_lambda_gc(p_values):
    """Calculate genomic control lambda"""
    chi2_values = -2 * np.log(p_values)
    return np.median(chi2_values) / 0.455
```

### Module Testing

Each module should be independently testable:

```python
# tests/test_statistics.py
import unittest
from src.modules.statistics import calculate_gwas_stats

class TestStatistics(unittest.TestCase):
    def test_calculate_gwas_stats(self):
        # Test with mock data
        stats = calculate_gwas_stats('tests/data/mock_gwas.tsv')
        self.assertIn('n_variants', stats)
        self.assertGreater(stats['lambda_gc'], 0)
```

## Directory Structure

Organize your LAP project with clear separation:

```
my-lap-project/
├── config/
│   ├── starter.cfg              # Main pipeline configuration
│   ├── starter.meta             # Instance definitions
│   └── examples/                # Example configurations
├── src/
│   ├── workflows/               # Workflow scripts (one per LAP class)
│   │   ├── trait_workflow.py
│   │   ├── model_workflow.py
│   │   └── result_workflow.py
│   └── modules/                 # Reusable utility modules
│       ├── __init__.py
│       ├── statistics.py
│       ├── plotting.py
│       ├── file_utils.py
│       └── validation.py
├── raw/                         # Raw input data
├── out/                         # Pipeline outputs
├── log/                         # Pipeline logs
├── tests/                       # Unit tests
├── docs/                        # Documentation
├── requirements.txt             # Python dependencies
└── README.md                    # Project overview
```

## Development Workflow

### 1. Design Phase
- Identify the major computational steps
- Define input/output files for each step
- Plan the LAP class hierarchy
- Sketch the dependency graph

### 2. Implementation Phase
- Create workflow scripts with subparser structure
- Implement atomic stages one at a time
- Build reusable modules as needed
- Write corresponding LAP commands

### 3. Testing Phase
- Test individual stages in isolation
- Test complete workflows
- Validate with real data
- Check LAP dependency resolution

### 4. Integration Phase
- Create LAP configuration files
- Define meta file instances
- Test full pipeline execution
- Document usage and requirements

## Best Practices

### 1. Stage Granularity
- Each stage should do one logical operation
- Stages should be fast enough that re-running isn't painful (~minutes, not hours)
- Balance between too many micro-stages and monolithic mega-stages

### 2. Error Handling
```python
def handle_stage_analysis(args):
    try:
        # Validate inputs
        if not Path(args.input_file).exists():
            raise FileNotFoundError(f"Input file not found: {args.input_file}")

        # Perform analysis
        result = analyze_data(args.input_file)

        # Validate outputs
        if result is None:
            raise ValueError("Analysis returned no results")

        # Write output
        result.to_csv(args.output_file)

    except Exception as e:
        logging.error(f"Stage failed: {e}")
        sys.exit(1)
```

### 3. Logging
- Use structured logging with timestamps
- Log start/completion of each stage
- Log key parameters and file sizes
- Include performance metrics where relevant

### 4. Configuration Management
- Use argparse for all parameters
- Provide sensible defaults
- Document all parameters clearly
- Consider configuration files for complex parameter sets

This workflow-based approach ensures your LAP pipelines are maintainable, debuggable, and efficient. Each component can be developed and tested in isolation, while the overall system benefits from LAP's dependency management and execution orchestration.
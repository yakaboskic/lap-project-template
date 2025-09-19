# LAP Pipeline Syntax Guide

This guide provides comprehensive documentation for the Lightweight Analysis Pipeline (LAP) configuration and meta file syntax.

## Overview

LAP pipelines are defined using two main files:
- **Config File (.cfg)**: Defines the pipeline architecture, classes, files, commands, and properties
- **Meta File (.meta)**: Instantiates specific instances of classes and assigns property values

LAP operates as a **file-based pipeline system** with no shared memory architecture. All data flows through input and output files, creating a dependency tree that determines execution order.

## Core Concepts

### 1. Classes
Classes define hierarchical levels at which files are created and commands are run. Each class can have:
- **Parent-child relationships**: Creating a tree structure
- **Properties**: Accessible via `@classname` syntax
- **Instance data**: Each class can have multiple instances

```cfg
# Basic class definition
class project=Project
class validation=Validation parent project
class trait=Trait parent validation
```

### 2. Files
Files define input and output data at specific class levels:

```cfg
# File definition syntax
path file filename=path/to/file.ext dir directory_name disp "Display Name" parent category_name class_level classname

# Examples
path file models_config_file=@validation.models_config_file.yaml dir project_dir disp "Model Configurations" parent validation_cat class_level validation
table path file phenotype_file=@validation.phenotypes.tsv dir project_dir disp "Phenotypes" parent validation_cat class_level validation
```

**File Attributes:**
- `path`: Indicates this is a file path
- `file`: File type declaration
- `table`: Optional prefix for tabular data files
- `dir`: Directory where file resides
- `disp`: Display name for web UI
- `parent`: Category for organization
- `class_level`: Which class this file belongs to

### 3. Directories
Directories define the filesystem structure:

```cfg
# Directory syntax
sortable mkdir path directory_name=path/structure class_level classname

# Examples
sortable mkdir path project_dir=$projects_dir/@project class_level project
sortable mkdir path validation_dir=$project_dir/@validation class_level validation
```

**Directory Attributes:**
- `sortable`: Files can be sorted in web UI
- `mkdir`: Create directory during initialization
- `path`: Unix filesystem path
- `class_level`: Associated class

### 4. Commands
Commands define the computational steps:

```cfg
# Command syntax
short cmd command_name=command_definition class_level classname run_if conditions

# Example
short cmd model_selection_analysis_cmd=$run_uv_cmd \
    $pigean_bin_dir/model_selection_analysis.py \
    !{input:--config:models_config_file} \
    !{output:--output-plot-file:model_selection_plot_out_file} \
    --mechanism-metric-name ndcg \
    class_level validation run_if validation:eq:geneset_analysis
```

**Command Attributes:**
- `short`/`long`/`local`: Execution type
- `cmd`: Command declaration
- `class_level`: Which class this command runs on
- `run_if`: Conditional execution

### 5. Properties
Properties store scalar values that can be referenced throughout the pipeline:

```cfg
# Property definition
prop property_name=scalar

# Usage in commands
!{prop:--model-name:model}
```

## File Reference Syntax

LAP uses special syntax for referencing files and properties:

### Input Files
```cfg
!{input:--flag:filename}                    # Basic input reference
!{input:--flag:filename:optional=1}         # Optional input
!{input:--flag:filename:allow_empty=1}      # Allow empty files
!{input;--flag;filename;if_prop=condition}  # Conditional input
```

### Output Files
```cfg
!{output:--flag:filename}                   # Basic output reference
!{output::filename}                         # Output without flag
```

### Properties
```cfg
!{prop:--flag:classname:property}           # Property reference
!{prop:--flag:classname}                    # Class instance name
```

### Raw References
```cfg
!{raw::classname:*trunk_variable}           # Raw path reference
```

## Meta File Syntax (.meta)

Meta files instantiate classes and assign property values. We **strongly recommend** using the meta-sanity YAML format for maintainability and readability.

### Meta-Sanity YAML Format (Recommended)
```yaml
config: "/path/to/config.cfg"

keys:
  base_dir: "/path/to/project"
  unix_out_dir: "${base_dir}/out"
  log_dir: "${base_dir}/log"

classes:
  my_project:
    class: project
    parent: null

  geneset_analysis:
    class: validation
    parent: my_project
    properties:
      models_config_file: "${raw_dir}/model-info.yaml"
      phenotype_file: "${raw_dir}/Phenotypes.tsv"

templates:
  common_traits:
    class: trait
    operation: for_each_item
    input:
      - T2D
      - BMI
      - HEIGHT
    pattern:
      name: "${item}"
      properties:
        trait_gwas_file: "${gwas_dir}/${item}.sumstats.gz"
    parent: geneset_analysis
```

Generate the traditional LAP meta file:
```bash
meta-sanity generate-meta config/my-project.meta.yaml config/my-project.meta
```

### Traditional Meta File Format (Legacy)
While still supported, traditional meta files are harder to maintain:
```meta
# Set global paths
unix_out_dir=/path/to/output
log_dir=/path/to/logs

# Instantiate classes
project	my_project
validation	geneset_analysis	parent=my_project
model	full_model	parent=geneset_analysis
trait	T2D	parent=geneset_analysis	trait_gwas_file=/data/T2D.sumstats.gz
```

**Note**: For new projects, use the YAML format above instead of this legacy format.

## Variable and Path Resolution

### Variable Types
1. **Global variables**: Defined at top level
2. **Class properties**: Accessible via `@classname`
3. **File paths**: Resolved through directory structure
4. **Command substitutions**: Shell-style `$()` syntax

### Path Resolution Examples
```cfg
# Variable definition
gwas_dir=/data/gwas
project_dir=$unix_out_dir/projects/@project

# File with variable substitution
trait_gwas_file=@trait.sumstats.gz dir trait_dir

# Command with path resolution
output_dir=$(dirname !{raw::experiment:*experiment_trunk})
```

## Categories and Web UI

Categories organize files in the web interface:

```cfg
cat validation_cat=null disp "Validation files" class_level validation
cat trait_cat=null disp "Trait files" class_level trait
```

## Command Patterns

### Conditional Execution
```cfg
run_if validation:eq:geneset_analysis           # Single condition
run_if and,validation:eq:p_validation,results:ne:p_results  # Multiple conditions
run_if or,trait_group:eq:common,trait_group:eq:rare        # OR conditions
```

### File Processing Patterns
```cfg
# Concatenating multiple files
first=1; \
for f in !{input::input_files:optional=1}; do \
    if [[ -s "\$f" ]]; then \
        if [[ \$first -eq 1 ]]; then \
            head -n 1 "\$f" > !{output::output_file}; \
            first=0; \
        fi; \
        tail -n +2 "\$f" >> !{output::output_file}; \
    fi; \
done
```

## Advanced Features

### Multi-line Commands
Commands can span multiple lines using backslash continuation:

```cfg
short cmd long_command_cmd=step1_command \
    --input !{input:--file:input_file} \
    --output !{output:--result:output_file} \
    --parameter value; \
    class_level validation
```

### Environment Management
```cfg
# Virtual environment activation
short cmd python_cmd=source /path/to/venv/bin/activate && \
    python script.py !{input:--input:file}; \
    class_level validation
```

### Resource Management
```cfg
# Memory and time specifications
default_mem=10000
max_jobs=1000
bsub_opts=-pe smp 1
```

## Include System

Config files can include common configurations:

```cfg
# Include common settings
!include $lap_trunk/config/common.cfg

# Override specific settings
max_jobs=500
default_mem=8000
```

## Best Practices

1. **File Organization**: Use clear directory hierarchies
2. **Naming Conventions**: Use descriptive file and command names
3. **Error Handling**: Always check for file existence in commands
4. **Resource Planning**: Specify appropriate memory and time limits
5. **Documentation**: Use `disp` attributes for clear file descriptions
6. **Modularity**: Break complex workflows into atomic commands
7. **Conditional Logic**: Use `run_if` to create flexible pipelines

## Common Patterns

### Input Validation
```cfg
if [[ ! -f "!{input::required_file}" ]]; then
    echo "Error: Required input file not found" >&2
    exit 1
fi
```

### Parallel Processing
```cfg
# Run multiple commands in parallel
command1 &
command2 &
command3 &
wait  # Wait for all background jobs
```

### Temporary Files
```cfg
temp_file=$(mktemp)
trap "rm -f $temp_file" EXIT
```

This syntax guide covers the essential elements of LAP pipeline configuration. For specific implementation examples, refer to the example configurations in the `examples/` directory.
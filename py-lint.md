---
name: py-lint
description: Run Python linting workflow (autoflake, ruff format, isort) on Python files
disable-model-invocation: true
argument-hint: [directory]
---

Run Python linting workflow on the project.

## Workflow

1. Find all Python files in the project (excluding .venv directories)
2. Run the following tools in order:
   - `autoflake --in-place --remove-unused-variables --remove-all-unused-imports`
   - `ruff format`
   - `isort`

## Script

```zsh
#!/bin/zsh
export SRC_DIR=${1:-$ARGUMENTS}

# Default to current directory if no argument provided
if [ -z "$SRC_DIR" ]; then
    SRC_DIR=$(pwd)
fi

# Find Python files
FILES=($(find "${SRC_DIR}" -type f -name "*.py" -not -path "*.venv*"))

echo "Found ${#FILES[@]} Python files"

# Check for parallel
if command -v parallel &> /dev/null; then
    TEMP_SCRIPT=$(mktemp)
    cat > "$TEMP_SCRIPT" << 'EOF'
#!/bin/zsh
FILE="$1"
autoflake --in-place --remove-unused-variables --remove-all-unused-imports "$FILE"
ruff format "$FILE"
isort "$FILE"
EOF
    chmod +x "$TEMP_SCRIPT"
    printf "%s\n" "${FILES[@]}" | parallel "$TEMP_SCRIPT"
    rm "$TEMP_SCRIPT"
else
    for FILE in "${FILES[@]}"; do
        echo "Processing $FILE"
        autoflake --in-place --remove-unused-variables --remove-all-unused-imports "$FILE"
        ruff format "$FILE"
        isort "$FILE"
    done
fi

echo "Done!"
```

## Requirements

- autoflake, ruff, isort must be installed
- If any tool is missing, report error

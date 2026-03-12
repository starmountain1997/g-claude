#!/bin/zsh
set -euo pipefail

# Target directory is the first argument, or current directory if empty
SRC_DIR="${1:-.}"

if [ ! -d "$SRC_DIR" ]; then
    echo "Error: Directory '$SRC_DIR' does not exist."
    exit 1
fi

# Find Python files (excluding .venv, .git, and common cache dirs)
FILES=($(find "${SRC_DIR}" -type f -name "*.py" \
    -not -path "*/.venv/*" \
    -not -path "*/.git/*" \
    -not -path "*/__pycache__/*" \
    -not -path "*/.pytest_cache/*" \
    -not -path "*/.ruff_cache/*"))

if [ ${#FILES[@]} -eq 0 ]; then
    echo "No Python files found in $SRC_DIR"
    exit 0
fi

echo "Found ${#FILES[@]} Python files"

# Format function
format_file() {
    local file="$1"
    echo "Processing $file"
    autoflake --in-place --remove-unused-variables --remove-all-unused-imports "$file"
    ruff format "$file"
    isort "$file"
}

# autoflake, ruff format, isort
echo "Running autoflake, ruff format, isort..."
if command -v parallel &> /dev/null; then
    # Create a temporary script for parallel execution
    TEMP_SCRIPT=$(mktemp)
    cat > "$TEMP_SCRIPT" << 'EOF'
#!/bin/zsh
file="$1"
autoflake --in-place --remove-unused-variables --remove-all-unused-imports "$file"
ruff format "$file"
isort "$file"
EOF
    chmod +x "$TEMP_SCRIPT"
    printf "%s\n" "${FILES[@]}" | parallel "$TEMP_SCRIPT"
    rm "$TEMP_SCRIPT"
else
    for file in "${FILES[@]}"; do
        format_file "$file"
    done
fi

echo "Successfully formatted ${#FILES[@]} files."

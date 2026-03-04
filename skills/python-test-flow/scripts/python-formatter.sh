#!/bin/zsh
export SRC_DIR=${1:-$ARGUMENTS}

# Default to current directory if no argument provided
if [ -z "$SRC_DIR" ]; then
    SRC_DIR=$(pwd)
fi

# Find Python files
FILES=($(find "${SRC_DIR}" -type f -name "*.py" -not -path "*.venv*"))

echo "Found ${#FILES[@]} Python files"

# Step 1: ruff check
echo "Running ruff check..."
ruff check "$SRC_DIR"

# Step 2: vulture dead code detection
echo "Running vulture..."
vulture "$SRC_DIR" --min-confidence 80 || true

# Step 3: autoflake, ruff format, isort
echo "Running autoflake, ruff format, isort..."
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

# Step 4: run pytest
echo "Running pytest..."
pytest "$SRC_DIR" -v || true

echo "Done!"

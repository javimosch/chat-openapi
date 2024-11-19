#!/bin/bash

# Function to check taskfile
check_taskfile() {
    local taskfile=$1
    echo "Checking $taskfile..."
    
    # Check if file exists
    if [ ! -f "$taskfile" ]; then
        echo "Error: $taskfile does not exist"
        return 1
    fi
    
    # Try to list tasks
    if task -t "$taskfile" --list-all 2>/dev/null; then
        echo "✅ $taskfile is valid"
        return 0
    else
        echo "❌ $taskfile has errors"
        # Show the actual error by running task again without redirecting stderr
        task -t "$taskfile" --list-all
        return 1
    fi
}

# Test Taskfile.yml
echo "Testing Taskfile.yml..."
check_taskfile "Taskfile.yml"
echo

# Test Taskfile-that-works.yml
echo "Testing Taskfile-that-works.yml..."
check_taskfile "Taskfile-that-works.yml"

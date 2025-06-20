#!/bin/bash
set -e

# Test script for Codex container solution validation
# This script tests the Phase 1 Environment Variable Solution

echo "🧪 Testing Codex Container Solution"
echo "====================================="

# Get the directory of this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CODEX_CLI_DIR="$(dirname "$SCRIPT_DIR")"

# Create a temporary test directory
TEST_DIR="$(mktemp -d)"
echo "📁 Created test directory: $TEST_DIR"

# Create a simple test file
cat > "$TEST_DIR/test.txt" << EOF
# Test file for container validation
This is a test file to validate that Codex container can:
1. Read files
2. Execute commands without interactive prompts
3. Handle git repository initialization properly
EOF

echo "📝 Created test file: $TEST_DIR/test.txt"

# Test 1: Simple file reading
echo ""
echo "🔍 Test 1: Simple file reading"
echo "-----------------------------"
if "$SCRIPT_DIR/run_in_container.sh" --work_dir "$TEST_DIR" "cat test.txt"; then
    echo "✅ Test 1 PASSED: Container can read files"
else
    echo "❌ Test 1 FAILED: Container cannot read files"
fi

# Test 2: Git operations (should work with pre-initialization)
echo ""
echo "🔍 Test 2: Git operations"
echo "------------------------"
if "$SCRIPT_DIR/run_in_container.sh" --work_dir "$TEST_DIR" "git status"; then
    echo "✅ Test 2 PASSED: Git operations work in container"
else
    echo "❌ Test 2 FAILED: Git operations failed in container"
fi

# Test 3: Simple Codex operation (if available)
echo ""
echo "🔍 Test 3: Simple Codex operation"
echo "--------------------------------"
if "$SCRIPT_DIR/run_in_container.sh" --work_dir "$TEST_DIR" "list files in this directory"; then
    echo "✅ Test 3 PASSED: Codex can execute simple commands"
else
    echo "❌ Test 3 FAILED: Codex command failed"
fi

# Test 4: Environment variable verification
echo ""
echo "🔍 Test 4: Environment variables"
echo "-------------------------------"
if "$SCRIPT_DIR/run_in_container.sh" --work_dir "$TEST_DIR" "env | grep CODEX"; then
    echo "✅ Test 4 PASSED: Environment variables are set"
else
    echo "❌ Test 4 FAILED: Environment variables not found"
fi

# Cleanup
echo ""
echo "🧹 Cleaning up test directory: $TEST_DIR"
rm -rf "$TEST_DIR"

echo ""
echo "🎯 Container Test Summary"
echo "========================"
echo "Tests completed. Check the output above for results."
echo ""
echo "💡 Next steps:"
echo "1. If all tests pass, the container solution is working"
echo "2. If tests fail, check the container logs for details"
echo "3. You can modify this script to add more specific tests"
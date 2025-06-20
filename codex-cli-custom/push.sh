#!/bin/bash

# Check if there are any changes to commit
if [[ -z $(git status -s) ]]; then
    echo "No changes to commit."
    exit 0
fi

# Get commit message from user
echo "Enter commit message:"
read commit_message

# If no message is provided, use a default one
if [[ -z "$commit_message" ]]; then
    commit_message="Update $(date +%Y-%m-%d)"
    echo "Using default commit message: $commit_message"
fi

# Add all changes
git add .

# Commit with the provided message
git commit -m "$commit_message"

# Push to the current branch
current_branch=$(git symbolic-ref --short HEAD)
git push origin $current_branch

echo "Changes committed and pushed to $current_branch."

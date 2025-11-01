#!/bin/bash
# Setup script for publishing verification_toolkit to GitHub

set -e

echo "Verification Toolkit GitHub Setup"
echo "=================================="

# Check if GitHub CLI is installed
if ! command -v gh &> /dev/null; then
    echo "GitHub CLI (gh) is not installed. Please install it first:"
    echo "  brew install gh  # on macOS"
    echo "  or visit: https://cli.github.com/"
    exit 1
fi

# Check if user is logged in to GitHub
if ! gh auth status &> /dev/null; then
    echo "Please login to GitHub CLI first:"
    echo "  gh auth login"
    exit 1
fi

# Get repository name
read -p "Enter GitHub repository name (e.g., verification-toolkit): " repo_name

if [ -z "$repo_name" ]; then
    echo "Repository name cannot be empty"
    exit 1
fi

# Get repository description
read -p "Enter repository description: " repo_description

# Get visibility preference
read -p "Make repository public? (y/n): " is_public

if [[ $is_public =~ ^[Yy]$ ]]; then
    visibility="--public"
else
    visibility="--private"
fi

echo "Creating GitHub repository: $repo_name"
echo "Description: $repo_description"
echo "Visibility: $visibility"

# Create GitHub repository
gh repo create "$repo_name" $visibility --description "$repo_description" --source=. --remote=origin --push

echo "Repository created and code pushed successfully!"
echo "Repository URL: https://github.com/$(gh api user -q .login)/$repo_name"
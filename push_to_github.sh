#!/bin/bash

# IPL Dashboard - Push to GitHub Script
# This script helps you push the project to GitHub

echo "🚀 IPL Dashboard - GitHub Push Assistant"
echo "========================================="
echo ""

# Check if git is installed
if ! command -v git &> /dev/null; then
    echo "❌ Git is not installed. Please install git first."
    exit 1
fi

echo "✅ Git found"
echo ""

# Show current status
echo "📊 Current Git Status:"
git log --oneline -3
echo ""

# Ask for GitHub repository URL
echo "📝 To push to GitHub, you need to:"
echo "1. Create a new repository on GitHub (https://github.com/new)"
echo "2. Name it: ipl-auction-dashboard (or your preferred name)"
echo "3. Copy the repository URL"
echo ""
echo "Example URLs:"
echo "   https://github.com/yourusername/ipl-auction-dashboard.git"
echo "   git@github.com:yourusername/ipl-auction-dashboard.git"
echo ""
read -p "Enter your GitHub repository URL: " REPO_URL

if [ -z "$REPO_URL" ]; then
    echo "❌ No repository URL entered. Exiting."
    exit 1
fi

echo ""
echo "🔄 Adding remote origin..."
git remote add origin $REPO_URL 2>/dev/null || git remote set-url origin $REPO_URL

echo ""
echo "📤 Pushing to GitHub..."
git push -u origin main

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ SUCCESS! Your project has been pushed to GitHub!"
    echo ""
    echo "🎉 Next steps:"
    echo "   1. Go to your GitHub repository"
    echo "   2. Copy GITHUB_README.md content to README.md on GitHub"
    echo "   3. Share your repository link!"
    echo ""
    echo "Repository URL: $REPO_URL"
else
    echo ""
    echo "❌ Push failed. Possible issues:"
    echo "   - Authentication required (use SSH key or GitHub token)"
    echo "   - Repository doesn't exist on GitHub"
    echo "   - Network connection issue"
    echo ""
    echo "Try these solutions:"
    echo "   1. Make sure you created the repository on GitHub"
    echo "   2. Set up SSH keys: https://docs.github.com/en/authentication"
    echo "   3. Or use HTTPS with personal access token"
fi

echo ""
echo "========================================="
echo "Script completed"

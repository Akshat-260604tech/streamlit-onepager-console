#!/bin/bash

# Streamlit Admin Console Deployment Script
# This script helps you deploy the admin console to Streamlit Cloud

set -e

echo "🚀 Streamlit Admin Console Deployment Script"
echo "============================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if we're in the right directory
if [ ! -f "app.py" ] || [ ! -f "requirements.txt" ]; then
    print_error "Please run this script from the streamlit-deploy directory"
    exit 1
fi

print_status "Checking deployment prerequisites..."

# Check if git is available
if ! command -v git &> /dev/null; then
    print_error "Git is not installed. Please install git first."
    exit 1
fi

# Check if we're in a git repository
if [ ! -d ".git" ]; then
    print_warning "Not in a git repository. Initializing..."
    git init
    git add .
    git commit -m "Initial admin console setup"
fi

# Check for uncommitted changes
if [ -n "$(git status --porcelain)" ]; then
    print_warning "You have uncommitted changes. Committing them now..."
    git add .
    git commit -m "Update admin console $(date)"
fi

print_status "Deployment options:"
echo "1. Deploy to new repository"
echo "2. Deploy to existing repository (current directory)"
echo "3. Just prepare files (no git operations)"
echo "4. Exit"

read -p "Choose an option (1-4): " choice

case $choice in
    1)
        print_status "Setting up new repository deployment..."

        read -p "Enter your GitHub username: " github_username
        read -p "Enter repository name (e.g., one-pager-admin): " repo_name

        # Create remote repository URL
        repo_url="https://github.com/${github_username}/${repo_name}.git"

        print_status "Adding remote origin: $repo_url"
        git remote add origin $repo_url 2>/dev/null || git remote set-url origin $repo_url

        print_status "Pushing to GitHub..."
        git branch -M main
        git push -u origin main

        print_success "Repository created and pushed to GitHub!"
        print_status "Next steps:"
        echo "1. Go to https://share.streamlit.io/"
        echo "2. Click 'New app'"
        echo "3. Connect to your repository: $repo_url"
        echo "4. Set main file path to: app_with_secrets.py"
        echo "5. Configure your secrets in Streamlit Cloud"
        echo "6. Deploy!"
        ;;

    2)
        print_status "Deploying to existing repository..."

        # Check if remote exists
        if ! git remote get-url origin &> /dev/null; then
            read -p "Enter your GitHub repository URL: " repo_url
            git remote add origin $repo_url
        fi

        print_status "Pushing changes to GitHub..."
        git push origin main

        print_success "Changes pushed to GitHub!"
        print_status "Next steps:"
        echo "1. Go to your Streamlit Cloud dashboard"
        echo "2. Update your app if it's already deployed"
        echo "3. Or create a new app pointing to this repository"
        ;;

    3)
        print_status "Preparing files for deployment..."
        print_success "Files are ready for deployment!"
        print_status "Manual deployment steps:"
        echo "1. Upload these files to your GitHub repository"
        echo "2. Go to https://share.streamlit.io/"
        echo "3. Create a new app"
        echo "4. Connect to your repository"
        echo "5. Set main file path to: app_with_secrets.py"
        echo "6. Configure secrets and deploy"
        ;;

    4)
        print_status "Exiting..."
        exit 0
        ;;

    *)
        print_error "Invalid option. Please choose 1-4."
        exit 1
        ;;
esac

print_status "Deployment preparation complete!"
print_status "Remember to:"
echo "• Configure your secrets in Streamlit Cloud"
echo "• Test the deployment thoroughly"
echo "• Monitor the logs for any issues"
echo "• Set up proper access controls if needed"

print_success "Happy deploying! 🎉"

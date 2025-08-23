#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Release management script for MODSDKSpring

Usage:
    python scripts/release.py --version 1.0.1
"""

import os
import sys
import re
import argparse
import subprocess

def update_version_in_file(file_path, old_version, new_version):
    """Update version in a specific file"""
    if not os.path.exists(file_path):
        print("Warning: {} not found".format(file_path))
        return False
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Replace version
    updated_content = content.replace(old_version, new_version)
    
    if updated_content != content:
        with open(file_path, 'w') as f:
            f.write(updated_content)
        print("Updated version in {}".format(file_path))
        return True
    
    print("No version found to update in {}".format(file_path))
    return False

def get_current_version():
    """Get current version from setup.py"""
    setup_path = "setup.py"
    if not os.path.exists(setup_path):
        return None
    
    with open(setup_path, 'r') as f:
        content = f.read()
    
    version_match = re.search(r"version\s*=\s*['\"]([^'\"]+)['\"]", content)
    if version_match:
        return version_match.group(1)
    
    return None

def validate_version(version):
    """Validate version format (semantic versioning)"""
    pattern = r'^\d+\.\d+\.\d+(?:-[a-zA-Z0-9]+)?$'
    return re.match(pattern, version) is not None

def create_git_tag(version):
    """Create and push git tag"""
    tag_name = "v{}".format(version)
    
    try:
        # Create tag
        subprocess.check_call(['git', 'tag', '-a', tag_name, '-m', 'Release {}'.format(version)])
        print("Created git tag: {}".format(tag_name))
        
        # Push tag
        subprocess.check_call(['git', 'push', 'origin', tag_name])
        print("Pushed git tag: {}".format(tag_name))
        
        return True
    except subprocess.CalledProcessError as e:
        print("Error creating/pushing git tag: {}".format(e))
        return False

def main():
    parser = argparse.ArgumentParser(description='Release management for MODSDKSpring')
    parser.add_argument('--version', required=True, help='New version to release (e.g., 1.0.1)')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be done without making changes')
    
    args = parser.parse_args()
    
    new_version = args.version
    
    # Validate version format
    if not validate_version(new_version):
        print("Error: Invalid version format. Use semantic versioning (e.g., 1.0.1)")
        sys.exit(1)
    
    # Get current version
    current_version = get_current_version()
    if not current_version:
        print("Error: Could not determine current version from setup.py")
        sys.exit(1)
    
    print("Current version: {}".format(current_version))
    print("New version: {}".format(new_version))
    
    if args.dry_run:
        print("DRY RUN - No changes will be made")
        print("Would update version in:")
        print("  - setup.py")
        print("Would create git tag: v{}".format(new_version))
        return
    
    # Confirm with user
    response = raw_input("Continue with release? (y/N): ")
    if response.lower() != 'y':
        print("Release cancelled")
        sys.exit(0)
    
    # Update version in setup.py
    if not update_version_in_file("setup.py", current_version, new_version):
        print("Error: Failed to update version in setup.py")
        sys.exit(1)
    
    # Commit version changes
    try:
        subprocess.check_call(['git', 'add', 'setup.py'])
        subprocess.check_call(['git', 'commit', '-m', 'Bump version to {}'.format(new_version)])
        subprocess.check_call(['git', 'push'])
        print("Committed and pushed version changes")
    except subprocess.CalledProcessError as e:
        print("Error committing changes: {}".format(e))
        sys.exit(1)
    
    # Create and push git tag
    if not create_git_tag(new_version):
        sys.exit(1)
    
    print("")
    print("Release {} completed successfully!".format(new_version))
    print("GitHub Actions will automatically:")
    print("  - Build the package")
    print("  - Publish to PyPI") 
    print("  - Create GitHub release")

if __name__ == '__main__':
    main()
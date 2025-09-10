#!/usr/bin/env python3
"""
Git Activity to CSV Converter
Task: Convert git logs from multiple projects to a consolidated CSV file
"""

import os
import csv
import subprocess
import re
import argparse
import json
from datetime import datetime, timedelta
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_author_filters():
    """Get author name filters from environment variable"""
    author_names = os.getenv('author_name', '')
    return [name.strip() for name in author_names.split(',') if name.strip()]

def parse_date(date_str):
    """Parse date string in YYYY-MM-DD format"""
    try:
        return datetime.strptime(date_str, '%Y-%m-%d')
    except ValueError:
        raise argparse.ArgumentTypeError(f"Invalid date format: {date_str}. Use YYYY-MM-DD format.")

def validate_date_args(args):
    """Validate and process date arguments"""
    if args.today:
        # Today only
        today = datetime.now().strftime('%Y-%m-%d')
        return today, today, 'today'
    
    if len(args.dates) == 1:
        # Specific date
        date_str = args.dates[0].strftime('%Y-%m-%d')
        return date_str, date_str, 'specific'
    
    if len(args.dates) == 2:
        # Date range
        start_date = args.dates[0]
        end_date = args.dates[1]
        
        if start_date > end_date:
            raise ValueError("Start date cannot be after end date")
        
        return start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'), 'range'
    
    # No date filter
    return None, None, 'all'

def read_project_list(file_path):
    """Read project directories and metadata from list_project.json"""
    projects = []
    project_mapping = {}  # For mapping project path to application type
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        for project in data:
            project_path = project.get('path', '').rstrip('/')
            if project_path and os.path.exists(project_path):
                projects.append(project_path)
                # Create mapping from project path to project name for Application_type
                project_mapping[project_path] = project.get('name', '')
            elif project_path:
                print(f"Warning: Project path does not exist: {project_path}")
        
        return projects, project_mapping
    except FileNotFoundError:
        print(f"Error: {file_path} not found")
        return [], {}
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in {file_path}: {str(e)}")
        return [], {}
    except Exception as e:
        print(f"Error reading {file_path}: {str(e)}")
        return [], {}

def is_git_repository(path):
    """Check if the given path is a git repository"""
    try:
        result = subprocess.run(['git', 'rev-parse', '--git-dir'], 
                              cwd=path, capture_output=True, text=True)
        return result.returncode == 0
    except:
        return False

def get_git_log(repo_path, author_filters, project_mapping, start_date=None, end_date=None):
    """Get git log for specified authors from a repository"""
    if not is_git_repository(repo_path):
        print(f"Warning: {repo_path} is not a git repository")
        return []
    
    commits = []
    
    try:
        # Build git log command with author filters
        cmd = ['git', 'log', '--pretty=format:%H|%an|%ae|%ai|%s']
        
        # Add date filters if specified
        if start_date and end_date:
            cmd.extend(['--since', f'{start_date} 00:00:00', '--until', f'{end_date} 23:59:59'])
        elif start_date:
            cmd.extend(['--since', f'{start_date} 00:00:00'])
        elif end_date:
            cmd.extend(['--until', f'{end_date} 23:59:59'])
        
        # If author filters are specified, add them to the command
        if author_filters:
            for author in author_filters:
                cmd.extend(['--author', author])
        
        result = subprocess.run(cmd, cwd=repo_path, capture_output=True, text=True)
        
        if result.returncode == 0:
            # Get application type from project mapping
            application_type = project_mapping.get(repo_path, '')
            
            for line in result.stdout.strip().split('\n'):
                if line:
                    parts = line.split('|', 4)
                    if len(parts) == 5:
                        commit_hash, author_name, author_email, date, message = parts
                        commits.append({
                            'date': date,
                            'author_name': author_name,
                            'author_email': author_email,
                            'Application_type': application_type,
                            'Description_Technical': message.replace('\n', ' ').replace('\r', ' '),
                            'commit_hash': commit_hash,
                            'project_path': repo_path
                        })
        else:
            print(f"Error getting git log from {repo_path}: {result.stderr}")
    
    except Exception as e:
        print(f"Exception while processing {repo_path}: {str(e)}")
    
    return commits

def save_to_csv(commits, output_file):
    """Save commits data to CSV file"""
    fieldnames = ['commit_hash', 'author_name', 'author_email', 'date', 'Application_type', 'Description_Technical', 'project_path']
    
    try:
        with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for commit in commits:
                # Reorder the commit data to match fieldnames
                row = {
                    'author_email': commit['author_email'],
                    'date': commit['date'],
                    'Application_type': commit['Application_type'],
                    'Description_Technical': commit['Description_Technical'],
                    'project_path': commit['project_path'],
                    'commit_hash': commit['commit_hash'],
                    'author_name': commit['author_name']
                }
                writer.writerow(row)
        print(f"Successfully saved {len(commits)} commits to {output_file}")
    except Exception as e:
        print(f"Error saving to CSV: {str(e)}")

def main():
    """Main function to process all git repositories and generate CSV"""
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description='Convert git logs from multiple projects to CSV',
        epilog='''
Examples:
  %(prog)s --today                    # Today's commits only
  %(prog)s 2025-09-02                 # Specific date
  %(prog)s 2025-09-01 2025-09-10      # Date range
  %(prog)s                            # All commits
        ''',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('--today', action='store_true', 
                       help='Filter commits to today only')
    parser.add_argument('dates', nargs='*', type=parse_date, 
                       help='Date(s) in YYYY-MM-DD format. One date for specific day, two dates for range.')
    
    args = parser.parse_args()
    
    # Validate argument combinations
    if args.today and args.dates:
        parser.error("Cannot use --today with date arguments")
    
    if len(args.dates) > 2:
        parser.error("Too many date arguments. Provide at most 2 dates for a range.")
    
    print("Starting Git Activity to CSV conversion...")
    
    # Process date arguments
    try:
        start_date, end_date, date_mode = validate_date_args(args)
    except ValueError as e:
        print(f"Error: {e}")
        return
    
    # Print date filter info
    if date_mode == 'today':
        print(f"Filtering commits for today: {start_date}")
    elif date_mode == 'specific':
        print(f"Filtering commits for specific date: {start_date}")
    elif date_mode == 'range':
        print(f"Filtering commits from {start_date} to {end_date}")
    else:
        print("No date filter applied - processing all commits")
    
    # Get author filters from environment
    author_filters = get_author_filters()
    print(f"Author filters: {author_filters}")
    
    # Read project list
    project_list_file = 'list_project.json'
    projects, project_mapping = read_project_list(project_list_file)
    print(f"Found {len(projects)} projects to process")
    
    if not projects:
        print("No valid projects found. Exiting.")
        return
    
    # Collect all commits from all projects
    all_commits = []
    
    for project_path in projects:
        print(f"Processing: {project_path}")
        commits = get_git_log(project_path, author_filters, project_mapping, start_date, end_date)
        all_commits.extend(commits)
        print(f"  Found {len(commits)} commits")
    
    # Generate output filename with timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    if date_mode == 'today':
        output_file = f'git_log_today_{timestamp}.csv'
    elif date_mode == 'specific':
        date_suffix = start_date.replace('-', '')
        output_file = f'git_log_{date_suffix}_{timestamp}.csv'
    elif date_mode == 'range':
        start_suffix = start_date.replace('-', '')
        end_suffix = end_date.replace('-', '')
        output_file = f'git_log_{start_suffix}_to_{end_suffix}_{timestamp}.csv'
    else:
        output_file = f'git_log_{timestamp}.csv'
    
    # Save to CSV
    if all_commits:
        save_to_csv(all_commits, output_file)
        print(f"\nTotal commits processed: {len(all_commits)}")
        print(f"Output file: {output_file}")
    else:
        print("No commits found matching the criteria.")

if __name__ == "__main__":
    main()

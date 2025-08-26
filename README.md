# Git Activity to CSV Converter

A Python tool to extract git commit activities from multiple projects and consolidate them into a single CSV file. This tool is perfect for tracking development activities across multiple repositories for reporting, analysis, or time tracking purposes.

## Features

- 📊 Extract git commits from multiple repositories
- 🎯 Filter commits by specific authors
- 📅 Option to filter commits for today only
- 📝 Export to CSV format with structured data
- 🏷️ Categorize commits by application type
- ⚠️ Error handling for invalid repositories
- 🔧 Environment variable configuration

## Installation

1. **Clone or download this repository**
   ```bash
   git clone git@github.com:zulfafalah/convert-git-activity-to-csv.git
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables** (optional)
   Create a `.env` file in the project root:
   ```env
   author_name=John Doe,Jane Smith,Your Name
   ```

## Configuration

### Project List Configuration

Create or modify the `list_project.json` file to specify which repositories to analyze:

```json
[
    {
        "name": "Web Application",
        "path": "/path/to/your/web-project",
        "category": "Development",
        "type": "web"
    },
    {
        "name": "Mobile App",
        "path": "/path/to/your/mobile-project",
        "category": "Android",
        "type": "mobile"
    }
]
```

**Field descriptions:**
- `name`: Display name for the project (used as Application_type in CSV)
- `path`: Absolute path to the git repository
- `category`: Project category (for your reference)
- `type`: Project type (for your reference)

### Environment Variables

- `author_name`: Comma-separated list of author names to filter commits (optional)

## Usage

### Basic Usage

Extract all commits from configured repositories:
```bash
python main.py
```

### Filter Today's Commits Only

Extract only commits made today:
```bash
python main.py --today
```

### Command Line Options

- `--today`: Filter commits to today only

## Output

The tool generates a CSV file with the following columns:

| Column | Description |
|--------|-------------|
| `commit_hash` | Git commit SHA hash |
| `author_name` | Name of the commit author |
| `author_email` | Email of the commit author |
| `date` | Commit timestamp |
| `Application_type` | Project name from configuration |
| `Description_Technical` | Commit message |
| `project_path` | Path to the repository |

### Output Files

- **All commits**: `git_log_YYYYMMDD_HHMMSS.csv`
- **Today's commits**: `git_log_today_YYYYMMDD_HHMMSS.csv`

## Example Workflow

1. **Configure your projects** in `list_project.json`
2. **Set author filters** in `.env` (optional)
3. **Run the tool**:
   ```bash
   # For all commits
   python main.py
   
   # For today's commits only
   python main.py --today
   ```
4. **Open the generated CSV** in Excel, Google Sheets, or any CSV viewer

## Sample Output

```csv
commit_hash,author_name,author_email,date,Application_type,Description_Technical,project_path
a1b2c3d4,John Doe,john@example.com,2024-08-26 10:30:00 +0700,Web Application,Fix user authentication bug,/path/to/web-project
e5f6g7h8,Jane Smith,jane@example.com,2024-08-26 14:15:00 +0700,Mobile App,Add new login screen,/path/to/mobile-project
```

## Error Handling

The tool handles various scenarios gracefully:

- **Missing repositories**: Warns about non-existent paths
- **Non-git directories**: Skips directories that aren't git repositories
- **Invalid JSON**: Reports JSON parsing errors in configuration
- **Git command failures**: Continues processing other repositories

## Requirements

- Python 3.6+
- Git installed and accessible from command line
- `python-dotenv` package

## Project Structure

```
git-activity-to-csv/
├── main.py                 # Main application script
├── requirements.txt        # Python dependencies
├── list_project.json      # Project configuration
├── .env                   # Environment variables (optional)
├── README.md              # This file
└── *.csv                  # Generated output files
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is open source. Feel free to use and modify as needed.

## Troubleshooting

### Common Issues

1. **"Command not found: git"**
   - Ensure Git is installed and added to your system PATH

2. **"Permission denied" errors**
   - Check that you have read access to the configured repository paths

3. **Empty CSV output**
   - Verify that the configured paths contain git repositories
   - Check that the author filters match actual commit authors
   - Ensure the date range contains commits

4. **Invalid JSON error**
   - Validate your `list_project.json` syntax using a JSON validator

### Debug Tips

- Run with verbose output to see which repositories are being processed
- Check the console output for warnings about missing or invalid repositories
- Verify that your `.env` file is properly formatted

## Author

Created for tracking development activities across multiple Git repositories.

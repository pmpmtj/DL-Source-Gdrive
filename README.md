# Google Drive Audio File Downloader

A Python tool for automatically downloading audio files (MP3, M4A) from Google Drive with OAuth2 authentication, configurable folder search, and robust error handling.

## 🚀 Features

- **OAuth2 Authentication** - Secure Google Drive API access with automatic token refresh
- **Configurable Search** - Search in root directory or specific Google Drive folders
- **Audio File Filtering** - Automatically filters and downloads only audio files (.mp3, .m4a)
- **Chronological Organization** - Downloads files to date-prefixed subdirectories to maintain chronological order for diary entries
- **Optional Source Cleanup** - Delete files from Google Drive after successful download
- **Comprehensive Logging** - Detailed logging with configurable levels
- **Cross-platform Support** - Works on Windows, macOS, and Linux
- **PyInstaller Support** - Can be packaged as a standalone executable

## 📋 Prerequisites

- Python 3.7 or higher
- Google Cloud Platform account
- Google Drive API enabled

## 🛠️ Installation

1. **Clone or download this repository**
   ```bash
   git clone <repository-url>
   cd dl_src_gdrive
   ```

2. **Install required dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up Google Drive API credentials** (see [Setup Instructions](#-setup-instructions))

## 🔧 Setup Instructions

### Step 1: Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Google Drive API:
   - Go to "APIs & Services" > "Library"
   - Search for "Google Drive API"
   - Click "Enable"

### Step 2: Create OAuth2 Credentials

1. Go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "OAuth client ID"
3. Choose "Desktop application" as the application type
4. Give it a name (e.g., "Google Drive Audio Downloader")
5. Click "Create"
6. Download the JSON file (it will be named something like `client_secret_123456789-abcdefg.apps.googleusercontent.com.json`)

### Step 3: Add Credentials to the Project

1. **Copy the downloaded JSON file** to the `src/dl_src_gdrive/config/` directory
2. **Rename the file** to match the configuration in `dl_gdrive_config.py`:
   - The default expected name is: `client_secret_890800499519-d2bvsnp5bbfqieovpd4fnafacl0hkjaa.apps.googleusercontent.com.json`
   - **OR** update the `client_secret_file` setting in `src/dl_src_gdrive/config/dl_gdrive_config.py` to match your actual filename

### Step 4: Configure the Application

#### Download Directory Configuration

Edit `app_config/app_config.py` to set the download directory:

```python
@dataclass
class AppConfig:
    # Must be an absolute path
    download_dir: str = r"C:\Users\YourUsername\Downloads"

APP_CONFIG = AppConfig()
```

#### Google Drive Settings

Edit `src/dl_src_gdrive/config/dl_gdrive_config.py` to customize Google Drive settings:

```python
@dataclass
class GdriveConfig:
    # Whether to delete files from Google Drive after download
    delete_from_src: bool = False
    
    # Folders to search (use "root" for root directory)
    search_folders: List[str] = field(default_factory=lambda: ["root"])
    
    # Your client secret filename
    client_secret_file: str = "your_actual_filename.json"
    
    # Supported audio file extensions
    allowed_extensions: List[str] = field(default_factory=lambda: ['.mp3', '.m4a'])
```

## 🚀 Usage

### Basic Usage

```bash
# Navigate to the project directory
cd src/dl_src_gdrive

# Run the downloader
python -m dl_src_gdrive.main
```

### Command Line Options

```bash
# Enable debug logging
python -m dl_src_gdrive.main --debug

# Remove credentials after download (for security)
python -m dl_src_gdrive.main --cleanup

# Delete files from Google Drive after successful download
python -m dl_src_gdrive.main --delete-from-gdrive

# Combine options
python -m dl_src_gdrive.main --debug --cleanup --delete-from-gdrive
```

### First Run

1. **Run the application** for the first time:
   ```bash
   python -m dl_src_gdrive.main
   ```

2. **Authenticate with Google Drive**:
   - A browser window will open
   - Sign in to your Google account
   - Grant permissions to the application
   - The browser will show a success message

3. **Download process**:
   - The tool will search for audio files in configured folders
   - Download each file to a unique subdirectory
   - Optionally delete files from Google Drive (if configured)

## 📁 File Organization

Downloaded files are organized chronologically as follows:

```
downloads/
├── 2024-10-02_143052_1xmnb8iq-uGbWa9bdJTd-vzSY19HsIDyR/  # Date + Google Drive file ID
│   └── Rua Diogo Domingos Alves.m4a
├── 2024-10-02_150230_2abc123def456ghi789jkl012mno345pqr/
│   └── Another Audio File.mp3
└── ...
```

**Chronological Ordering**: Files are organized by their Google Drive creation date in `YYYY-MM-DD_HHMMSS` format, ensuring diary entries maintain proper chronological order when browsing the file system.

## ⚙️ Configuration Options

### Search Folders

To search specific Google Drive folders instead of the root directory:

1. **Get the folder ID** from Google Drive URL:
   - Open the folder in Google Drive
   - Copy the ID from the URL: `https://drive.google.com/drive/folders/FOLDER_ID_HERE`

2. **Update configuration**:
   ```python
   search_folders: List[str] = field(default_factory=lambda: [
       "root",  # Root directory
       "1ABC123DEF456GHI789JKL012MNO345PQR",  # Specific folder ID
       "1XYZ789UVW456RST123OPQ890MNO567JKL"   # Another folder ID
   ])
   ```

### Supported File Formats

To add or change supported audio formats:

```python
allowed_extensions: List[str] = field(default_factory=lambda: [
    '.mp3',   # MPEG Audio Layer III
    '.m4a',   # MPEG-4 Audio
    '.wav',   # Waveform Audio File Format
    '.flac',  # Free Lossless Audio Codec
    '.aac',   # Advanced Audio Coding
])
```

### Download Directory

To change the download location, edit `app_config/app_config.py`:

```python
@dataclass
class AppConfig:
    # Must be an absolute path
    download_dir: str = r"C:\Users\YourUsername\Downloads"  # Windows
    # download_dir: str = "/home/yourusername/downloads"  # Linux/macOS

APP_CONFIG = AppConfig()
```

**Important**: The download directory must be an absolute path. The application will validate this and show an error if a relative path is provided.

## 📊 Logging

The application provides comprehensive logging:

- **Console output** - Real-time progress and status updates
- **File logging** - Detailed logs saved to `logs/gdrive_downloader.log`
- **Debug mode** - Use `--debug` flag for verbose output

### Log Levels

- **INFO** - General progress and status information
- **DEBUG** - Detailed debugging information (use `--debug` flag)
- **WARNING** - Non-critical issues (e.g., files already exist)
- **ERROR** - Critical errors that prevent operation

## 🔒 Security

### Credential Management

- **OAuth2 tokens** are stored locally in `config/token.json`
- **Use `--cleanup` flag** to remove credentials after use
- **Never commit** `token.json` or `client_secret_*.json` to version control

### File Safety

- **Filename sanitization** prevents filesystem issues
- **UUID-based directories** prevent file conflicts
- **Duplicate detection** skips already downloaded files

## 🐛 Troubleshooting

### Common Issues

1. **"Client secret file not found"**
   - Ensure the JSON file is in `src/dl_src_gdrive/config/`
   - Check the filename matches the configuration

2. **"Authentication failed"**
   - Verify the client secret file is valid
   - Check that Google Drive API is enabled
   - Ensure the OAuth2 credentials are for a "Desktop application"

3. **"No audio files found"**
   - Check the `search_folders` configuration
   - Verify the `allowed_extensions` include your file types
   - Ensure you have access to the specified folders

4. **"Permission denied" errors**
   - Check file permissions for the download directory
   - Ensure the application has write access

### Debug Mode

Use debug mode for detailed troubleshooting:

```bash
python -m dl_src_gdrive.main --debug
```

This will show:
- Detailed file discovery process
- Individual file filtering decisions
- Download progress for each file
- Authentication flow details

## 📝 Example Workflow

1. **Setup**:
   ```bash
   # Install dependencies
   pip install -r requirements.txt
   
   # Add your client secret file to config/
   cp ~/Downloads/client_secret_*.json src/dl_src_gdrive/config/
   ```

2. **Configure** (optional):
   ```python
   # Edit app_config/app_config.py for download directory
   download_dir: str = r"C:\Users\YourUsername\Downloads"
   
   # Edit src/dl_src_gdrive/config/dl_gdrive_config.py for Google Drive settings
   search_folders = ["root", "1ABC123DEF456GHI789JKL"]
   allowed_extensions = ['.mp3', '.m4a', '.wav']
   ```

3. **Run**:
   ```bash
   cd src/dl_src_gdrive
   python -m dl_src_gdrive.main --debug
   ```

4. **Authenticate** (first time only):
   - Browser opens for Google authentication
   - Grant permissions to the application

5. **Download**:
   - Tool searches configured folders
   - Downloads audio files to `downloads/` directory
   - Optionally deletes files from Google Drive

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For issues and questions:
1. Check the troubleshooting section above
2. Review the logs in `logs/gdrive_downloader.log`
3. Create an issue in the repository

## 🔄 Version History

- **v1.0.0** - Initial release with OAuth2 authentication and audio file downloading

---

**Note**: This tool is designed for personal use. Ensure you have proper permissions for any Google Drive files you're downloading and comply with Google's Terms of Service.

"""
Downloader utility module for TikTok Clip Automator.
This module handles downloading video content from various sources,
including TikTok, Instagram, and other social media platforms.
Provides functions for URL validation, content extraction, and
file management during the download process.

Weekly Highlights Mode:
Fetches top content from Reddit and YouTube for automated weekly highlight compilation.
X/Twitter content requires manual video URL input.
"""

import os
import logging
import subprocess
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
import tempfile
import os
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

def ensure_drive_subfolder(service, parent_id, subfolder_name):
    query = f"'{parent_id}' in parents and mimeType = 'application/vnd.google-apps.folder' and name = '{subfolder_name}' and trashed = false"
    results = service.files().list(q=query, fields="files(id, name)").execute()
    folders = results.get('files', [])
    if folders:
        return folders[0]['id']
    # Create folder if missing
    folder_metadata = {'name': subfolder_name,
                       'mimeType': 'application/vnd.google-apps.folder',
                       'parents': [parent_id]}
    folder = service.files().create(body=folder_metadata, fields='id').execute()
    return folder.get('id')

def upload_to_drive_via_service_account(file_name, file_stream):
    """
    Uploads a video to the 'impulse/2.0/' folder in Google Drive using a service account,
    then deletes any temp file after upload.

    Args:
      file_name:        Name for the uploaded file in Drive (str)
      file_stream:      File-like object or stream (opened in 'rb' mode)

    Returns:
      The uploaded Google Drive file ID string upon success, else None.
    """
    SCOPES = ['https://www.googleapis.com/auth/drive']
    SERVICE_ACCOUNT_FILE = 'creds.json'
    IMPULSE_PARENT_ID = '1IjWmMJJKp3BMhVINrSbwkL1HIT5277WF'

    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES
    )
    service = build('drive', 'v3', credentials=credentials)

    # Find or create '2.0' within 'impulse'
    subfolder_id = ensure_drive_subfolder(service, IMPULSE_PARENT_ID, '2.0')

    temp_path = ''
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file_name)[-1]) as tmp:
            tmp.write(file_stream.read())
            temp_path = tmp.name

        file_metadata = {'name': file_name, 'parents': [subfolder_id]}
        media = MediaFileUpload(temp_path, resumable=True)
        uploaded = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
        print(f"Uploaded {file_name} to Google Drive (impulse/2.0) with ID {uploaded.get('id')}")
        return uploaded.get('id')
    finally:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# =============================================================================
# API CONFIGURATION - ADD YOUR API KEYS HERE
# =============================================================================

# Reddit API Configuration
# Get credentials from: https://www.reddit.com/prefs/apps
REDDIT_CLIENT_ID = os.getenv('REDDIT_CLIENT_ID', '')  # Add your client ID here
REDDIT_CLIENT_SECRET = os.getenv('REDDIT_CLIENT_SECRET', '')  # Add your client secret here
REDDIT_USER_AGENT = os.getenv('REDDIT_USER_AGENT', 'TikTokClipAutomator/1.0')  # Your app name

# YouTube API Configuration
# Get credentials from: https://console.developers.google.com/
YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY', '')  # Add your API key here

# TODO: Add more platform API configurations as needed
# TIKTOK_API_KEY = os.getenv('TIKTOK_API_KEY', '')  # Future implementation
# INSTAGRAM_API_KEY = os.getenv('INSTAGRAM_API_KEY', '')  # Future implementation

# =============================================================================
# MANUAL X/TWITTER VIDEO DOWNLOADER
# =============================================================================

def fetch_manual_x_clips(tweet_urls: List[str], output_dir: str = 'downloads') -> Dict[str, Any]:
    """
    Downloads video clips from manually provided X/Twitter URLs using yt-dlp.
    
    Note: X/Twitter content is now manual-only. Users must provide specific tweet URLs
    containing videos. Automated fetching of X/Twitter content has been disabled.
    
    Args:
        tweet_urls (List[str]): List of X/Twitter URLs containing videos
        output_dir (str): Directory to save downloaded videos
        
    Returns:
        Dict[str, Any]: Results containing successful downloads and errors
    """
    results = {
        'successful_downloads': [],
        'failed_downloads': [],
        'errors': []
    }
    
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    for url in tweet_urls:
        try:
            logger.info(f"Attempting to download video from X/Twitter URL: {url}")
            
            # Use yt-dlp to download the video
            cmd = [
                'yt-dlp',
                '--extract-flat', 'false',
                '--write-info-json',
                '--write-thumbnail',
                '--output', f'{output_dir}/%(uploader)s_%(title)s_%(id)s.%(ext)s',
                url
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            results['successful_downloads'].append({
                'url': url,
                'status': 'success',
                'output_dir': output_dir
            })
            
            logger.info(f"Successfully downloaded video from: {url}")
            
        except subprocess.CalledProcessError as e:
            error_msg = f"Failed to download from {url}: {e.stderr}"
            logger.error(error_msg)
            results['failed_downloads'].append(url)
            results['errors'].append(error_msg)
            
        except Exception as e:
            error_msg = f"Unexpected error downloading from {url}: {str(e)}"
            logger.error(error_msg)
            results['failed_downloads'].append(url)
            results['errors'].append(error_msg)
    
    return results

# =============================================================================
# WEEKLY HIGHLIGHTS FETCHER (AUTOMATED REDDIT & YOUTUBE ONLY)
# =============================================================================

class WeeklyHighlightsFetcher:
    """
    Fetches top content from Reddit and YouTube for automated weekly highlights.
    
    Note: X/Twitter content is no longer automatically fetched. Use fetch_manual_x_clips()
    function for manual X/Twitter video downloading with user-provided URLs.
    
    Automated platforms:
    - Reddit: Fetches top posts from specified subreddits
    - YouTube: Fetches trending videos based on search terms
    
    Manual platforms:
    - X/Twitter: Requires manual URL input via fetch_manual_x_clips() function
    """
    
    def __init__(self):
        """Initialize the WeeklyHighlightsFetcher."""
        self.reddit_client = None
        self.youtube_client = None
        # Note: Twitter client removed - now manual only
        
    def validate_api_credentials(self) -> Dict[str, bool]:
        """
        Validate API credentials for automated platforms only (Reddit and YouTube).
        
        Returns:
            Dict[str, bool]: Status of each platform's API credentials
        """
        credentials = {
            'reddit': bool(REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET),
            'youtube': bool(YOUTUBE_API_KEY)
            # Note: Twitter credentials no longer checked for automated fetching
        }
        return credentials
    
    def fetch_reddit_highlights(self, config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Fetch top posts from Reddit subreddits.
        
        Args:
            config (Dict[str, Any]): Reddit configuration with subreddits and limit
            
        Returns:
            List[Dict[str, Any]]: List of Reddit posts
        """
        # TODO: Implement Reddit API integration
        logger.info(f"TODO: Fetch Reddit highlights with config: {config}")
        return []
    
    def fetch_youtube_highlights(self, config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Fetch trending videos from YouTube.
        
        Args:
            config (Dict[str, Any]): YouTube configuration with search terms and limit
            
        Returns:
            List[Dict[str, Any]]: List of YouTube videos
        """
        # TODO: Implement YouTube API integration
        logger.info(f"TODO: Fetch YouTube highlights with config: {config}")
        return []
    
    def fetch_all_highlights(self, config: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
        """
        Fetch highlights from all automated platforms (Reddit and YouTube only).
        
        Note: X/Twitter content must be manually downloaded using fetch_manual_x_clips()
        
        Args:
            config (Dict[str, Any]): Configuration for all platforms
            
        Returns:
            Dict[str, List[Dict[str, Any]]]: Highlights organized by platform
        """
        highlights = {}
        
        # Fetch automated content only
        if 'reddit' in config:
            highlights['reddit'] = self.fetch_reddit_highlights(config['reddit'])
            
        if 'youtube' in config:
            highlights['youtube'] = self.fetch_youtube_highlights(config['youtube'])
        
        # Note: X/Twitter removed from automated fetching
        logger.info("For X/Twitter content, use fetch_manual_x_clips() with specific tweet URLs")
        
        return highlights

def validate_api_credentials() -> Dict[str, bool]:
    """
    Global function to validate API credentials for automated platforms.
    
    Returns:
        Dict[str, bool]: Status of each platform's API credentials
    """
    fetcher = WeeklyHighlightsFetcher()
    return fetcher.validate_api_credentials()

def get_default_weekly_config() -> Dict[str, Any]:
    """
    Get default configuration for automated weekly highlights (Reddit and YouTube only).
    
    Note: X/Twitter configuration removed as it now requires manual URL input.
    
    Returns:
        Dict[str, Any]: Default configuration for automated platforms
    """
    return {
        'reddit': {
            'subreddits': ['funny', 'videos', 'nextfuckinglevel', 'oddlysatisfying'],
            'limit': 10
        },
        'youtube': {
            'search_terms': ['viral video', 'trending now', 'funny moments'],
            'limit': 10
        }
        # Note: Twitter configuration removed - use fetch_manual_x_clips() instead
    }

# =============================================================================
# LEGACY FUNCTIONS (for backward compatibility)
# =============================================================================

def download_video(url: str, output_path: str) -> bool:
    """
    Download a video from a given URL.
    
    Args:
        url (str): Video URL to download
        output_path (str): Path where the video should be saved
        
    Returns:
        bool: True if download successful, False otherwise
    """
    # TODO: Implement video downloading functionality
    logger.info(f"TODO: Download video from {url} to {output_path}")
    return False

if __name__ == "__main__":
    # Example usage
    print("Weekly Highlights Fetcher - Automated Reddit/YouTube, Manual X/Twitter!")
    
    # Check API credentials for automated platforms
    credentials = validate_api_credentials()
    print(f"Automated API Status: {credentials}")
    
    # Initialize fetcher
    fetcher = WeeklyHighlightsFetcher()
    
    # Get default config (automated platforms only)
    config = get_default_weekly_config()
    print(f"Automated platforms config: {config}")
    
    # Example of manual X/Twitter usage
    print("\nFor X/Twitter videos, use manual mode:")
    print("tweet_urls = ['https://twitter.com/user/status/123', 'https://x.com/user/status/456']")
    print("results = fetch_manual_x_clips(tweet_urls)")
    print("print(f'X/Twitter results: {results}')")
    
    # This would fetch automated highlights once APIs are implemented
    # highlights = fetcher.fetch_all_highlights(config)
    # print(f"Automated highlights: {highlights}")

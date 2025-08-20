#!/usr/bin/env python3
"""
Test script for Drive upload functionality.
Downloads a small public sample file and uploads it to Drive using 
upload_to_drive_via_service_account from utils.downloader.
"""

import os
import io
import requests
import tempfile
from utils.downloader import upload_to_drive_via_service_account

def download_sample_file():
    """
    Downloads a small public sample file for testing.
    Returns the file content as bytes and a filename.
    """
    # Using a small public sample image from httpbin.org
    url = "https://httpbin.org/image/png"
    
    print(f"Downloading sample file from: {url}")
    response = requests.get(url)
    response.raise_for_status()
    
    filename = "test_sample_image.png"
    print(f"Downloaded {len(response.content)} bytes")
    
    return response.content, filename

def test_drive_upload():
    """
    Main test function - downloads sample file and uploads to Drive.
    """
    print("Starting Drive upload test...")
    
    # Check if creds.json exists
    if not os.path.exists('creds.json'):
        print("ERROR: creds.json not found. Make sure it exists for Drive authentication.")
        return False
    
    try:
        # Download a sample file
        file_content, filename = download_sample_file()
        
        # Create a file-like object from the content
        file_stream = io.BytesIO(file_content)
        
        # Upload to Drive
        print(f"Uploading {filename} to Google Drive...")
        drive_file_id = upload_to_drive_via_service_account(filename, file_stream)
        
        if drive_file_id:
            print(f"SUCCESS: File uploaded to Drive with ID: {drive_file_id}")
            return True
        else:
            print("FAILED: Upload returned None")
            return False
            
    except Exception as e:
        print(f"ERROR: {str(e)}")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("Drive Upload Test Script")
    print("=" * 50)
    
    success = test_drive_upload()
    
    if success:
        print("\n✅ Test PASSED: Drive upload functionality works!")
        exit(0)
    else:
        print("\n❌ Test FAILED: Drive upload functionality failed!")
        exit(1)

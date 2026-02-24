import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import os

# Configuration
# The ID corrected from your URL
SPREADSHEET_ID = "1zysi4NGU8RQVUbvjcFE1pYAvscoEeXTclJkFEZl7A9M"
SHEET_NAME = "Sheet1"  # Default name from your screenshot
SERVICE_ACCOUNT_FILE = "service_account.json"

def get_sheets_client():
    """Authenticates and returns the gspread client."""
    if not os.path.exists(SERVICE_ACCOUNT_FILE):
        return None
    
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    
    try:
        credentials = Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, 
            scopes=scopes
        )
        gc = gspread.authorize(credentials)
        return gc
    except Exception as e:
        print(f"Error authenticating with Google Sheets: {e}")
        return None

def append_chat(user_message, bot_reply):
    """
    Appends a new row to the Google Sheet with the conversation details.
    Columns: Timestamp, User Message, Bot Reply
    """
    client = get_sheets_client()
    if not client:
        return False
        
    try:
        sh = client.open_by_key(SPREADSHEET_ID)
        worksheet = sh.worksheet(SHEET_NAME)
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
        
        row = [timestamp, user_message, bot_reply]
        worksheet.append_row(row)
        return True
    except gspread.exceptions.SpreadsheetNotFound:
        print(f"Error: Spreadsheet with ID '{SPREADSHEET_ID}' not found. Please check the ID.")
        return False
    except gspread.exceptions.WorksheetNotFound:
        print(f"Error: Worksheet named '{SHEET_NAME}' not found in the spreadsheet.")
        return False
    except Exception as e:
        print(f"Unexpected error appending to Google Sheets: {e}")
        return False

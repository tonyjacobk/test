from datetime import  timedelta, date
import datetime
import pytz
import os
import requests
import shutil
headers = {
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36',
    'sec-ch-ua': '"Not;A=Brand";v="99", "Google Chrome";v="139", "Chromium";v="139"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"'
}



def generate_appropriate_ma_date_string():
    
    # Get current UTC time
    utc_now = datetime.datetime.now(pytz.UTC)
    current_hour = utc_now.hour
    current_minute = utc_now.minute
    current_weekday = utc_now.weekday()  # 0=Monday, 6=Sunday
    
    # Start with current date
    target_date = utc_now.date()
    
    # Rule 1: If Saturday (5) or Sunday (6), use Friday's date
    if current_weekday == 5:  # Saturday
        target_date = target_date - timedelta(days=1)  # Go back to Friday
    elif current_weekday == 6:  # Sunday
        target_date = target_date - timedelta(days=2)  # Go back to Friday
    
    # Rule 2: If GMT time < 13:00, use yesterday's date
    elif current_hour < 13:
        target_date = target_date - timedelta(days=1)
    
    # Format the date string: MA + DD + MM + YY
    day = target_date.strftime("%d")
    month = target_date.strftime("%m") 
    year = target_date.strftime("%y")
    
    ma_string = f"MA{day}{month}{year}"
    
    return ma_string

def generate_ma_string(target_date):
    
    # Format the date string: MA + DD + MM + YY
    day = target_date.strftime("%d")
    month = target_date.strftime("%m")
    year = target_date.strftime("%y")
    
    return f"MA{day}{month}{year}"

 
def parse_ma_string(ma_string):
    
    if not isinstance(ma_string, str) or len(ma_string) != 8 or not ma_string.startswith("MA"):
        raise ValueError("MA string must be in format 'MADDMMYY'")
    
    try:
        day_str = ma_string[2:4]
        month_str = ma_string[4:6]
        year_str = ma_string[6:8]
        
        day = int(day_str)
        month = int(month_str)
        year = 2000 + int(year_str)  # Assuming 21st century
        
        return date(year, month, day)
    
    except (ValueError, TypeError) as e:
        raise ValueError(f"Invalid MA string format: {ma_string}") from e



def generate_previous_day_ma_string(today_ma_string):

    # Parse the input MA string to get the date
    today_date = parse_ma_string(today_ma_string)
    today_weekday = today_date.weekday()  # 0=Monday, 6=Sunday

    # Calculate previous business day
    if today_weekday == 0:  # Monday
        # Previous business day is Friday (3 days back)
        previous_date = today_date - timedelta(days=3)
    else:
        # Previous business day is yesterday
        previous_date = today_date - timedelta(days=1)

    return generate_ma_string(previous_date)




def is_file_older_than_last_13gmt(filepath="/tmp/price.csv") -> bool:
    if not os.path.exists(filepath):
      return True

    # Get current UTC time
    now = datetime.datetime.utcnow()

    # Today's 13:00 UTC
    last_13 = now.replace(hour=13, minute=0, second=0, microsecond=0)

    # If current time is before 13:00 UTC today, use yesterday’s 13:00 UTC
    if now < last_13:
        last_13 = last_13 - datetime.timedelta(days=1)

    # Get file modification time
    file_mtime = datetime.datetime.utcfromtimestamp(os.path.getmtime(filepath))

    # Return True if file is older than last 13:00 UTC
    return file_mtime < last_13

def is_resource_found(url):
    try:
        response = requests.head(url,headers=headers)
        return response.ok
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return False



def download_and_backup(url, headers):
    download_path = '/tmp/price.csv'
    backup_path = '/tmp/price.bak'

    # Step 1: Backup existing file if it exists
    if os.path.exists(download_path):
        print(f"Backing up '{download_path}' to '{backup_path}'...")
        try:
            os.rename(download_path, backup_path)
        except OSError as e:
            print(f"Error: Failed to rename file: {e}")
            return "Error in backup"

    # Step 2: Download the new file
    print(f"Downloading from '{url}' to '{download_path}'...")
    try:
        response = requests.get(url, headers=headers, stream=True)
        response.raise_for_status()  # This will raise an exception for bad status codes
        
        with open(download_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        print("Download successful.")
        
        # If download is successful, remove the backup file
        if os.path.exists(backup_path):
            os.remove(backup_path)
            print(f"Backup file '{backup_path}' removed.")

    # Step 3: Handle download failure and restore backup
    except requests.exceptions.RequestException as e:
        print(f"Download failed: {e}")
        if os.path.exists(backup_path):
            print(f"Restoring '{backup_path}' to '{download_path}'...")
            try:
                shutil.copyfile(backup_path, download_path)
                os.remove(backup_path)
                print("Restore successful.")
            except OSError as restore_e:
                print(f"Error: Failed to restore backup file: {restore_e}")

# Run the function





def bhav_main():
    if not is_file_older_than_last_13gmt():
        return ("No new file down loaded")
    c=generate_appropriate_ma_date_string()
    found=False
    while not found:
       print(c)
       url="https://nsearchives.nseindia.com/archives/equities/mkt/"+c+".csv"
       print(url)
       found=is_resource_found(url)
       if found:
           download_and_backup(url,headers)
           return(url)
       c=generate_previous_day_ma_string(c)

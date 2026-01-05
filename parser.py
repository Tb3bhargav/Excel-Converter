import pandas as pd
import re
import zipfile
import os
import tempfile
from datetime import datetime

class WhatsAppParser:
    def __init__(self):
        self.df = None

    def parse_file(self, filepath):
        """
        Parses a .txt or .zip file and returns a pandas DataFrame.
        """
        if filepath.lower().endswith('.zip'):
            return self._parse_zip(filepath)
        else:
            return self._parse_txt(filepath)

    def _parse_zip(self, zip_path):
        try:
            with zipfile.ZipFile(zip_path, 'r') as z:
                # Look for _chat.txt or any .txt file
                txt_files = [f for f in z.namelist() if f.endswith('.txt')]
                if not txt_files:
                    raise ValueError("No .txt file found in the zip archive.")
                
                # Prefer _chat.txt if it exists, otherwise take the first one
                target_file = '_chat.txt' if '_chat.txt' in txt_files else txt_files[0]
                
                with z.open(target_file) as f:
                    # Read and decode bytes to string
                    content = f.read().decode('utf-8', errors='replace')
                    return self._process_content(content.splitlines())
        except Exception as e:
            raise ValueError(f"Error reading zip file: {e}")

    def _parse_txt(self, txt_path):
        try:
            with open(txt_path, 'r', encoding='utf-8', errors='replace') as f:
                lines = f.readlines()
            return self._process_content(lines)
        except Exception as e:
            raise ValueError(f"Error reading text file: {e}")

    def _process_content(self, lines):
        data = []
        message_buffer = []
        date, time, sender = None, None, None

        # Regex patterns to try
        # Pattern 1: [DD/MM/YY, HH:MM:SS AM/PM] Sender: Message
        # Pattern 2: DD/MM/YY, HH:MM AM/PM - Sender: Message
        # Pattern 3: MM/DD/YY, HH:MM AM/PM - Sender: Message
        
        # We'll use a flexible regex for the timestamp part
        # Matches: [12/01/24, 10:30:45 AM] or 12/01/24, 10:30 AM - 
        timestamp_pattern = re.compile(r'^\[?(\d{1,2}[/-]\d{1,2}[/-]\d{2,4},? \d{1,2}:\d{2}(?::\d{2})?(?: [AP]M)?)\]?(?: -)? (.*)')

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Check for control characters/formatting markers that might be at start
            # (Basic cleanup)
            line = line.replace('\u200e', '') 

            match = timestamp_pattern.match(line)
            if match:
                # If we have a previous message buffered, save it
                if date and sender:
                    full_message = '\n'.join(message_buffer)
                    data.append([date, time, sender, full_message])
                
                # Reset buffer
                message_buffer = []
                
                timestamp_str = match.group(1)
                remaining = match.group(2)
                
                # Parse timestamp
                dt_obj = self._parse_timestamp(timestamp_str)
                if dt_obj:
                    date = dt_obj.date()
                    time = dt_obj.time()
                else:
                    # Fallback if date parsing fails, treat as continuation? 
                    # Or just keep raw string. Let's keep raw for now or skip.
                    # If date fails, it might not be a new message line actually.
                    message_buffer.append(line)
                    continue

                # Extract Sender and Message
                # Expecting: "Sender: Message" or "Sender: <Media omitted>"
                # System messages might not have a colon, e.g. "You added X"
                if ': ' in remaining:
                    sender, message = remaining.split(': ', 1)
                else:
                    sender = 'System'
                    message = remaining
                
                message_buffer.append(message)
            else:
                # Continuation of previous message
                if date and sender:
                    message_buffer.append(line)

        # Save the last message
        if date and sender and message_buffer:
            full_message = '\n'.join(message_buffer)
            data.append([date, time, sender, full_message])

        df = pd.DataFrame(data, columns=['Date', 'Time', 'Sender', 'Message'])
        df['Full DateTime'] = pd.to_datetime(df['Date'].astype(str) + ' ' + df['Time'].astype(str))
        df['Message Length'] = df['Message'].str.len()
        
        self.df = df
        return df

    def _parse_timestamp(self, ts_string):
        # Clean up the string
        ts_string = ts_string.replace(',', '').replace('[', '').replace(']', '')
        
        formats = [
            '%d/%m/%y %I:%M:%S %p', # 12/01/24 10:30:45 AM
            '%d/%m/%Y %I:%M:%S %p', # 12/01/2024 10:30:45 AM
            '%m/%d/%y %I:%M:%S %p', # US style
            '%d/%m/%y %I:%M %p',    # Short time
            '%d/%m/%Y %I:%M %p',
            '%d/%m/%y %H:%M',       # 24hr
            '%d/%m/%Y %H:%M',
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(ts_string, fmt)
            except ValueError:
                continue
        return None

import os
from dotenv import load_dotenv

load_dotenv()

# Gmail Configuration
GMAIL_LABEL = os.getenv('GMAIL_LABEL', 'bordereaux vinted')
CHECK_INTERVAL = int(os.getenv('CHECK_INTERVAL', '60'))

# Printer Configuration
PRINTER_NAME = os.getenv('PRINTER_NAME', '')

# Logs Configuration
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

# Working Hours Configuration
WORK_START_HOUR = int(os.getenv('WORK_START_HOUR', '8'))   # Heure de début (par défaut 8h)
WORK_END_HOUR = int(os.getenv('WORK_END_HOUR', '22'))      # Heure de fin (par défaut 22h)

# Gmail API Scopes
SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

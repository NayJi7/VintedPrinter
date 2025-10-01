import logging
import sys
from gmail_client import GmailClient
from config import LOG_LEVEL

logging.basicConfig(level=getattr(logging, LOG_LEVEL))
logger = logging.getLogger(__name__)

def main():
    gmail_client = GmailClient()
    gmail_client.authenticate()

    results = gmail_client.service.users().labels().list(userId='me').execute()
    labels = results.get('labels', [])

    print("\n" + "="*60)
    print("Liste de tous vos labels Gmail:")
    print("="*60)

    for label in sorted(labels, key=lambda x: x['name']):
        print(f"  - '{label['name']}' (ID: {label['id']})")

    print("="*60)
    print(f"\nTotal: {len(labels)} labels\n")

if __name__ == "__main__":
    main()

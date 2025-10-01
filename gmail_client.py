import os
import base64
import logging
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from config import SCOPES, GMAIL_LABEL

logger = logging.getLogger(__name__)

class GmailClient:
    def __init__(self):
        self.service = None
        self.label_id = None

    def authenticate(self):
        """Authentifie l'utilisateur avec Gmail API"""
        creds = None

        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', SCOPES)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists('credentials.json'):
                    raise FileNotFoundError(
                        "Le fichier credentials.json est introuvable. "
                        "Téléchargez-le depuis Google Cloud Console."
                    )
                flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
                creds = flow.run_local_server(port=8080, prompt='select_account')

            with open('token.json', 'w') as token:
                token.write(creds.to_json())

        self.service = build('gmail', 'v1', credentials=creds)
        logger.info("Authentification Gmail réussie")

    def get_label_id(self):
        """Récupère l'ID du label Gmail"""
        try:
            results = self.service.users().labels().list(userId='me').execute()
            labels = results.get('labels', [])

            for label in labels:
                if label['name'].lower() == GMAIL_LABEL.lower():
                    self.label_id = label['id']
                    logger.info(f"Label '{GMAIL_LABEL}' trouvé avec ID: {self.label_id}")
                    return self.label_id

            logger.error(f"Label '{GMAIL_LABEL}' introuvable dans Gmail")
            return None

        except Exception as e:
            logger.error(f"Erreur lors de la récupération du label: {e}")
            return None

    def get_all_emails_with_label(self):
        """Récupère tous les emails avec le label spécifié"""
        if not self.label_id:
            self.get_label_id()

        if not self.label_id:
            return []

        try:
            results = self.service.users().messages().list(
                userId='me',
                labelIds=[self.label_id]
            ).execute()

            messages = results.get('messages', [])
            logger.info(f"{len(messages)} email(s) total trouvé(s) avec le label")
            return messages

        except Exception as e:
            logger.error(f"Erreur lors de la récupération des emails: {e}")
            return []

    def get_unread_emails_with_label(self):
        """Récupère les emails non lus avec le label spécifié"""
        if not self.label_id:
            self.get_label_id()

        if not self.label_id:
            return []

        try:
            results = self.service.users().messages().list(
                userId='me',
                labelIds=[self.label_id, 'UNREAD']
            ).execute()

            messages = results.get('messages', [])
            logger.info(f"{len(messages)} email(s) non lu(s) trouvé(s)")
            return messages

        except Exception as e:
            logger.error(f"Erreur lors de la récupération des emails: {e}")
            return []

    def get_email_attachments(self, message_id):
        """Récupère les pièces jointes PDF d'un email"""
        try:
            message = self.service.users().messages().get(
                userId='me',
                id=message_id,
                format='full'
            ).execute()

            attachments = []

            if 'parts' in message['payload']:
                for part in message['payload']['parts']:
                    if part['filename'] and part['filename'].lower().endswith('.pdf'):
                        if 'attachmentId' in part['body']:
                            attachment = self.service.users().messages().attachments().get(
                                userId='me',
                                messageId=message_id,
                                id=part['body']['attachmentId']
                            ).execute()

                            file_data = base64.urlsafe_b64decode(attachment['data'])
                            attachments.append({
                                'filename': part['filename'],
                                'data': file_data
                            })
                            logger.info(f"Pièce jointe trouvée: {part['filename']}")

            return attachments

        except Exception as e:
            logger.error(f"Erreur lors de la récupération des pièces jointes: {e}")
            return []

    def get_email_body(self, message_id):
        """Récupère le contenu texte de l'email"""
        try:
            message = self.service.users().messages().get(
                userId='me',
                id=message_id,
                format='full'
            ).execute()

            def get_text_from_payload(payload):
                """Extrait récursivement le texte du payload"""
                body = ""

                if 'parts' in payload:
                    for part in payload['parts']:
                        body += get_text_from_payload(part)
                else:
                    if payload.get('mimeType') == 'text/plain' or payload.get('mimeType') == 'text/html':
                        data = payload.get('body', {}).get('data', '')
                        if data:
                            text = base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
                            body += text

                return body

            body_text = get_text_from_payload(message['payload'])
            return body_text

        except Exception as e:
            logger.error(f"Erreur lors de la récupération du contenu de l'email: {e}")
            return ""

    def mark_as_read(self, message_id):
        """Marque un email comme lu"""
        try:
            self.service.users().messages().modify(
                userId='me',
                id=message_id,
                body={'removeLabelIds': ['UNREAD']}
            ).execute()
            logger.info(f"Email {message_id} marqué comme lu")
            return True

        except Exception as e:
            logger.error(f"Erreur lors du marquage comme lu: {e}")
            return False

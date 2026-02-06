import logging
import sys
import os
import time
import shutil
import socket
from datetime import datetime
from gmail_client import GmailClient
from config import LOG_LEVEL, CHECK_INTERVAL, WORK_START_HOUR, WORK_END_HOUR
from pdf_modifier import extract_vinted_articles, add_footer_to_pdf
from printer import Printer


def check_single_instance():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.bind(("127.0.0.1", 37429))
        sock.listen(1)
        return True, sock
    except socket.error:
        return False, None


def show_instance_running_message():
    print("=" * 50)
    print("Une instance de VintedPrinter tourne déjà.")
    print("=" * 50)
    time.sleep(3)


def force_exit():
    if sys.platform == "win32":
        os.system("exit")
    sys.exit(0)


is_single, singleton_socket = check_single_instance()
if not is_single:
    show_instance_running_message()
    force_exit()

# Configuration de l'encodage UTF-8 pour Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

# Configuration du logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("vinted_printer.log", encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
)

logger = logging.getLogger(__name__)


def process_emails():
    """Traite les emails non lus avec le label Vinted Bordereaux"""
    gmail_client = GmailClient()
    processed_emails = {}  # Dictionnaire pour suivre les emails et leurs fichiers

    try:
        # Authentification Gmail
        gmail_client.authenticate()

        # Vérifier le label
        if not gmail_client.get_label_id():
            logger.error("Impossible de trouver le label Gmail.")
            return False

        # Récupérer les statistiques
        all_messages = gmail_client.get_all_emails_with_label()
        unread_messages = gmail_client.get_unread_emails_with_label()

        read_count = len(all_messages) - len(unread_messages)

        logger.info(f"\n{'=' * 60}")
        logger.info(f"Statistiques du label 'Vinted Bordereaux':")
        logger.info(f"  - Total: {len(all_messages)} email(s)")
        logger.info(f"  - Non lus: {len(unread_messages)} email(s)")
        logger.info(f"  - Lus: {read_count} email(s)")
        logger.info(f"{'=' * 60}\n")

        # Utiliser les emails non lus pour le traitement
        messages = unread_messages

        if not messages:
            logger.info("Aucun email non lu trouvé avec ce label.")
            return (True, {}, None)

        logger.info(f"Traitement des {len(messages)} email(s) non lu(s):")
        logger.info(f"{'=' * 60}\n")

        # Créer le dossier uploads s'il n'existe pas
        uploads_dir = "uploads"
        os.makedirs(uploads_dir, exist_ok=True)

        # Lister les détails de chaque email
        for idx, message in enumerate(messages, 1):
            message_id = message["id"]

            # Récupérer les détails complets de l'email
            msg_detail = (
                gmail_client.service.users()
                .messages()
                .get(
                    userId="me",
                    id=message_id,
                    format="metadata",
                    metadataHeaders=["From", "Subject", "Date"],
                )
                .execute()
            )

            # Extraire les headers
            headers = {
                h["name"]: h["value"]
                for h in msg_detail.get("payload", {}).get("headers", [])
            }

            logger.info(f"Email {idx}:")
            logger.info(f"  ID: {message_id}")
            logger.info(f"  De: {headers.get('From', 'N/A')}")
            logger.info(f"  Sujet: {headers.get('Subject', 'N/A')}")
            logger.info(f"  Date: {headers.get('Date', 'N/A')}")

            # Extraire les articles depuis le sujet de l'email
            subject = headers.get("Subject", "")
            articles = extract_vinted_articles(subject)

            if articles:
                article_word = "article" if len(articles) == 1 else "articles"
                footer_text = f"{len(articles)} {article_word} : " + " | ".join(
                    articles
                )
                logger.info(f"  Articles trouvés: {footer_text}")
            else:
                footer_text = ""
                logger.info(f"  Aucun article trouvé")

            # Récupérer les pièces jointes
            attachments = gmail_client.get_email_attachments(message_id)
            if attachments:
                logger.info(f"  Pièces jointes PDF ({len(attachments)}):")
                pdf_files = []
                for att in attachments:
                    # Modifier le PDF pour ajouter le footer avec les articles
                    if footer_text:
                        modified_pdf = add_footer_to_pdf(att["data"], footer_text)
                    else:
                        modified_pdf = att["data"]

                    # Sauvegarder le PDF dans le dossier uploads
                    pdf_path = os.path.join(uploads_dir, att["filename"])
                    with open(pdf_path, "wb") as f:
                        f.write(modified_pdf)
                    logger.info(
                        f"    - {att['filename']} ({len(att['data'])} octets) -> Sauvegardé dans {pdf_path}"
                    )
                    pdf_files.append(pdf_path)

                # Associer les fichiers PDF à cet email
                processed_emails[message_id] = pdf_files
            else:
                logger.info(f"  Aucune pièce jointe PDF")

            logger.info("")

        logger.info(f"{'=' * 60}")
        logger.info(f"Traitement terminé: {len(messages)} email(s) traité(s)")
        return (True, processed_emails, gmail_client)

    except Exception as e:
        logger.error(f"Erreur lors du traitement: {e}", exc_info=True)
        return (False, {}, None)


def print_uploaded_files(processed_emails, gmail_client):
    """Imprime tous les fichiers PDF présents dans le dossier uploads et marque les emails comme lus si réussi"""
    uploads_dir = "uploads"
    history_dir = "history"

    # Créer le dossier history s'il n'existe pas
    os.makedirs(history_dir, exist_ok=True)

    if not os.path.exists(uploads_dir):
        return

    pdf_files = [f for f in os.listdir(uploads_dir) if f.lower().endswith(".pdf")]

    if not pdf_files:
        return

    logger.info(f"\n{'=' * 60}")
    logger.info(f"Impression de {len(pdf_files)} fichier(s) PDF...")
    logger.info(f"{'=' * 60}\n")

    printer = Printer()
    printed_files = []  # Liste des fichiers imprimés avec succès

    for pdf_file in pdf_files:
        pdf_path = os.path.join(uploads_dir, pdf_file)

        logger.info(f"Traitement de: {pdf_file}")

        # Imprimer le fichier
        if printer.print_pdf_file(pdf_path):
            # Attendre un peu pour laisser l'impression se lancer
            time.sleep(2)

            logger.info(f"  ✓ Impression réussie")
            printed_files.append(pdf_path)

            # Déplacer le fichier vers history au lieu de le supprimer
            try:
                # Générer un nom unique avec timestamp pour éviter les doublons
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                base_name = os.path.splitext(pdf_file)[0]
                extension = os.path.splitext(pdf_file)[1]
                history_filename = f"{base_name}_{timestamp}{extension}"
                history_path = os.path.join(history_dir, history_filename)

                shutil.move(pdf_path, history_path)
                logger.info(f"  ✓ Fichier déplacé vers history/{history_filename}")
            except Exception as e:
                logger.error(f"  ✗ Impossible de déplacer le fichier vers history: {e}")
        else:
            logger.error(
                f"  ✗ Échec de l'impression - fichier conservé pour réessayer plus tard"
            )

        logger.info("")

    logger.info(f"{'=' * 60}")
    logger.info("Impression terminée\n")

    # Marquer les emails comme lus uniquement si leurs PDFs ont été imprimés avec succès
    if gmail_client and processed_emails:
        for message_id, pdf_files_list in processed_emails.items():
            # Vérifier si tous les fichiers de cet email ont été imprimés
            all_printed = all(pdf_file in printed_files for pdf_file in pdf_files_list)

            if all_printed:
                if gmail_client.mark_as_read(message_id):
                    logger.info(
                        f"✓ Email {message_id[:8]}... marqué comme lu après impression réussie"
                    )
                else:
                    logger.error(
                        f"✗ Impossible de marquer l'email {message_id[:8]}... comme lu"
                    )
            else:
                logger.warning(
                    f"⚠ Email {message_id[:8]}... non marqué comme lu (impression incomplète)"
                )


def is_working_hours():
    """Vérifie si on est dans les heures de travail"""
    current_hour = datetime.now().hour
    return WORK_START_HOUR <= current_hour < WORK_END_HOUR


def main():
    logger.info("=== Vinted Printer - Surveillance continue ===")
    logger.info(f"Intervalle de vérification: {CHECK_INTERVAL} minutes")
    logger.info(f"Heures de travail: {WORK_START_HOUR}h - {WORK_END_HOUR}h")
    logger.info("Appuyez sur Ctrl+C pour arrêter le programme\n")

    try:
        while True:
            current_time = datetime.now()
            current_hour = current_time.hour

            # Vérifier si on est dans les heures de travail
            if not is_working_hours():
                # Calculer le temps jusqu'à la prochaine heure de travail
                if current_hour < WORK_START_HOUR:
                    # On est avant l'heure de début, attendre jusqu'à WORK_START_HOUR
                    next_check = current_time.replace(
                        hour=WORK_START_HOUR, minute=0, second=0, microsecond=0
                    )
                else:
                    # On est après l'heure de fin, attendre jusqu'à demain WORK_START_HOUR
                    next_check = current_time.replace(
                        hour=WORK_START_HOUR, minute=0, second=0, microsecond=0
                    )
                    next_check = next_check.replace(day=next_check.day + 1)

                sleep_seconds = (next_check - current_time).total_seconds()
                logger.info(
                    f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Hors des heures de travail"
                )
                logger.info(
                    f"Prochaine vérification à {next_check.strftime('%Y-%m-%d %H:%M:%S')}"
                )
                time.sleep(sleep_seconds)
                continue

            logger.info(
                f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Vérification des nouveaux emails..."
            )

            result = process_emails()

            # Gérer le résultat
            if isinstance(result, tuple):
                success, processed_emails, gmail_client = result
            else:
                # Compatibilité avec l'ancien format (cas où il n'y a pas de nouveaux emails)
                success = result
                processed_emails = {}
                gmail_client = None

            # Après avoir traité les emails, imprimer les fichiers présents dans uploads
            print_uploaded_files(processed_emails, gmail_client)

            if success:
                logger.info(
                    f"Prochaine vérification dans {CHECK_INTERVAL} minute(s)..."
                )
                time.sleep(CHECK_INTERVAL * 60)
            else:
                logger.warning("Erreur rencontrée. Nouvelle tentative dans 1 minute...")
                time.sleep(60)

    except KeyboardInterrupt:
        logger.info("\n\nArrêt du programme demandé par l'utilisateur.")
        logger.info("Programme terminé.")
    except Exception as e:
        logger.error(f"Erreur fatale: {e}", exc_info=True)


if __name__ == "__main__":
    main()

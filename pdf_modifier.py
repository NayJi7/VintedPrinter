import logging
import re
from pypdf import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
import io

logger = logging.getLogger(__name__)

def extract_vinted_articles(email_subject):
    """Extrait la liste des articles Vinted depuis le sujet de l'email"""
    articles = []

    # Pattern dans le sujet: "pour B5 Veste pilou pilou" ou "pour H1 Ensemble neuf, H2 Ensemble neuf, ..."
    pattern = r'pour\s+(.+?)(?:\s*$)'
    match = re.search(pattern, email_subject, re.IGNORECASE)

    if match:
        items_text = match.group(1).strip()
        # Séparer par des virgules
        items = items_text.split(',')
        articles = [item.strip() for item in items if item.strip()]
        logger.info(f"Articles extraits du sujet: {articles}")

    return articles

def add_footer_to_pdf(pdf_data, footer_text):
    """Ajoute un footer avec le texte spécifié au PDF"""
    try:
        # Créer un lecteur PDF depuis les données
        pdf_reader = PdfReader(io.BytesIO(pdf_data))
        pdf_writer = PdfWriter()

        # Pour chaque page du PDF
        for page_num, page in enumerate(pdf_reader.pages):
            # Créer un nouveau PDF avec juste le footer
            packet = io.BytesIO()
            can = canvas.Canvas(packet, pagesize=A4)

            # Obtenir les dimensions de la page
            page_width = float(page.mediabox.width)
            page_height = float(page.mediabox.height)

            # Définir la police et la taille
            font_size = 7
            can.setFont("Helvetica", font_size)

            # Calculer la largeur du texte disponible (avec marges)
            margin = 40
            max_width = page_width - (2 * margin)

            # Découper le texte en plusieurs lignes si nécessaire
            from reportlab.pdfbase.pdfmetrics import stringWidth

            if stringWidth(footer_text, "Helvetica", font_size) > max_width:
                # Découper le texte en lignes
                words = footer_text.split(' | ')
                lines = []
                current_line = []

                for word in words:
                    test_line = ' | '.join(current_line + [word])
                    if stringWidth(test_line, "Helvetica", font_size) <= max_width:
                        current_line.append(word)
                    else:
                        if current_line:
                            lines.append(' | '.join(current_line))
                            current_line = [word]
                        else:
                            # Le mot est trop long, on le tronque
                            lines.append(word[:int(max_width / font_size)])

                if current_line:
                    lines.append(' | '.join(current_line))

                # Dessiner chaque ligne
                y_position = 20
                for line in reversed(lines):  # De bas en haut
                    can.drawString(margin, y_position, line)
                    y_position += font_size + 2
            else:
                # Le texte tient sur une ligne
                can.drawString(margin, 20, footer_text)

            can.save()

            # Rembobiner le buffer
            packet.seek(0)

            # Lire le PDF du footer
            footer_pdf = PdfReader(packet)
            footer_page = footer_pdf.pages[0]

            # Fusionner le footer avec la page originale
            page.merge_page(footer_page)
            pdf_writer.add_page(page)

        # Écrire le résultat dans un buffer
        output_buffer = io.BytesIO()
        pdf_writer.write(output_buffer)
        output_buffer.seek(0)

        logger.info(f"Footer ajouté au PDF: {footer_text}")
        return output_buffer.getvalue()

    except Exception as e:
        logger.error(f"Erreur lors de l'ajout du footer au PDF: {e}")
        return pdf_data  # Retourner le PDF original en cas d'erreur

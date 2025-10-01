import os
import logging
import tempfile
import subprocess
import shutil
import win32print
import win32api
from config import PRINTER_NAME

logger = logging.getLogger(__name__)

class Printer:
    def __init__(self):
        self.printer_name = PRINTER_NAME or self.get_default_printer()

    def get_default_printer(self):
        """Récupère l'imprimante par défaut si aucune n'est spécifiée"""
        try:
            default = win32print.GetDefaultPrinter()
            logger.info(f"Utilisation de l'imprimante par défaut: {default}")
            return default
        except Exception as e:
            logger.error(f"Impossible de récupérer l'imprimante par défaut: {e}")
            return None

    def list_printers(self):
        """Liste toutes les imprimantes disponibles"""
        printers = [printer[2] for printer in win32print.EnumPrinters(2)]
        return printers

    def print_pdf(self, pdf_data, filename):
        """Imprime un PDF"""
        if not self.printer_name:
            logger.error("Aucune imprimante configurée")
            return False

        # Vérifier que l'imprimante existe
        available_printers = self.list_printers()
        if self.printer_name not in available_printers:
            logger.error(f"Imprimante '{self.printer_name}' introuvable. Imprimantes disponibles: {available_printers}")
            return False

        tmp_path = None
        try:
            # Créer un fichier temporaire
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                tmp_file.write(pdf_data)
                tmp_path = tmp_file.name

            # Imprimer le fichier
            logger.info(f"Impression de {filename} sur {self.printer_name}")
            win32api.ShellExecute(
                0,
                "print",
                tmp_path,
                f'/d:"{self.printer_name}"',
                ".",
                0
            )

            # Nettoyer le fichier temporaire après un délai
            # (ne pas supprimer immédiatement car l'impression est asynchrone)
            logger.info(f"Impression de {filename} envoyée avec succès")

            # On pourrait implémenter une file d'attente pour supprimer le fichier plus tard
            # Pour l'instant on le laisse se faire nettoyer par le système

            return True

        except Exception as e:
            logger.error(f"Erreur lors de l'impression de {filename}: {e}")
            if tmp_path and os.path.exists(tmp_path):
                try:
                    os.unlink(tmp_path)
                except:
                    pass
            return False

    def find_sumatra_pdf(self):
        """Trouve SumatraPDF s'il est installé"""
        # Chemins courants pour SumatraPDF
        common_paths = [
            r"C:\Program Files\SumatraPDF\SumatraPDF.exe",
            r"C:\Program Files (x86)\SumatraPDF\SumatraPDF.exe",
            os.path.expanduser(r"~\AppData\Local\SumatraPDF\SumatraPDF.exe"),
        ]

        for path in common_paths:
            if os.path.exists(path):
                return path

        # Chercher dans PATH
        sumatra = shutil.which("SumatraPDF.exe")
        if sumatra:
            return sumatra

        return None

    def print_pdf_file(self, pdf_path):
        """Imprime un fichier PDF depuis son chemin"""
        if not self.printer_name:
            logger.error("Aucune imprimante configurée")
            return False

        if not os.path.exists(pdf_path):
            logger.error(f"Fichier introuvable: {pdf_path}")
            return False

        # Vérifier que l'imprimante existe
        available_printers = self.list_printers()
        if self.printer_name not in available_printers:
            logger.error(f"Imprimante '{self.printer_name}' introuvable. Imprimantes disponibles: {available_printers}")
            return False

        try:
            # Convertir en chemin absolu
            abs_path = os.path.abspath(pdf_path)

            logger.info(f"Impression de {os.path.basename(pdf_path)} sur {self.printer_name}")

            # Méthode 1: Utiliser SumatraPDF (le plus fiable pour l'impression automatique)
            sumatra_path = self.find_sumatra_pdf()
            if sumatra_path:
                logger.info(f"Utilisation de SumatraPDF: {sumatra_path}")
                try:
                    result = subprocess.run(
                        [sumatra_path, '-print-to', self.printer_name, '-silent', abs_path],
                        capture_output=True,
                        timeout=30
                    )

                    if result.returncode == 0:
                        logger.info(f"Impression de {os.path.basename(pdf_path)} envoyée avec succès via SumatraPDF")
                        return True
                    else:
                        raise Exception(f"SumatraPDF returned code {result.returncode}")

                except Exception as e:
                    logger.warning(f"SumatraPDF échoué: {e}, tentative avec méthode alternative...")

            # Méthode 2: Utiliser Adobe Reader si installé
            adobe_paths = [
                r"C:\Program Files\Adobe\Acrobat DC\Acrobat\Acrobat.exe",
                r"C:\Program Files (x86)\Adobe\Acrobat Reader DC\Reader\AcroRd32.exe",
                r"C:\Program Files\Adobe\Acrobat Reader DC\Reader\AcroRd32.exe",
            ]

            for adobe_path in adobe_paths:
                if os.path.exists(adobe_path):
                    logger.info(f"Utilisation d'Adobe Reader: {adobe_path}")
                    try:
                        result = subprocess.run(
                            [adobe_path, '/t', abs_path, self.printer_name],
                            capture_output=True,
                            timeout=30
                        )

                        logger.info(f"Impression de {os.path.basename(pdf_path)} envoyée avec succès via Adobe Reader")
                        return True

                    except Exception as e:
                        logger.warning(f"Adobe Reader échoué: {e}, tentative avec méthode alternative...")
                        break

            # Méthode 3: Fallback avec ShellExecute (peut ne pas fonctionner avec Chrome)
            logger.warning("Aucun lecteur PDF en ligne de commande trouvé, utilisation de ShellExecute...")
            win32api.ShellExecute(
                0,
                "print",
                abs_path,
                None,
                ".",
                0
            )

            logger.info(f"Impression de {os.path.basename(pdf_path)} envoyée avec succès via ShellExecute")
            return True

        except Exception as e:
            logger.error(f"Erreur lors de l'impression de {pdf_path}: {e}")
            return False

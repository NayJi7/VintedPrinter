"""
Script pour lister toutes les imprimantes disponibles sur Windows
"""
import win32print

def list_all_printers():
    """Liste toutes les imprimantes disponibles"""
    print("=" * 60)
    print("Liste des imprimantes disponibles :")
    print("=" * 60)

    printers = win32print.EnumPrinters(win32print.PRINTER_ENUM_LOCAL | win32print.PRINTER_ENUM_CONNECTIONS)

    if not printers:
        print("Aucune imprimante trouvée")
        return

    for i, printer in enumerate(printers, 1):
        printer_name = printer[2]
        print(f"\n{i}. {printer_name}")

    print("\n" + "=" * 60)

    # Imprimante par défaut
    try:
        default = win32print.GetDefaultPrinter()
        print(f"Imprimante par défaut : {default}")
    except:
        print("Aucune imprimante par défaut définie")

    print("=" * 60)
    print("\nCopiez le nom exact de votre imprimante dans le fichier .env")
    print("Exemple : PRINTER_NAME=Samsung CLX-3180 Series")

if __name__ == "__main__":
    list_all_printers()

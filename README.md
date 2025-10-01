# Vinted Printer - Automatic Shipping Label Printer

---

## 📋 Project Description

Vinted Printer is an automated solution for Vinted sellers that monitors your Gmail inbox, downloads shipping labels from Vinted emails, adds custom footers with article information, and automatically prints them on your printer. Perfect for managing multiple sales without manual intervention!

## ✨ Main Features

- 🔍 **Automatic Gmail monitoring** - Checks for new Vinted shipping labels at configurable intervals
- 📧 **Smart email filtering** - Uses Gmail labels to identify Vinted shipping emails
- 📄 **PDF modification** - Adds a custom footer with article names to each shipping label
- 🖨️ **Automatic printing** - Sends labels to your printer silently
- ⏰ **Working hours scheduling** - Only operates during configured business hours (8h-22h by default)
- ✅ **Email status management** - Marks emails as read only after successful printing
- 📊 **Detailed logging** - Tracks all operations with comprehensive logs
- 🔄 **Retry mechanism** - Keeps failed prints for retry on next cycle

## 🎯 The Workflow

### How It Works

1. **Monitor Gmail** - Continuously checks your Gmail for new emails with the configured label
2. **Extract information** - Retrieves PDF attachments and article names from email subjects
3. **Modify PDFs** - Adds a footer with article count and names (e.g., "4 articles : Article1 | Article2 | Article3 | Article4")
4. **Print automatically** - Sends modified PDFs to your configured printer
5. **Mark as processed** - Marks emails as read only after successful printing
6. **Clean up** - Removes printed files from the uploads folder

### Smart Features

- 🌙 **Night mode** - Automatically pauses during non-working hours
- 🔁 **Auto-retry** - Keeps unprinted files and retries in the next cycle
- 📱 **Remote access compatible** - Works with closed laptop lid via AnyDesk
- 🛡️ **Token refresh** - Automatically renews Gmail API access tokens

## 🏆 Use Case

Perfect for Vinted sellers who:

- ✅ Process **multiple sales per day**
- ✅ Want to **save time** on manual printing
- ✅ Need **organized tracking** of printed labels
- ✅ Want to **identify articles** directly on shipping labels
- ✅ Run a **dedicated printing station** (laptop + printer)

## 🛠️ Technologies Used

- **Language:** Python 3.12
- **Gmail Integration:** Google Gmail API (OAuth 2.0)
- **PDF Processing:** pypdf, reportlab
- **Printing:** win32print, SumatraPDF
- **Configuration:** python-dotenv
- **Platform:** Windows (with pywin32)

## 🚀 Quick Start

### Prerequisites

- Windows PC (laptop recommended)
- Python 3.12
- Gmail account
- Printer connected to the PC
- Google Cloud Console account (free)

### Installation

See detailed installation guides:

- 🇫🇷 [Installation Guide (French)](INSTALLATION.fr.md)
- 🇬🇧 [Installation Guide (English)](INSTALLATION.en.md)

### Quick Setup

1. **Configure Google Cloud Console** (Gmail API)
2. **Install Python 3.12** and dependencies
3. **Install SumatraPDF** for reliable printing
4. **Configure `.env` file** with your settings
5. **Run the program:** `python main.py`

## 🎓 Learning Outcomes

This project helped me:

- 🔐 **Master OAuth 2.0** authentication with Google APIs
- 📄 **Manipulate PDFs** programmatically with Python
- 🖨️ **Handle Windows printing** systems and drivers
- ⏰ **Implement scheduling** and time-based automation
- 🔧 **Create robust error handling** and retry mechanisms
- 📱 **Configure remote access** solutions for unattended operation

## 🔧 Technical Architecture

```
📦 vintedprinter/
├── 🐍 main.py              # Main application loop
├── 📧 gmail_client.py      # Gmail API integration
├── 🖨️ printer.py            # Printing logic (SumatraPDF/Adobe)
├── 📄 pdf_modifier.py      # PDF footer modification
├── ⚙️ config.py             # Configuration management
├── 📋 list_printers.py     # Printer discovery utility
├── 📁 uploads/             # Temporary PDF storage
├── 🔑 credentials.json     # Google OAuth credentials (not included)
├── 🎫 token.json           # Gmail API token (auto-generated)
├── ⚙️ .env                  # Environment configuration
└── 📊 vinted_printer.log   # Application logs
```

## 🎮 Configuration Options

### Environment Variables (.env)

```env
GMAIL_LABEL=Vinted Bordereaux    # Gmail label name
CHECK_INTERVAL=90                # Check interval (minutes)
PRINTER_NAME=Samsung CLX-3180    # Printer name
WORK_START_HOUR=8                # Start time (24h format)
WORK_END_HOUR=22                 # End time (24h format)
LOG_LEVEL=INFO                   # Log level (DEBUG/INFO/WARNING/ERROR)
```

### Laptop Configuration (Closed Lid Operation)

Run these PowerShell commands as administrator to keep your laptop running with the lid closed:

```powershell
# Prevent sleep when lid is closed
powercfg /setacvalueindex SCHEME_CURRENT 4f971e89-eebd-4455-a8de-9e59040e7347 5ca83367-6e45-459f-a27b-476b1d01c936 0
powercfg /setdcvalueindex SCHEME_CURRENT 4f971e89-eebd-4455-a8de-9e59040e7347 5ca83367-6e45-459f-a27b-476b1d01c936 0

# Disable automatic sleep
powercfg /change standby-timeout-ac 0
powercfg /change standby-timeout-dc 0

# Apply settings
powercfg /setactive SCHEME_CURRENT
```

## 📸 Example Output

```
=== Vinted Printer - Surveillance continue ===
Intervalle de vérification: 30 minutes
Heures de travail: 8h - 22h

[2025-10-01 08:00:00] Vérification des nouveaux emails...

============================================================
Statistiques du label 'Vinted Bordereaux':
  - Total: 5 email(s)
  - Non lus: 2 email(s)
  - Lus: 3 email(s)
============================================================

Email 1:
  Sujet: Bordereau d'envoi Vinted - pour Veste pilou pilou
  Articles trouvés: 1 article : Veste pilou pilou
  ✓ Impression réussie
  ✓ Fichier supprimé après impression
  ✓ Email marqué comme lu

Prochaine vérification dans 30 minute(s)...
```

## 🔒 Security & Privacy

- ✅ **OAuth 2.0 authentication** - No password storage
- ✅ **Local processing** - PDFs processed on your machine
- ✅ **Auto token refresh** - No manual intervention needed
- ✅ **Gitignore protection** - Sensitive files excluded from version control
- ✅ **Test mode** - Gmail API runs in test mode for personal use

## 🐛 Troubleshooting

### Common Issues

**Printing fails:**

- ✅ Install SumatraPDF (recommended)
- ✅ Check printer is turned on and connected
- ✅ Verify printer name in `.env` matches exactly

**Gmail authentication errors:**

- ✅ Check `credentials.json` is present
- ✅ Verify OAuth consent screen is configured
- ✅ Add your Gmail as a test user

**Emails not detected:**

- ✅ Create the Gmail label exactly as configured
- ✅ Apply label to Vinted shipping emails
- ✅ Check label name in `.env`

---

## 👥 Contributors

<a href="https://github.com/NayJi7/VintedPrinter/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=NayJi7/VintedPrinter" />
</a>

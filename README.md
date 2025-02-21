# File Watcher Application

This project is a Python application that monitors a specified directory for new files with the extensions `.csv` and `.txt`. It checks for new files every five minutes and sends any detected files via email to a specified address.

## Project Structure

```
file-watcher-app
├── src
│   ├── main.py          # Main entry point of the application
│   └── utils
│       └── email_sender.py  # Utility for sending emails with attachments
├── requirements.txt     # Project dependencies
└── README.md            # Project documentation
```

## Setup Instructions

1. Clone the repository:
   ```
   git clone https://github.com/microsoft/vscode-remote-try-python.git
   cd file-watcher-app
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Configure the email settings in `src/utils/email_sender.py` to specify the email account and recipient.

## Usage

1. Run the application:
   ```
   python src/main.py
   ```

2. The application will start monitoring the specified directory. If new `.csv` or `.txt` files are added, they will be sent to the configured email address.

## License

This project is licensed under the MIT License.
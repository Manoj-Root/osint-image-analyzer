# OSINT Image Analyzer

[![Python](https://img.shields.io/badge/python-3.10+-blue)](https://www.python.org/)

**Developed by Manoj Kumar | cybergodfather**  
A CLI-based digital forensics and OSINT tool for analyzing images.

---

## ⚡ Features

- **EXIF Analysis**: Extracts metadata like camera, software, GPS coordinates, and timestamps.
- **Steganography Detection**: Detects hidden messages and files using `steghide`, `binwalk`, `zsteg` (Linux), and hidden strings scanning.
- **Vision Analysis**:
  - Performs OCR (extracts visible text from images)
  - Image hashing (aHash, pHash, dHash, wHash)
  - Error Level Analysis (ELA) for detecting image tampering
- Cross-platform support (Windows & Linux)

---

## 📥 Installation

1. Clone the repository:

git clone 

cd osint-image-analyzer

  2. Create a virtual environment and activate it:

python -m venv venv

source venv/bin/activate  # Linux/macOS

venv\Scripts\activate     # Windows

  3. Install the requirements:

pip install -r requirements.txt

  4. Install OS-specific tools:

### Linux:

sudo apt update

sudo apt install binwalk binutils vim-common steghide tesseract-ocr


## 🚀 Usage

EXIF Analysis: 

python -m osint_tool.cli exif test-data/sample.jpg

## Steganography Analysis:

python -m osint_tool.cli stego test-data/sample.jpg
### with password
python -m osint_tool.cli stego test-data/hidden.jpg -p yourpassword
### with password list
python -m osint_tool.cli stego test-data/hidden.jpg -w password_list.txt

## Vision Analysis:

python -m osint_tool.cli vision test-data/sample.jpg

## Full Analysis (EXIF + Stego + Vision):

python -m osint_tool.cli analyze test-data/sample.jpg

## 🗂 Folder Structure

osint-image-analyzer/

│
├── osint_tool/

│   ├── __init__.py

│   ├── cli.py

│   ├── exif_module.py

│   ├── stego_module.py

│   └── vision_module.py

│

├── test-data/       # Sample images for testing

├── text.txt         # Optional text files for stego

├── requirements.txt

└── README.md

## ⚖️ Disclaimer

---> All rights belong to Manoj Kumar, the creator of this tool.

---> This tool is for educational purposes only.

---> Open for anyone to use, learn from, and contribute to.

---> Do not use for illegal or malicious activities.

## 🤝 Contributions

This is primarily a learning project for digital forensics and OSINT. Contributions are welcome, especially around:

* Better stego detection

* Advanced image tampering detection

* Integration with online OSINT platforms

## License

All rights reserved © Manoj Kumar. Educational use only.





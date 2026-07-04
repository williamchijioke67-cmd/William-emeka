# 🔒 File Integrity Monitor (FIM)

This project is a simple File Integrity Monitor (FIM) built with Python and CustomTkinter. It allows you to monitor a folder on your computer and detect if any files have been modified, deleted, or newly added.

The application works by creating a **SHA-256 hash** of every file in a selected folder. When you scan the folder again, it compares the current hashes with the original ones and reports any differences. This makes it useful for learning about file integrity, cybersecurity concepts, and basic system monitoring.

---

## ✨ Features

- Easy-to-use graphical interface built with **CustomTkinter**
- Monitor any folder on your computer
- Create a baseline of your files using **SHA-256 hashing**
- Detect:
  - Modified files
  - Deleted files
  - Newly added files
- Save and compare file hashes
- Lightweight and beginner-friendly

---

## 🛠 Requirements

Before running the project, make sure you have:

- Python 3.8 or newer
- Git
- pip (Python package manager)

---

## 📥 Installation

### Clone the repository

```bash
git clone https://github.com/williamchijioke67-cmd/William-emeka.git
cd William-emeka
```

### Install the required package

```bash
pip install customtkinter
```

or

```bash
pip3 install customtkinter
```

---

## ▶️ Running the Program

Start the application by running:

```bash
python3 fim.py
```

or

```bash
python fim.py
```

Replace `fim.py` with your Python filename if it has a different name.

---

## 🚀 How It Works

1. Launch the application.
2. Select the folder you want to monitor.
3. Create a baseline. This saves the current SHA-256 hashes of every file.
4. Make changes to the folder (add, delete, or modify files).
5. Run another scan.
6. The application will show which files have changed.

---

## 📚 Why I Built This

I created this project to improve my Python programming skills while learning about cybersecurity. File Integrity Monitoring is an important security concept used to detect unauthorized changes to files, and this project helped me understand how hashing can be used to verify file integrity.

---

## 🔮 Future Improvements

- Real-time monitoring
- Email notifications
- Log file generation
- Export scan results
- Support for multiple hashing algorithms
- Better UI and themes

---

## 🤝 Contributions

Suggestions and improvements are always welcome. Feel free to fork the project, open an issue, or submit a pull request.

---

## 📄 License

This project is open source and available under the MIT License.

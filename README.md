# STUDENT AI – The Never-Tired Student 🎓🤖

> "Teachers may get tired of giving work, but the Student AI never gets tired of doing it."

Student AI is a production-ready, highly intelligent web application designed to simulate a perfect student. Whether it's writing assignments, solving complex problems, generating study notes, or drafting formal letters, Student AI handles it all instantly with multiple personalities and professional export options.

![Student AI Preview](https://via.placeholder.com/800x400.png?text=Student+AI+Interface+Preview)

## ✨ Key Features

- **🤖 Multi-Personality AI**: Choose between a *Hardworking*, *Funny*, or *Smart Topper* student persona.
- **📝 Automatic Task Completion**: 
  - **Assignments**: Full academic essays with proper structure.
  - **Solvers**: Step-by-step solutions to teacher-provided problems.
  - **Notes**: Comprehensive study guides and chapter summaries.
  - **Letters**: Professional formal and informal correspondence.
- **🎙️ Voice Commands**: Interact with the AI using integrated Speech-to-Text.
- **📂 Professional Exports**: 
  - High-quality **PDF** with customizable styles.
  - **Handwritten PDF** mode for a personal touch.
  - Editable **DOCX** (Word) and **TXT** files.
- **🎨 Glassmorphism UI**: A sleek, modern dark-themed dashboard with smooth animations.
- **🛡️ Secure & Scalable**: Engineered with Flask, PostgreSQL, and production-grade security (CSRF protection, rate limiting, connection pooling).

## 🚀 Tech Stack

- **Frontend**: HTML5, Vanilla CSS (Glassmorphism), JavaScript (ES6+).
- **Backend**: Python Flask.
- **Database**: PostgreSQL with SQLAlchemy ORM.
- **AI Engine**: HuggingFace Inference API (`zephyr-7b-beta`).
- **Export Engine**: `xhtml2pdf`, `python-docx`, `reportlab`.

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.8+
- PostgreSQL
- HuggingFace API Key

### 1. Clone the Repository
```bash
git clone https://github.com/harshith1432/Student-AI.git
cd Student-AI
```

### 2. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment
Create a `.env` file in the root directory:
```env
SECRET_KEY=your_secret_key_here
DATABASE_URL=postgresql://user:password@localhost:5432/student_ai
HF_API_KEY=your_huggingface_api_key_here
```

### 5. Initialize Database
```python
python
>>> from extensions import db
>>> from app import create_app
>>> app = create_app()
>>> with app.app_context():
...     db.create_all()
```

### 6. Run Application
```bash
python run.py
```
Visit `http://localhost:5000` to start working!

## 📸 Screenshots

*Registration & Dashboard*
*Coming Soon...*

## 📜 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

---
Created with ❤️ by Harshith

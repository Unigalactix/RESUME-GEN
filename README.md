# 🚀 AI Career Suite — RESUME-GEN

An AI-powered career optimization tool built with **Streamlit** and **Google Gemini AI**. It helps job seekers create ATS-optimized resumes, score their resume against a job description, and discover targeted job opportunities — all from their LinkedIn data export.

---

## ✨ Features

| Tool | Description |
|---|---|
| 📄 **AI Resume Generator** | Tailors your resume to a specific job description using your LinkedIn data. Outputs an editable Markdown resume and a downloadable PDF. |
| 📊 **Resume Score** | Analyzes how well your existing PDF resume matches a job description. Returns a 0–100 score, key strengths/weaknesses, and actionable suggestions. |
| 🔍 **Job Finder** | Identifies top hiring companies for your target role and generates Google Dork search links to find open roles directly on company ATS portals (Lever, Greenhouse, Workday, iCIMS). |

---

## 🛠️ Tech Stack

- **Python 3.11**
- **[Streamlit](https://streamlit.io/)** — Web UI
- **[Google Generative AI (Gemini)](https://ai.google.dev/)** — LLM for analysis and content generation
- **Pandas** — LinkedIn CSV data processing
- **fpdf2** — PDF generation
- **PyPDF2** — PDF text extraction
- **BeautifulSoup4 + Requests** — Job description extraction from URLs
- **python-dotenv** — Environment variable management

---

## 📋 Prerequisites

1. **Python 3.11** — [Download here](https://www.python.org/downloads/)
2. **Google Gemini API Key** — [Get one free at Google AI Studio](https://aistudio.google.com/app/apikey)
3. **LinkedIn Data Export** — Your personal LinkedIn data (CSV files)

---

## ⚡ Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/Unigalactix/RESUME-GEN.git
cd RESUME-GEN
```

### 2. Create a Virtual Environment (Recommended)

```bash
python3 -m venv venv
source venv/bin/activate       # macOS/Linux
venv\Scripts\activate          # Windows
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Your API Key

Create a `.env` file in the project root:

```bash
GEMINI_API_KEY=your_gemini_api_key_here
```

> ⚠️ **Never commit your `.env` file.** It is already listed in `.gitignore`.

### 5. Add Your LinkedIn Data

Export your LinkedIn data and place the CSV files in the `Data/` folder. See [LinkedIn Data Export Guide](#-linkedin-data-export-guide) below.

### 6. Run the App

```bash
streamlit run app.py
```

The application will open at **http://localhost:8501**.

---

## 🔑 Configuration

### Environment Variables

| Variable | Description |
|---|---|
| `GEMINI_API_KEY` | Your Google Gemini API key (required) |

### LinkedIn Data Export Guide

1. Go to **LinkedIn > Settings & Privacy > Data Privacy > Get a copy of your data**
2. Select **"Want something in particular? Select the data files you're most interested in"**
3. Check at minimum: **Profile, Positions, Education, Skills, Projects, Certifications**
4. Download the export (can take up to 24 hours)
5. Extract the ZIP and copy all CSV files into the `Data/` folder of this project

---

## 🖥️ Usage

### AI Resume Generator

1. Navigate to **AI Resume Generator** from the sidebar
2. Paste a job description or enter a job posting URL
3. Click **Generate Resume**
4. Review the generated Markdown resume and AI keyword suggestions
5. Edit the Markdown in-app if needed
6. Click **Download PDF** to save your tailored resume

### Resume Score

1. Navigate to **Resume Score** from the sidebar
2. Upload your existing resume as a **PDF**
3. Paste a job description or enter a job posting URL
4. Click **Score Resume**
5. Review your score (🟢 ≥80 · 🟡 ≥60 · 🔴 <60), strengths, weaknesses, and suggestions

### Job Finder

1. Navigate to **Find Jobs** from the sidebar
2. Enter your **target role** (e.g., `Senior Software Engineer`)
3. Optionally add a **location** (e.g., `San Francisco, CA`)
4. Click **Find Jobs**
5. Browse the list of target companies and click the generated **Google search links** to find open roles directly on their ATS portals

---

## 📁 Project Structure

```
RESUME-GEN/
├── app.py                  # Streamlit entry point — navigation & routing
├── data_loader.py          # Loads & parses LinkedIn CSV exports
├── matcher.py              # AI-powered skill & experience matching
├── markdown_generator.py   # Converts structured data to Markdown resume
├── pdf_generator.py        # Renders Markdown resume to PDF (fpdf2)
├── resume_formatter.py     # ATS formatting rules & helpers
├── requirements.txt        # Python dependencies
├── .env                    # API keys — NOT committed (add manually)
├── .gitignore
├── .devcontainer/
│   └── devcontainer.json   # VS Code Dev Container configuration
├── Data/                   # LinkedIn CSV exports & processed JSON data
│   ├── Process_data.py     # Data processing utilities
│   ├── update_data_json.py # Updates JSON cache from CSVs
│   ├── positions.json      # Cached positions data
│   ├── certs.json          # Cached certifications data
│   └── *.csv               # LinkedIn data export files
└── tools/                  # Feature modules (Streamlit page renderers)
    ├── __init__.py
    ├── resume_generator.py # AI Resume Generator page
    ├── resume_scorer.py    # Resume Score page
    └── job_finder.py       # Job Finder page
```

---

## 🧑‍💻 Development with VS Code Dev Containers

This repository includes a `.devcontainer` configuration for one-click setup with VS Code:

1. Install the **Dev Containers** extension in VS Code
2. Open the project folder in VS Code
3. Click **"Reopen in Container"** when prompted
4. The container will install all dependencies and automatically start the Streamlit app on port **8501**

---

## 🤝 Contributing

Contributions are welcome! To get started:

1. Fork the repository
2. Create a new branch: `git checkout -b feature/your-feature-name`
3. Make your changes and commit: `git commit -m "Add your feature"`
4. Push to your fork: `git push origin feature/your-feature-name`
5. Open a Pull Request

---

## 📄 License

This project is open source. See the repository for licensing details.

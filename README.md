# 🚀 AI Career Suite — RESUME-GEN

An AI-powered career optimization tool built with **Streamlit** and **Google Gemini AI**. It helps job seekers create ATS-optimized resumes, score their resume against a job description, and discover targeted job opportunities — all from their LinkedIn data export.

---

## ✨ Features

| Tool | Description |
|---|---|
| 📄 **AI Resume Generator** | Tailors your resume to a job description using LinkedIn export data, supports section toggles and resume variants, and outputs editable Markdown plus a downloadable PDF. |
| 📊 **Resume Score** | Analyzes how well your existing PDF resume matches a job description and now returns a score breakdown, gap map, rewrite priorities, and suggested replacement bullets. |
| 🔍 **Job Finder** | Identifies top hiring companies for your target role, adds structured filters for work authorization and job preferences, and generates Google Dork plus ATS-specific search links for company job boards. |

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

Copy the environment template and update it:

```bash
cp .env.example .env
```

Then set your API key in `.env`:

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

When the API key is missing, the app now surfaces a visible warning and AI-assisted features fall back to limited behavior where possible.

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
3. Choose a **resume variant** and pick the sections you want to include
4. Click **Generate Tailored Resume**
5. Review the generated Markdown resume, profile completeness insights, and AI keyword suggestions
6. Edit the Markdown in-app if needed
7. Click **Generate Final PDF** to save your tailored resume

### Resume Score

1. Navigate to **Resume Score** from the sidebar
2. Upload your existing resume as a **PDF**
3. Paste a job description or enter a job posting URL
4. Click **Score Resume**
5. Review your score (🟢 ≥80 · 🟡 ≥60 · 🔴 <60), category breakdown, gap analysis, rewrite priorities, and tailored bullets

### Job Finder

1. Navigate to **Find Jobs** from the sidebar
2. Choose a common role from the dropdown or enter your own custom role
3. Add filters such as **location**, **experience level**, **job mode**, and **industry focus**
4. If relevant, select a **work authorization focus** like `F-1 OPT friendly` or `H-1B sponsorship required`
5. Optionally start from a preset such as `F-1 OPT New Grad` or `H-1B Transfer`
6. Click **Generate Targets & Queries**
7. Browse the target companies, review the sponsorship signal, and open the generated **Google** or **ATS-specific** search links to find roles directly on company portals

### App Validation

The sidebar now shows whether:

1. Gemini is configured correctly
2. Your required LinkedIn export files are present
3. The app is running in fallback mode because of missing configuration

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

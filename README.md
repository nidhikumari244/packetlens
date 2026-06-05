# AI Network Troubleshooting Assistant

A portfolio-grade Streamlit application that helps users triage common network incidents using explainable rule-based protocol detection, Groq AI diagnosis, SQLite history, operational analytics, and downloadable incident reports.

This project is built for final-year B.Tech students who want a resume-ready project for Cisco, NOC, software engineering, AI support, and infrastructure internship roles.

## Why This Project Stands Out

Most AI chatbot projects only return plain text. This application behaves more like a lightweight NetOps incident triage tool:

- Classifies the issue before calling AI
- Extracts technical evidence such as IPs, domains, and commands
- Estimates severity and confidence
- Generates root cause, explanation, business impact, playbook, commands, prevention, and escalation guidance
- Stores incident history in SQLite
- Shows dashboard analytics for incident categories and severity mix
- Exports a professional text incident report
- Falls back to deterministic rule-based diagnosis when the API key is missing or the API fails

## Features

- Streamlit dashboard with incident KPIs
- Protocol/category analytics
- AI-assisted incident diagnosis
- Rule-based classifier for DNS, TCP/IP, HTTP/HTTPS, DHCP, Routing, Firewall, Wi-Fi, and Unknown
- Confidence scoring and extracted evidence
- Recommended commands for Windows, Linux, and Cisco-style workflows
- Escalation guidance for high-severity issues
- Searchable diagnosis history
- Category filtering
- Delete records
- Download incident reports
- Clean modular Python architecture
- Pytest test coverage for classifier and report generation

## Tech Stack

- Python
- Streamlit
- Groq API
- SQLite
- Pandas
- python-dotenv
- pytest

## Architecture

```text
ai-network-troubleshooting-assistant/
├── app.py                  # Streamlit UI and workflow orchestration
├── classifier.py           # Rule classifier, evidence extraction, severity logic
├── ai_engine.py            # Groq prompt, JSON normalization, fallback handling
├── database.py             # SQLite persistence and dashboard analytics
├── report_generator.py     # Downloadable incident report generation
├── requirements.txt
├── README.md
├── .env.example
├── sample_cases.md
└── tests/
    ├── test_classifier.py
    └── test_report_generator.py
```

## Diagnosis Pipeline

```text
User input/logs
    -> Rule-based protocol classification
    -> Evidence extraction
    -> Severity and confidence estimation
    -> Groq AI structured diagnosis
    -> Fallback playbook if AI is unavailable
    -> SQLite storage
    -> Dashboard/history/report export
```

## Setup

### 1. Open the project

```bash
cd ai-network-troubleshooting-assistant
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

Windows:

```bash
.venv\Scripts\activate
```

macOS/Linux:

```bash
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Add Groq API key

Copy `.env.example` to `.env`:

```bash
copy .env.example .env
```

Update `.env`:

```env
GROQ_API_KEY=your_actual_groq_api_key
```

The app still works without the key using rule-based fallback diagnosis.

### 5. Run the app

```bash
streamlit run app.py
```

### 6. Run tests

```bash
pytest
```

## Demo Inputs

```text
DNS lookup failed for portal.company.com. Ping to 8.8.8.8 works, but nslookup portal.company.com times out.
```

```text
DHCP not assigning IP. Client has 169.254.10.22 address and cannot access internal resources.
```

```text
Application traffic is blocked on port 443 after a firewall policy update. Ping works but HTTPS fails.
```

```text
traceroute stops after gateway while accessing 10.20.30.40. Other local devices are reachable.
```

More examples are available in `sample_cases.md`.

## Screenshots To Add On GitHub

After running the project, add screenshots for:

- Dashboard analytics
- Diagnose Issue page
- Incident triage output
- History page
- Downloaded incident report

## LinkedIn Post Caption

I built an AI Network Troubleshooting Assistant using Python, Streamlit, Groq API, and SQLite.

The project diagnoses common network incidents such as DNS failures, DHCP lease issues, packet loss, routing breaks, firewall blocks, Wi-Fi instability, and HTTP/HTTPS errors. It combines rule-based protocol classification with AI-generated troubleshooting playbooks, evidence extraction, confidence scoring, incident history, dashboard analytics, and downloadable reports.

This helped me connect networking fundamentals with practical AI and software engineering workflows.

## Resume Bullet Points

- Built an AI-powered Network Troubleshooting Assistant using Python, Streamlit, Groq API, and SQLite to triage DNS, DHCP, TCP/IP, routing, firewall, Wi-Fi, and HTTP/HTTPS incidents.
- Designed a hybrid diagnosis pipeline combining deterministic protocol classification, evidence extraction, severity estimation, confidence scoring, and LLM-generated troubleshooting playbooks.
- Implemented persistent SQLite incident history with search, category filtering, deletion, dashboard analytics, and downloadable incident reports.
- Added resilient error handling with missing API-key detection and rule-based fallback diagnosis to keep the application usable during outages and live demos.
- Created modular production-style Python components for classification, AI orchestration, database persistence, report generation, and Streamlit UI rendering.
- Added pytest coverage for classifier and report-generation logic to demonstrate maintainability and engineering discipline.

## Interview Talking Points

- Why rule-based classification is used before AI
- How fallback diagnosis improves reliability
- How SQLite stores incident history
- How confidence score and extracted evidence make the system explainable
- How this project can evolve into a FastAPI + Docker + CI/CD deployment

## Future Enhancements

- FastAPI backend
- Docker deployment
- PDF report export
- User authentication
- Cisco IOS command templates
- Packet capture parsing
- CI pipeline with automated tests

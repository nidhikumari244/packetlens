# PacketLens

PacketLens is an intelligent network diagnostics and troubleshooting platform built with **Python, Streamlit, Groq AI, and SQLite**. It classifies network incidents, generates structured troubleshooting playbooks, and provides analytics through an interactive dashboard.

---

## 🚀 Live Demo

👉 https://packetlens-nidhik.streamlit.app/

---

## 📦 Repository

👉 https://github.com/nidhikumari244/packetlens

---

## ✨ Features

* AI-assisted network troubleshooting using Groq API
* Rule-based classification for network issues
* Supports DNS, DHCP, TCP/IP, Routing, Firewall, HTTP/HTTPS, and Wi-Fi incidents
* Severity and confidence scoring for each diagnosis
* Structured troubleshooting playbook generation
* Incident history tracking using SQLite
* Analytics dashboard for insights into network issues
* Downloadable incident reports
* Fallback rule-based diagnosis when AI is unavailable

---

## 🧠 How It Works

```text
User Input (logs / symptoms)
        ↓
Rule-Based Classifier
        ↓
Groq AI Diagnosis Engine
        ↓
Evidence Extraction + Severity Scoring
        ↓
SQLite Storage
        ↓
Dashboard + Report Generation
```

---

## 🛠️ Tech Stack

* Python
* Streamlit
* Groq API
* SQLite
* Pandas
* Pytest

---

## 📁 Project Structure

```text
packetlens/
├── app.py                  # Streamlit UI
├── ai_engine.py           # AI diagnosis engine (Groq integration)
├── classifier.py          # Rule-based classification logic
├── database.py            # SQLite storage & analytics
├── report_generator.py    # Report generation module
├── requirements.txt
├── sample_cases.md
├── tests/
└── README.md
```

---

## ⚙️ Installation & Setup

### 1. Clone Repository

```bash
git clone https://github.com/nidhikumari244/packetlens.git
cd packetlens
```

### 2. Create Virtual Environment

```bash
python -m venv .venv
```

### 3. Activate Environment

**Windows**

```bash
.venv\Scripts\activate
```

**Linux / macOS**

```bash
source .venv/bin/activate
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Add Environment Variable

Create a `.env` file:

```env
GROQ_API_KEY=your_api_key_here
```

### 6. Run Application

```bash
streamlit run app.py
```

---

## 📊 Sample Issues Supported

* DNS resolution failures
* DHCP IP assignment issues
* Routing breaks and missing paths
* Firewall blocking traffic
* HTTP/HTTPS connectivity failures
* Wi-Fi instability
* TCP/IP packet loss and routing issues

---

## 🧪 Testing

```bash
pytest
```

---

## 📸 Screenshots

### Dashboard

<img width="1904" height="863" alt="Dashboard " src="https://github.com/user-attachments/assets/0647000c-ad35-4715-8177-d5875718cbcb" />

### Incident Analysis

<img width="1918" height="866" alt="diagnosis issue (1)" src="https://github.com/user-attachments/assets/ea461b61-3059-4dbe-8764-1d7daf36b270" />
<img width="1919" height="858" alt="Diagnosis issue " src="https://github.com/user-attachments/assets/2501f31e-bd4c-40a0-b656-c61118e19b40" />

### Incident History

<img width="1919" height="857" alt="History" src="https://github.com/user-attachments/assets/b072d2ae-3cfb-4738-ac6b-0d586062ad9b" />

### Report Generation

<img width="1919" height="734" alt="about project" src="https://github.com/user-attachments/assets/8aed6a84-2357-47a6-92eb-2c3bfe0f0955" />

---

## 📈 Future Improvements

* FastAPI backend for scalability
* Docker containerization
* Real-time network monitoring
* Packet capture analysis (Wireshark integration)
* PDF report export
* Authentication system
* CI/CD pipeline using GitHub Actions

---

## 🏆 Why This Project Matters

PacketLens demonstrates:

* Practical understanding of **computer networks**
* Ability to build **AI + rule-based hybrid systems**
* Real-world **incident troubleshooting workflow**
* Full-stack development skills using Python
* Production-style project structure with testing and persistence

---

## 📄 License

MIT License

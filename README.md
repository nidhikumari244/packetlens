## 🚀 Live Demo

👉 https://packetlens-nidhik.streamlit.app/

## 📦 Repository

https://github.com/nidhikumari244/packetlens

# PacketLens

PacketLens is a network diagnostics and troubleshooting platform built with Python and Streamlit. It helps analyze common network issues, classify incidents, generate troubleshooting guidance, and maintain incident history through an interactive dashboard.

## Features

* AI-assisted network troubleshooting
* Rule-based network issue classification
* DNS, DHCP, Routing, Firewall, TCP/IP, HTTP/HTTPS and Wi-Fi analysis
* Severity and confidence scoring
* Incident history management with SQLite
* Dashboard analytics and reporting
* Downloadable troubleshooting reports
* Fallback diagnosis when AI service is unavailable

## Tech Stack

* Python
* Streamlit
* Groq API
* SQLite
* Pandas
* Pytest

## Project Structure

```text
packetlens/
├── app.py
├── ai_engine.py
├── classifier.py
├── database.py
├── report_generator.py
├── requirements.txt
├── sample_cases.md
├── tests/
└── README.md
```

## Installation

Clone the repository:

```bash
git clone https://github.com/nidhikumari244/packetlens.git
cd packetlens
```

Create a virtual environment:

```bash
python -m venv .venv
```

Activate the environment:

Windows:

```bash
.venv\Scripts\activate
```

Linux/macOS:

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create a `.env` file:

```env
GROQ_API_KEY=your_api_key_here
```

Run the application:

```bash
streamlit run app.py
```

## Sample Issues

* DNS resolution failures
* DHCP address assignment issues
* Routing problems
* Firewall rule blocks
* HTTP/HTTPS connectivity failures
* Wi-Fi instability
* TCP/IP communication issues

## Testing

Run tests using:

```bash
pytest
```

## Screenshots

* Dashboard
<img width="1904" height="863" alt="Dashboard " src="https://github.com/user-attachments/assets/0647000c-ad35-4715-8177-d5875718cbcb" />

* Incident Analysis
<img width="1918" height="866" alt="diagnosis issue (1)" src="https://github.com/user-attachments/assets/ea461b61-3059-4dbe-8764-1d7daf36b270" />
<img width="1919" height="858" alt="Diagnosis issue " src="https://github.com/user-attachments/assets/2501f31e-bd4c-40a0-b656-c61118e19b40" />

* Incident History
<img width="1919" height="857" alt="History" src="https://github.com/user-attachments/assets/b072d2ae-3cfb-4738-ac6b-0d586062ad9b" />

* Report Generation
<img width="1919" height="734" alt="about project" src="https://github.com/user-attachments/assets/8aed6a84-2357-47a6-92eb-2c3bfe0f0955" />

## License

MIT License

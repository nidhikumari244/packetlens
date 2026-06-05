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

Add screenshots of:

* Dashboard
* Incident Analysis
* Analytics Page
* Report Generation

## License

MIT License

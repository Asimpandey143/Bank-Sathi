# 🏦 BankSathi — Accessible, Family-Protected Digital Banking

> **"Shared guidance, not shared access."**  
> Accessible, voice-first digital banking tailored for Indian seniors, featuring **Trusted Circle** advisory second opinions with zero screen-sharing and zero helper PIN/account access.

---

## 🌟 Overview

Millions of seniors and digitally inexperienced individuals in India struggle with modern UPI and net-banking interfaces. Conventional solutions often resort to screen-sharing tools (like AnyDesk or TeamViewer), which lead to devastating fraud, OTP theft, and loss of financial autonomy.

**BankSathi** redesigns digital banking around dignity, clarity, and safety:
1. **Conversational Voice Banking**: Speak naturally in your native language (*"Send five thousand rupees to Ravi"*).
2. **Behavioral Risk Engine**: Automatically detects unusual transfers that deviate from established baselines (e.g. ₹5,000 vs. ₹1,500 baseline).
3. **Trusted Circle Protocol**: Sends a privacy-safe alert to a trusted family member (e.g. Daughter Ananya) for an **advisory second opinion** without giving them access to your account or PIN.
4. **User-Only Authorization**: The helper can give an advisory opinion (`Looks Expected` or `Don't Recognize This`), but **only the user** can authorize and confirm the final payment.
5. **Google Pay (GPay India) UI/UX Format**: Designed with Google Material 3 and Stitch AI for seamless familiarity.

---

## 🚀 Key Features

### 1. 🛡️ Trusted Circle & Advisory Second Opinion
* **Zero Screen-Sharing**: No remote screen access, no OTP/PIN exposure, and no account takeover risk.
* **Advisory Feedback**: Trusted family members provide real-time guidance:
  * `✓ Looks Expected`
  * `⚠️ Don't Recognize This`
  * `❓ Request User Verification`
* **Server-Side Enforcement**: Backend enforces `HTTP 403 Forbidden` if anyone other than the primary user attempts to confirm a payment.

### 2. 🎙️ Natural Voice & Intent Extraction
* Web Speech API integration for real-time speech recognition (STT) and voice synthesis (TTS).
* Parses natural speech into structured banking intents (`TRANSFER`, `PAY_BILL`, `CHECK_BALANCE`).
* Interactive ambiguity resolution: prompts user for clarification if amount or recipient is missing.
* **Synchronized Captions Banner**: Audio is paired with real-time visual captions for hearing accessibility.

### 3. 🔍 Behavioral Risk Engine
* Analyzes transaction history and computes personal spending baselines.
* Deterministic scoring across four risk tiers: `LOW`, `MEDIUM`, `HIGH`, `CRITICAL`.
* Plain-language risk explanations rather than technical security jargon.

### 4. ♿ WCAG AAA Accessibility Suite
* **Dynamic Font Scaling**: Instant `A-` / `A+` controls (0.85x to 2.0x zoom) across all components.
* **High Contrast Mode**: 1-click toggle between standard and high-contrast color schemes.
* **56px Touch Target Standard**: Oversized, tactile interactive elements for motor accessibility.
* **Multi-Language Support**: English, Hindi, Marathi, Gujarati, Bengali, and Tamil.

### 5. 📱 Google Pay (GPay India) Format UI/UX (Stitch AI)
* Pristine white canvas with Material 3 elevation and soft diffused shadows.
* Full-width GPay pill search and voice bar.
* 4-Column quick action circles: **Scan QR**, **Pay Contacts**, **Bank Transfer**, **Trusted Circle**.
* Horizontal scrollable **People** avatars for 1-tap payments.
* Account balance tile with tap-to-hide/show and **🔊 Read Balance** audio speaker button.

---

## 🏗️ Tech Stack

### Frontend
- **Framework**: React 18 + Vite + TypeScript
- **Styling**: Vanilla CSS with Stitch Design System Tokens (Lexend typography, Material 3 palette)
- **Voice / Audio**: Web Speech API (SpeechRecognition + SpeechSynthesis)

### Backend
- **Framework**: FastAPI (Python 3.11)
- **Database**: SQLAlchemy 2.0 (Async) + SQLite (Local) / PostgreSQL (Production)
- **Security**: JWT Authentication (OAuth2 Bearer), Argon2 / Passlib password hashing
- **Testing**: Pytest (100% test pass rate across 54 unit and integration tests)

---

## 🏁 Quickstart Guide

### Prerequisites
- Python 3.11+
- Node.js 18+ and npm

### 1. Clone the Repository
```bash
git clone https://github.com/Asimpandey143/Bank-Sathi.git
cd Bank-Sathi
```

### 2. Backend Setup
```bash
cd banksaathi/backend

# Create and activate virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1  # On Windows PowerShell
# source .venv/bin/activate    # On Linux/macOS

# Install dependencies
pip install -r requirements.txt

# Run database seed (Pre-populates Meena Devi & Daughter Ananya)
python seed_demo.py

# Start FastAPI backend
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```
Backend API will be live at: **http://127.0.0.1:8000**  
Interactive API Docs (Swagger): **http://127.0.0.1:8000/docs**

### 3. Frontend Setup
```bash
cd ../frontend

# Install dependencies
npm install

# Start Vite dev server
npm run dev
```
Frontend application will be live at: **http://localhost:5173**

---

## 🎭 Pre-Seeded Demo Credentials

| Role | Name | Phone Number | Password | Profile |
| :--- | :--- | :--- | :--- | :--- |
| **Primary User (Mother)** | **Meena Devi** | `9999999001` | `demoPassword123!` | ₹50,000 balance, ₹1,500 transfer baseline |
| **Trusted Circle (Daughter)** | **Ananya** | `9999999002` | `daughterPassword123!` | Active protector with advisory second-opinion access |

---

## 🎬 Testing the Live Demo Scenario

1. Open [**http://localhost:5173**](http://localhost:5173).
2. Click **`▶️ Run ₹5,000 Demo Story`** in the top demo controller bar.
3. The AI parses the request to send ₹5,000 to Ravi Kumar. Click **`Review Transaction & Risk Check →`**.
4. The Risk Engine flags the transaction as **HIGH / MEDIUM Risk** and sends a privacy-safe alert to Daughter Ananya.
5. In the top bar, click **`🛡️ 2. Daughter (Ananya)`** to view the alert and submit **`✓ Looks Expected`**.
6. Switch back by clicking **`👵 1. Mother (Meena)`**. Review her daughter's advisory badge and click **`Confirm Payment`** to execute the transfer.

---

## 🧪 Automated Tests

Run backend pytest suite:
```bash
cd banksaathi/backend
pytest tests/ -q
```
Result: **54 passed in ~30s (100% test coverage)**.

---

## 📄 License

Distributed under the MIT License. See `LICENSE` for details.

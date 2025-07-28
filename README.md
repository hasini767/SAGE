#  SAGE – AI Wellness Assistant

SAGE (Self-Awareness and Guidance Engine) is a personalized wellness web application that helps users improve their mental well-being through AI-driven conversation, journaling, mindfulness tools, and emotional tracking.

## Features

### AI Chatbot – SAGE
- Built using OpenAI GPT-4 API
- Provides empathetic and thoughtful responses
- Designed for stress relief, wellness advice, and emotional support
- Typing animation ("SAGE is typing...") for realistic interaction
- SQLite-based chat history per user

### Journal
- Create, save, and view personal journal entries
- Upload handwritten notes using image-based OCR
- Stored securely in a local SQLite database

### Emotion Log Upload
- Upload `.txt` files with mood or reflection logs
- Automatically parsed and displayed in the journal interface

### Stress Relief Games
- Mini browser-based games (e.g., Screen Pet, Spinner)
- Accessible through the `/games` page

### Yoga & Meditation
- Curated set of images/videos for mindfulness and relaxation
- Step-by-step breathing and stretching techniques

### Authentication
- Firebase Authentication (Email/Password)
- Session management with user-specific journal/chat data

---

## 🛠️ Tech Stack

| Frontend       | Backend          | AI & ML           | Database       | Auth         |
|----------------|------------------|-------------------|----------------|--------------|
| HTML, CSS, JS  | Python, Flask    | OpenAI GPT-4 API  | SQLite (local) | Firebase     |

---

## Getting Started

### Prerequisites

- Python 3.10+
- Flask
- OpenAI Python SDK
- Firebase config (for Auth)
- Tesseract OCR (for image-to-text journal uploads)

### Installation

```bash
# Clone the repo
git clone https://github.com/your-username/sage-wellness-app.git
cd sage-wellness-app

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt

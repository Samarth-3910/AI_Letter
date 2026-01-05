# GhostWriter AI ✍️

**GhostWriter AI** is a smart personal letter-writing assistant.  
It reads your sample texts or images to mimic your unique writing style (tone, vocabulary, structure) and generates professional letters that sound exactly like you.

---

## 🚀 How It Works (Workflow)

Here is the journey your data takes when you use the app:

```mermaid
graph TD
    User((User))
    Frontend[Frontend UI \n(Next.js)]
    Backend[Backend API \n(FastAPI)]
    AI[Gemini 2.5 AI \n(Google)]

    User -->|Type Prompt / Upload Sample| Frontend
    Frontend -->|Send Data (JSON)| Backend
    Backend -->|Construct Prompt Context| AI
    AI -->|Generate Ghostwritten Text| Backend
    Backend -->|Return Draft| Frontend
    Frontend -->|Display Letter| User
```

**Text Workflow:**
`User Input` -> `Frontend` -> `Backend` -> `Gemini AI` -> `Backend` -> `Frontend` -> `User Screen`

---

## 🛠️ Quick Start

You can run the entire application (Backend + Frontend) with one command.

### 1. Simple Run
```bash
python run_app.py
```
*This launches the Backend on port 8000 and Frontend on port 3000.*

---

## 🏗️ Architecture

- **Frontend**: Next.js 16 (React), Tailwind CSS.
- **Backend**: Python 3.11, FastAPI.
- **AI Engine**: Google Gemini 2.5 Flash (Multimodal).

---

## 📦 Deployment (Manual)

- **Frontend**: Host on **Firebase Hosting**.
- **Backend**: Host on **Render.com**.
*(See `deployment_manual.md` for details)*

# 🧠 AI Code Reviewer

A fully local code review tool that combines **static analysis** with a **fine-tuned LLM** to identify Python issues and suggest instant AI-generated fixes — no APIs required!

---

## 🚀 Features

### 🔍 Code Analysis (via AST)

- Detects **unused imports**
- Detects **unused variables**
- Flags **unreachable code**
- Warns about **inefficient or nested loops**
- Measures **cyclomatic complexity** (coming soon)

### 🤖 AI Code Fixes (via TinyLlama or CodeT5)

- Suggests **inline code fixes** using a **local LLM** (TinyLlama or fine-tuned CodeT5)
- Supports **rule-based shortcuts** for common patterns
- **No external API calls** required

### 🖥️ Frontend

- Built with **Next.js 15 + TailwindCSS**
- Upload `.py` file and see:
  - 🔢 Line-level issues
  - 👀 Code preview
  - ✅ AI-suggested fix

### 📄 Report

- Saves **markdown reports** with line-by-line issues and fix suggestions
- Optional: Save individual issue files for GitHub annotations or CI integration

---

## 🧪 How It Works

1. **Upload Python file** via frontend or API
2. **AST Analyzer** parses and collects issues
3. For each issue:
   - Tries **rule-based fix** first
   - Else sends prompt to **local LLM** with line-level context
4. **Fix + context** displayed in UI and saved to report

---

## 🛠️ Tech Stack

| Layer     | Tool                                |
| --------- | ----------------------------------- |
| Backend   | FastAPI                             |
| Frontend  | Next.js (App Router) + Tailwind     |
| AI Model  | TinyLlama / CodeT5 (fine-tuned)     |
| Parser    | Python `ast` module                 |
| Prompting | Custom templates + caching          |
| Reports   | Markdown + optional per-issue files |

---

## 📦 Local Setup

### 1. Install Requirements

```bash
pip install -r requirements.txt
cd ai_code_reviewer_frontend && npm install

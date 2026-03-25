# 🚀 OnboardIQ — AI-Powered Employee Onboarding Platform

> Built by **KONVERGE.AI** | Frontend Dashboard

---

## 📋 Prerequisites

Make sure you have these installed on your machine:

| Tool     | Required Version | Check Command  |
|----------|-----------------|----------------|
| **Node.js** | v18 or above    | `node -v`      |
| **npm**     | v9 or above     | `npm -v`       |

### Installing Node.js (if not installed)

**Windows / Mac:** Download from [https://nodejs.org](https://nodejs.org) (LTS version recommended)

**Ubuntu/Debian:**
```bash
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt-get install -y nodejs
```

---

## ⚡ Quick Start (3 Steps)

### 1. Clone the repository
```bash
git clone <your-repo-url>
cd OnboardingIQ/frontend
```

### 2. Install dependencies
```bash
npm install
```

### 3. Start the development server
```bash
npm run dev
```

The app will be running at: **http://localhost:3000**

---

## 🔐 Login Credentials (Demo)

| Role           | Email                 | Password    |
|----------------|-----------------------|-------------|
| **HR Admin**   | `hr@konverge.ai`      | `admin123`  |
| **Candidate**  | `tejas@konverge.ai`   | `welcome1`  |
| **Candidate**  | `mugdha@konverge.ai`  | `welcome1`  |

- **HR Admin** → Full dashboard: Analytics, Employees, Job Offerings, Workflow, Chat, Settings
- **Candidate** → Personal onboarding checklist with progress tracker

---

## 🛠️ Available Scripts

| Command         | Description                              |
|-----------------|------------------------------------------|
| `npm run dev`   | Start development server (hot-reload)    |
| `npm run build` | Create production build                  |
| `npm run start` | Run production build locally             |
| `npm run lint`  | Run ESLint checks                        |

---

## 📁 Project Structure

```
frontend/
├── src/
│   └── app/
│       ├── page.tsx          # Main application (login + dashboard)
│       ├── layout.tsx        # Root layout with Inter font + SEO meta
│       └── globals.css       # Global styles, scrollbar, animations
├── public/                   # Static assets
├── package.json              # Dependencies
├── tsconfig.json             # TypeScript config
├── next.config.ts            # Next.js configuration
├── postcss.config.mjs        # PostCSS (Tailwind CSS v4)
└── eslint.config.mjs         # Linting rules
```

---

## 🧰 Tech Stack

| Technology       | Purpose                          |
|------------------|----------------------------------|
| **Next.js 16**   | React framework (App Router)     |
| **Tailwind CSS 4** | Utility-first styling          |
| **Framer Motion** | Animations & page transitions   |
| **Lucide React** | Icon library                     |
| **TypeScript**   | Type safety                      |

---

## 🔮 Upcoming Integrations

- **Azure OpenAI (RAG)** — AI Chat Assistant with policy document knowledge base
- **FastAPI Backend** — JWT authentication, candidate CRUD, task management
- **Microsoft Azure AD** — Enterprise SSO login
- **Keka HRMS Sync** — Employee data synchronization

---

## 🐛 Troubleshooting

### "Module not found" error
```bash
rm -rf node_modules package-lock.json
npm install
```

### Port 3000 already in use
```bash
# Find and kill the process
npx kill-port 3000
npm run dev
```

### Styles not loading properly
Make sure you have Tailwind CSS v4 installed:
```bash
npm install tailwindcss@latest @tailwindcss/postcss@latest
```

---

## 👥 Team

- **KONVERGE.AI** — Development Team

---

© 2026 KONVERGE.AI — All rights reserved.

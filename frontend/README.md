# Healthcare Multi-Agent Frontend

Modern React-based frontend for the Healthcare Multi-Agent System with real-time chat and analytics dashboard.

## 🚀 Quick Start

### 1. Install Dependencies
```powershell
npm install
```

### 2. Start Development Server
```powershell
npm run dev
```

The frontend will be available at: **http://localhost:5173**

## 🎯 Running the Complete System

### Terminal 1: Backend
```powershell
cd d:\workspace\healthcare-multi-agent\backend
python run.py
```

### Terminal 2: Frontend
```powershell
cd d:\workspace\healthcare-multi-agent\frontend
npm run dev
```

### Access Points
- 💬 **Chat Interface**: http://localhost:5173
- 📊 **Analytics Dashboard**: http://localhost:5173/dashboard
- 🔧 **Backend API**: http://localhost:8000

## ✨ Features

- **Real-Time Chat**: Beautiful chat UI with multi-agent orchestration
- **Analytics Dashboard**: Live metrics and performance monitoring
- **Agent Indicators**: Visual tracking of active agents
- **HITL Flags**: Automatic flagging for human review
- **Session Management**: Persistent chat sessions
- **Mobile Responsive**: Works on all devices

## 📱 Pages

- **`/`** - Chat interface with quick suggestions
- **`/dashboard`** - Analytics with auto-refresh (30s)

## 🔧 Tech Stack

- React 18 + Vite
- Tailwind CSS
- React Router
- Axios
- Lucide React Icons

## 🎨 Configuration

Environment variables (`.env`):
```
VITE_API_URL=http://localhost:8000
```

## 🎥 Demo Tips

1. **Chat Demo**: Show multi-agent routing with different message types
2. **Dashboard Demo**: Display real-time metrics and HITL flags
3. **Session Demo**: Create new session, show persistence

## 🐛 Troubleshooting

- **"Failed to fetch"**: Ensure backend is running on port 8000
- **No dashboard data**: Run `backend/tests/test_analytics.ps1` to generate test data
- **Port in use**: Use `npm run dev -- --port 5174`

## 📚 Scripts

```powershell
npm run dev        # Development server
npm run build      # Production build
npm run preview    # Preview build
```

---

**Ready for hackathon! 🏆**

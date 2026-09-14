# 🍌 Banana Leaf Disease Detection & Management System

[![FastAPI](https://img.shields.io/badge/FastAPI-0.111.0-009688.svg?style=flat&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Python](https://img.shields.io/badge/Python-3.12-3776AB.svg?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![TensorFlow](https://img.shields.io/badge/TensorFlow-2.16+-FF6F00.svg?style=flat&logo=tensorflow&logoColor=white)](https://www.tensorflow.org/)
[![Flutter](https://img.shields.io/badge/Flutter-3.24+-02569B.svg?style=flat&logo=flutter&logoColor=white)](https://flutter.dev)
[![React](https://img.shields.io/badge/React-18-61DAFB.svg?style=flat&logo=react&logoColor=black)](https://reactjs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0-3178C6.svg?style=flat&logo=typescript&logoColor=white)](https://www.typescriptlang.org/)
[![MySQL](https://img.shields.io/badge/MySQL-8.0-4479A1.svg?style=flat&logo=mysql&logoColor=white)](https://www.mysql.com/)

> **Undergraduate Final Project (Tugas Akhir)**  
> An end-to-end intelligent agricultural diagnosis and farm management ecosystem designed to detect banana leaf diseases from mobile cameras, providing farmers with immediate treatment guidance and administrators with comprehensive analytics and AI model lifecycle management.

---

## 📌 Table of Contents
- [Overview](#-overview)
- [System Architecture](#-system-architecture)
- [Key Features](#-key-features)
  - [1. Mobile Application (Farmer Client)](#1-mobile-application-farmer-client)
  - [2. Web Admin Dashboard](#2-web-admin-dashboard)
  - [3. Backend & AI Pipeline](#3-backend--ai-pipeline)
- [Supported Disease Classes](#-supported-disease-classes)
- [Project Structure](#-project-structure)
- [Getting Started](#-getting-started)
  - [Prerequisites](#prerequisites)
  - [Backend Setup](#backend-setup)
  - [Frontend Setup](#frontend-setup)
  - [Mobile App Setup](#mobile-app-setup)
- [API Overview](#-api-overview)
- [Author & Acknowledgments](#-author--acknowledgments)

---

## 🌿 Overview

Banana cultivation is often severely impacted by foliar diseases such as **Sigatoka**, **Cordana**, and **Panama disease**, causing substantial economic loss for farmers. This project bridges deep learning and practical agriculture:

1. **Farmers** can snap a photo of a banana leaf in their plantation and receive accurate, instant disease diagnosis along with confidence levels and actionable treatment recommendations.
2. **Agricultural Administrators** have access to a centralized web portal to track regional outbreak trends, manage user activity logs, inspect prediction histories, and deploy/hot-swap new neural network models without downtime.

---

## 🏛 System Architecture

```mermaid
graph TD
    subgraph MobileClient ["📱 Mobile Client (Flutter)"]
        F1["Farmer Camera / Gallery"] --> F2["Predict Screen"]
        F2 --> F3["History & Profile Screen"]
    end

    subgraph WebAdmin ["💻 Web Admin (React + Vite)"]
        W1["Dashboard & Analytics"]
        W2["AI Model Management (Hot-Swap)"]
        W3["Predictions & User Audit Logs"]
    end

    subgraph BackendAPI ["⚡ Backend API (FastAPI)"]
        B1["JWT OAuth2 Auth"]
        B2["Predictions Controller"]
        B3["Model Manager Controller"]
        B4["Activity Logger & SSE"]
    end

    subgraph AIPipeline ["🧠 AI Detection Pipeline (TensorFlow/Keras)"]
        M1["Stage 1: Binary Gate Filter (Banana vs Non-Banana)"]
        M2["Stage 2: Multi-Class Disease Classifier"]
        M1 -->|Valid Banana Leaf| M2
        M1 -->|Random / Invalid Image| REJ["Reject with Guidance"]
    end

    subgraph Database ["🗄 Storage & Database"]
        DB[(MySQL 8.0 Database)]
        FS["Static Files (Images & H5 Models)"]
    end

    MobileClient -->|REST API (HTTP/JSON + Multipart)| BackendAPI
    WebAdmin -->|REST API (Bearer Token)| BackendAPI
    BackendAPI --> AIPipeline
    BackendAPI --> DB
    BackendAPI --> FS
```

---

## ✨ Key Features

### 1. Mobile Application (Farmer Client)
- **Instant Photo Diagnosis**: Capture leaf images using the device camera or select from gallery.
- **Smart Image Validation**: Rejects non-banana images automatically using the Stage 1 filter model.
- **Detailed Disease Breakdown**: Displays confidence percentage, severity status, and treatment steps.
- **Offline-Tolerant History**: Sort and filter past diagnostic results by date or condition.
- **Profile Management**: Update farmer personal details and upload custom avatars with automatic fallback.

### 2. Web Admin Dashboard
- **Interactive Overview**: Real-time KPI cards for total predictions, registered farmers, active AI models, and regional trends.
- **AI Model Hot-Swapping**: Upload new `.h5`/`.keras` models and activate/deactivate filter and disease models dynamically in memory without restarting the server.
- **Historical Prediction Explorer**: Paginated audit table with full-size image modal previews and owner details.
- **Audit Logs**: Comprehensive event trail recording IP addresses, browser agents, timestamps, and user actions.
- **Leaf Conditions Encyclopedia**: Manage disease descriptions, reference images, and symptoms.

### 3. Backend & AI Pipeline
- **Dual-Model Inference Pipeline**:
  - **Filter Model**: Input size `150x150`, filters out background clutter and non-banana foliage.
  - **Disease Model**: Input size `224x224`, classifies target diseases.
- **High-Concurrency Async API**: Built with FastAPI and Async SQLAlchemy (`aiomysql`).
- **Secure Authentication**: OAuth2 Password Flow with salted hashing and JWT tokens.
- **Graceful Lifecycle Management**: Auto-loads active models into TensorFlow memory upon server startup.

---

## 🔬 Supported Disease Classes

| No | Condition / Disease | Pathogen / Cause | Description |
|:--:|:--------------------|:-----------------|:------------|
| 1 | **Healthy (Sehat)** | None | Vibrant green leaf without chlorosis or lesions. |
| 2 | **Cordana Leaf Spot** | *Cordana musae* | Oval or diamond-shaped lesions with bright yellow halos. |
| 3 | **Panama Disease** | *Fusarium oxysporum* | Progressive yellowing of older leaves and vascular discoloration. |
| 4 | **Yellow & Black Sigatoka** | *Pseudocercospora spp.* | Dark streaks and necrotic spots reducing photosynthetic area. |

---

## 📂 Project Structure

```text
Final Project/
├── Backend/                       # FastAPI Server & AI Engine
│   ├── app/
│   │   ├── ai/                    # Saved TensorFlow models (.h5)
│   │   ├── database/              # Async SQLAlchemy connection
│   │   ├── models/                # Database ORM models
│   │   ├── routers/               # API routes (predict, models, auth, etc.)
│   │   ├── schemas/               # Pydantic validation schemas
│   │   ├── static/                # Uploaded avatars and leaf photos
│   │   └── utils/                 # TensorFlow preprocessing, image helpers
│   ├── migrations/                # Alembic database migrations
│   ├── main.py                    # Application entry point & lifespan
│   └── requirements.txt           # Python dependencies
│
├── Frontend/                      # Web Admin Monorepo
│   └── vite-monorepo/apps/web/    # React + Vite Admin Portal
│       ├── src/
│       │   ├── api/               # Axios API client modules
│       │   ├── components/        # Layout, sidebar, UI widgets
│       │   ├── pages/             # Dashboard, Models, Users, Predictions
│       │   └── main.tsx           # React bootstrap
│       └── package.json
│
├── Mobile/                        # Flutter Mobile App for Farmers
│   ├── android/                   # Native Android wrapper & Gradle Kotlin DSL
│   ├── lib/
│   │   ├── constants/             # API URLs, color schemes, themes
│   │   ├── models/                # Dart data models
│   │   ├── providers/             # State management (Provider)
│   │   ├── screens/               # Auth, Predict, History, Profile screens
│   │   ├── services/              # Dio HTTP API client & secure storage
│   │   └── widgets/               # Reusable dialogs and UI components
│   └── pubspec.yaml               # Flutter package dependencies
│
├── sync-mobile.sh                 # One-command sync helper from Windows to WSL
└── README.md                      # Project documentation
```

---

## 🚀 Getting Started

### Prerequisites
- **Python** 3.10 – 3.12
- **Node.js** 18+ and **npm**
- **Flutter SDK** 3.24+ and **Android Studio**
- **MySQL** 8.0 Server

---

### Backend Setup

1. **Navigate to the Backend directory:**
   ```bash
   cd Backend
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate   # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables:**
   Create a `.env` file in the `Backend/` root:
   ```env
   DATABASE_URL=mysql+aiomysql://<user>:<password>@localhost:3306/final_project
   ALEMBIC_URL_DB=mysql+pymysql://<user>:<password>@localhost:3306/final_project
   HASH_ALGORITMA=HS256
   SESS_TOKEN=your_secure_random_secret_key_here
   MODEL_URL=app/ai/
   ```

5. **Run database migrations:**
   ```bash
   alembic upgrade head
   ```

6. **Start the FastAPI server:**
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```
   *The interactive Swagger documentation will be available at `http://localhost:8000/docs`.*

---

### Frontend Setup

1. **Navigate to the web application directory:**
   ```bash
   cd Frontend/vite-monorepo/apps/web
   ```

2. **Install Node dependencies:**
   ```bash
   npm install
   ```

3. **Run the Vite development server:**
   ```bash
   npm run dev
   ```
   *Open `http://localhost:5173` in your browser.*

---

### Mobile App Setup

1. **Navigate to the Mobile directory:**
   ```bash
   cd Mobile
   ```

2. **Configure API Base URL:**
   Open `lib/constants/api_constants.dart` and update the `baseUrl` to point to your computer's IP address on your local network:
   ```dart
   static const String baseUrl = 'http://192.168.X.X:8000';
   ```

3. **Get dependencies:**
   ```bash
   flutter pub get
   ```

4. **Run on an attached Android device:**
   ```bash
   flutter run
   ```

---

## 🔌 API Overview

| Method | Endpoint | Description | Access |
|:-------|:---------|:------------|:-------|
| `POST` | `/auth/login` | Authenticate user & issue JWT token | Public |
| `POST` | `/auth/register/` | Register new farmer account | Public |
| `GET` | `/predict/status` | Check AI model readiness in memory | User |
| `POST` | `/predict/add` | Submit leaf photo for disease prediction | User |
| `GET` | `/predict/show` | Retrieve farmer personal prediction history | User |
| `GET` | `/predict/show-all` | Paginated prediction records with filters | Admin |
| `DELETE` | `/predict/delete/{id}` | Remove prediction record and disk image | User / Admin |
| `GET` | `/model/show` | List all uploaded models | Admin |
| `PUT` | `/model/set-status/{id}` | Activate a specific model (hot-swap) | Admin |
| `GET` | `/profile/detail` | Fetch comprehensive user profile | User |
| `PATCH` | `/profile/update` | Update personal profile data | User |
| `PUT` | `/profile/update-image` | Upload and replace profile picture | User |

---

## 👤 Author & Acknowledgments

- **Developer**: Yoga Widiantara ([@widiantara13](https://github.com/widiantara13))
- **Program**: Informatics / Computer Science Undergraduate Degree
- **Project**: Final Project / Bachelor's Thesis (*Tugas Akhir*)

---
*Built with ❤️ for sustainable agriculture and smart farming.*


# Train Booking System

A full-stack train booking and analytics platform built with FastAPI, React, and MySQL. Features real-time analytics, beautiful visualizations, and a responsive dashboard for tracking bookings, revenue, and customer behavior.

<img width="1693" height="1247" alt="Screenshot 2025-12-19 002358" src="https://github.com/user-attachments/assets/cc6351e6-cdd2-4aff-bf6c-3f675d32177f" />

---

## Screenshot

### Analytics Dashboard
*Real-time analytics with interactive charts and dynamic time range filtering*

### Booking Trends
*Daily booking and revenue trends visualization*

### Database Schema


*Complete entity relationship diagram for the train booking system*

---

##  Features

###  Core Features
-  **Real-time Analytics Dashboard** - Interactive charts with Recharts
- **Dynamic Time Filtering** - Switch between 7/30/90 day views
-  **Revenue Tracking** - Monitor total revenue and booking values
-  **Popular Routes Analysis** - Identify most booked train routes
- **Customer Insights** - Track top spenders and booking patterns
-  **Journey Performance** - Analyze most popular train journeys
- **Class Distribution** - Visualize First/Business/Economy bookings

###  Technical Features
-  **RESTful API** with FastAPI and automatic OpenAPI docs
-  **Pandas-Powered Analytics** - Efficient data processing
-  **Single SQL Query Architecture** - Optimized database access
-  **Responsive Design** - Works on desktop, tablet, and mobile
-  **CORS Enabled** - Secure cross-origin requests
-  **SQLAlchemy ORM** - Clean database interactions

---

##  Tech Stack

### Backend
- **FastAPI** - Modern Python web framework
- **SQLAlchemy** - SQL toolkit and ORM
- **Pandas** - Data analysis and manipulation
- **PyMySQL** - MySQL database connector
- **Pydantic** - Data validation
- **Uvicorn** - ASGI server

### Frontend
- **React 18** - UI library
- **Vite** - Build tool and dev server
- **Recharts** - Charting library
- **Axios** - HTTP client
- **Tailwind CSS** - Utility-first CSS

### Database
- **MySQL 8.0+** - Relational database
- **11 Tables** - Normalized schema design

---

## Database Schema

The system uses a normalized relational database with 11 interconnected tables:

### Core Tables
- `schedule` - Train schedules (Weekday, Weekend, Holiday)
- `train_station` - Station information
- `train_journey` - Journey definitions
- `journey_station` - Stops on each journey
- `carriage_class` - First, Business, Economy classes
- `carriage_price` - Pricing by schedule and class
- `journey_carriage` - Carriages available per journey
- `passenger` - Customer information
- `booking` - Booking records
- `booking_status` - Active, Cancelled, Completed

---

##  Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+
- MySQL 8.0+
- Git

###  Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/train-booking-system.git
cd train-booking-system
```

### Setup MySQL Database

```bash
# Open MySQL Workbench and run:
CREATE DATABASE train_booking;

# Run the schema creation script
# Location: database/schema.sql

# Run the dummy data generator (optional)
# Location: database/generate_90_days_dummy_data.sql
```

### Setup Backend

```bash
cd backend
# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your MySQL credentials

# Start the server
uvicorn app.main:app --reload
```

Backend running at: http://localhost:8000  
API Docs at: http://localhost:8000/docs

### Setup Frontend

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```
 Frontend running at: http://localhost:3000

---

## Project Structure

```
train-booking-system/
├── backend/                    # FastAPI Backend
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py            # FastAPI application
│   │   ├── database.py        # Database connection
│   │   ├── models.py          # SQLAlchemy models
│   │   ├── schemas.py         # Pydantic schemas
│   │   └── routers/
│   │       └── analytics.py   # Analytics endpoints
│   ├── requirements.txt
│   └── .env.example
│
├── frontend/                   # React Frontend
│   ├── src/
│   │   ├── pages/
│   │   │   └── AnalyticsDashboard.jsx
│   │   ├── services/
│   │   │   └── api.js         # API client
│   │   ├── App.jsx
│   │   ├── main.jsx
│   │   └── index.css
│   ├── index.html
│   ├── package.json
│   └── vite.config.js
│
├── database/                   # Database Scripts
│   ├── schema.sql
│   └── generate_90_days_dummy_data.sql
│
├── docs/                       # Documentation & Images
│   └── images/
│       ├── dashboard-screenshot.png
│       ├── database-erd.png
│       └── booking-trends.png
│
├── .gitignore
└── README.md
```

---

##  API Endpoints

### Analytics Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/analytics/dashboard?days={n}` | Complete dashboard data |
| GET | `/api/analytics/bookings/stats` | Booking statistics |
| GET | `/api/analytics/revenue/stats` | Revenue analytics |
| GET | `/api/analytics/popular-routes` | Top routes by bookings |
| GET | `/api/analytics/daily-trends?days={n}` | Daily booking trends |
| GET | `/api/analytics/class-distribution` | Class breakdown |
| GET | `/api/analytics/passengers/top-spenders?limit={n}` | Top spending customers |
| GET | `/api/analytics/journeys/performance?limit={n}` | Journey performance metrics |

# PrepWise 🎓

PrepWise is an intelligent, adaptive exam preparation platform designed to help students master subjects through personalized quizzes and detailed analytics. Built with a modern tech stack, it features a dynamic learning engine that adjusts request difficulty based on performance and provides AI-powered explanations for mistakes.

## 🚀 Key Features

- **Adaptive Learning Engine**: Automatically adjusts quiz difficulty (Easy/Medium/Hard) based on your performance history.
- **Smart Analytics Dashboard**: Visualizes progress with charts, tracking strong and weak topic areas.
- **AI Tutor Integration**: integrated with **Google Gemini AI** to provide instant, conversational explanations for incorrect answers.
- **Secure Authentication**: Robust user management using **Supabase Auth** (Email/Password & OTP).
- **Teacher Console**: Dedicated interface for educators to manage question banks and view student insights.
- **Daily Goals**: Tracks daily quiz attempts to maintain study momentum.
- **Responsive Design**: Modern UI with dark mode aesthetics and mobile compatibility.

## 🛠️ Tech Stack

- **Backend**: Python, Flask
- **Database**: PostgreSQL (via Supabase)
- **Frontend**: HTML5, CSS3, Vanilla JavaScript, Jinja2 Templates
- **Authentication**: Supabase Auth (JWT/Session Management)
- **AI/ML**: Google Gemini API (Generative AI)
- **Visualization**: Matplotlib (Server-side plotting), Chart.js (implied context)

## 📂 Project Structure

```bash
PrepWise/
├── backend/
│   ├── app.py                  # Main Flask application entry point
│   ├── models.py               # Database models (User, HistoryStack)
│   ├── analytics_engine.py     # Logic for performance analysis
│   ├── requirements.txt        # Python dependencies
│   ├── static/                 # CSS, JavaScript, Images
│   └── templates/              # HTML Templates (Jinja2)
├── .env                        # Environment variables (Sensitive)
├── README.md                   # Project documentation
└── ...
```

## ⚡ Getting Started

### Prerequisites

- Python 3.8+
- PostgreSQL database (or Supabase project)
- Google Gemini API Key

### Installation

1.  **Clone the repository**
    ```bash
    git clone https://github.com/yourusername/PrepWise.git
    cd PrepWise
    ```

2.  **Set up a Virtual Environment**
    ```bash
    # Windows
    python -m venv venv
    .\venv\Scripts\activate

    # macOS/Linux
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install Dependencies**
    ```bash
    pip install -r backend/requirements.txt
    ```

4.  **Configure Environment Variables**
    Create a `.env` file in the `backend/` directory (or root, depending on your setup) with the following keys:
    ```ini
    DATABASE_URL=postgresql://user:password@host:port/dbname
    SECRET_KEY=your_flask_secret_key
    SUPABASE_URL=your_supabase_project_url
    SUPABASE_KEY=your_supabase_anon_key
    GEMINI_API_KEY=your_google_gemini_api_key
    ```
    *Note: Ensure your `DATABASE_URL` starts with `postgresql://`. If using Supabase transaction pooler, it might be `postgres://`, the app handles the fix.*

5.  **Initialize the Database**
    Run the initialization scripts to set up tables and seed data (if applicable):
    ```bash
    python backend/init_db.py
    # python backend/seed_db.py (Optional: for dummy data)
    ```

6.  **Run the Application**
    ```bash
    cd backend
    python app.py
    ```
    The server will start at `http://127.0.0.1:5000/`.

## 🤝 Contributing

Contributions are welcome! Please fork the repository and submit a pull request for any enhancements or bug fixes.

## 📄 License

This project is licensed under the generic MIT License (Modify as needed).


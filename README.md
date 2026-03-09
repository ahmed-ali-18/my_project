# Municipal Complaint Analysis and Monitoring System

A Flask web app for citizens to report municipal issues and for admins to monitor, analyze, and resolve complaints with AI-driven insights.

## Quick start

### 1. Install dependencies

```bash
cd "c:\Users\matee\OneDrive\Documents\Desktop\my_project"
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Train the AI classifier (recommended)

This uses the sample data in `data/complaints_training.csv` and saves the model to `ai/model.joblib`. The app will then use this model to auto-categorize new complaints instead of the rule-based fallback.

```bash
python -m ai.train_model
```

The script will:

- Download required NLTK data (punkt, stopwords, wordnet) if needed
- Load and preprocess the training CSV
- Train a TF-IDF + Logistic Regression pipeline
- Print a classification report and save the model to `ai/model.joblib`

### 3. Run the app

```bash
set FLASK_ENV=development
python app.py
```

Open **http://127.0.0.1:5000** in your browser.

### 4. Create an admin user (one-time)

In a new terminal, with the same venv activated:

```bash
python -c "
from app import create_app
from models import db, User
app = create_app()
with app.app_context():
    admin = User(name='Admin', email='admin@example.com', role='admin')
    admin.set_password('admin123')
    db.session.add(admin)
    db.session.commit()
    print('Admin created: admin@example.com / admin123')
"
```

Then log in at **/auth/login** with `admin@example.com` / `admin123`.

## Training data

- **Sample file:** `data/complaints_training.csv`  
  Columns: `title`, `description`, `category`.

- **Categories:** Road Issues, Garbage Management, Water Supply, Street Lighting, Drainage Issues.

You can add more rows to the CSV and run `python -m ai.train_model` again to improve the classifier.

## Project structure

- `app.py` – Flask app factory and setup  
- `config.py` – Configuration (dev/prod, DB, uploads, delay threshold)  
- `models.py` – User and Complaint models  
- `routes/` – Auth, citizen complaints, admin and analytics  
- `ai/` – Text preprocessing, classifier, training script  
- `data/` – Training CSV for the classifier  
- `templates/` – Jinja2 HTML templates  
- `static/` – CSS, JS, uploads  

NutriGenix — AI-Powered Nutrition & Diet Platform

An all-in-one, AI-powered diet and nutrition web app built for **Pakistani eating habits**. NutriGenix helps users track calories and water, calculate BMI/TDEE, generate personalized 7-day diet plans, and get real-time dietary advice from an AI chatbot.

> Developed as a Computer Architecture project (BSCS, 6th Semester) at the University of South Asia, Lahore.

---

 Problem

Most popular nutrition apps (MyFitnessPal, Cronometer, HealthifyMe) focus on Western diets and have little or no data for Pakistani foods like Biryani, Roti, Daal, or Karahi. Pakistan also has a very high rate of diabetes, obesity, hypertension, and PCOS. NutriGenix fills this gap with culturally relevant, free-to-use nutrition tools.

Features

Authentication – register, login, logout (Django auth + signals)
Dashboard – calories vs. goal, water intake, BMI, TDEE, weekly calorie chart, macro doughnut chart (Chart.js)
 Food Log– search 55+ Pakistani foods, log meals (Breakfast / Lunch / Dinner / Snack), delete entries
BMI & TDEE Calculator – uses the Mifflin-St Jeor equation, with goal-based calorie adjustment
Water Tracker – circular progress indicator, quick-add buttons, daily log
AI Chatbot – powered by Groq API (Llama 3.1-8B-Instant) with a rule-based fallback
7-Day Diet Plan Generator – personalized plan using a greedy calorie allocation algorithm
Health Condition Filters – Diabetes, PCOS, Hypertension, Thyroid
Profile Management – measurements, activity level, goals, water goal
Premium Subscription (Demo) – freemium model with demo payment gateway

 Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.13, Django 5.0 |
| Frontend | HTML5, CSS3, Bootstrap 5, JavaScript |
| AI Chatbot | Groq API — Llama 3.1-8B-Instant |
| Charts | Chart.js |
| Database | SQLite (development) |
| Version Control | Git + GitHub |

## 🚀 Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/hafizawajeeha123-crypto/nutrigenix.git
cd nutrigenix
```

### 2. Create and activate a virtual environment

```bash
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # macOS / Linux
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up environment variables

Create a `.env` file in the project root:

```env
GROQ_API_KEY=your_groq_api_key_here
SECRET_KEY=your_django_secret_key_here
DEBUG=True
```

You can get a free Groq API key from [console.groq.com](https://console.groq.com).

### 5. Set up the database

```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

### 6. Import the food database

```bash
python manage.py import_foods
```

### 7. Run the server

```bash
python manage.py runserver
```

Open **http://127.0.0.1:8000** in your browser.

Algorithms Used
Algorithm  Purpose  Complexity 
|---|---|---|
| Mifflin-St Jeor equation | BMR calculation | O(1) |
| BMI formula (WHO) | BMI and category | O(1) |
| Activity multiplier | TDEE calculation | O(1) |
| Calorie goal adjustment | Lose (−500) / Maintain / Gain (+300) | O(1) |
| Greedy calorie allocation | 7-day diet plan (25% / 35% / 30% / 10% split) | O(n × m) |
| Q-object search | Multi-field food search (max 20 results) | O(n) |
| Django signals | Auto-create profiles, update water summaries | — |

Database Models

`UserProfile` · `FoodItem` · `MealLog` · `DietPlan` · `DietPlanMeal` · `WaterLog` · `WaterDailySummary` · `ChatSession` · `ChatMessage`

Future Work

- Mobile app
- Wearable device integration
- Micronutrient data in the food database
- Real payment integration (Easypaisa, JazzCash)

Supervised by **Sir Tauseef**, Department of Computer Science, University of South Asia.

Disclaimer

NutriGenix provides general nutrition information and is not a substitute for professional medical advice. Consult a doctor or registered dietitian for health conditions.

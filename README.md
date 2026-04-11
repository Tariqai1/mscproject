# Advanced Sarcasm-Aware Sentiment Analysis System for E-commerce Reviews

A comprehensive machine learning system that analyzes sentiment and detects sarcasm in e-commerce reviews using hybrid transformer models, traditional ML baselines, and deep learning approaches.

## 📋 Project Overview

This system is designed as an MSc IT Advanced Project that addresses the challenge of accurately analyzing sentiment in sarcastic e-commerce reviews. Traditional sentiment analysis models often fail on sarcastic content, so this system uses a two-stage hybrid architecture:

**Stage 1:** BERT-based sarcasm detection  
**Stage 2A:** Logistic Regression for non-sarcastic reviews  
**Stage 2B:** RoBERTa for sarcastic reviews  

### Key Features

- 🎯 **Dual-Task Learning:** Simultaneously predicts sentiment (positive/negative/neutral) and sarcasm (yes/no)
- 🤖 **Multiple Models:** Implementation of 5 different architectures (LR, SVM, LSTM, BERT, RoBERTa)
- 📊 **Hybrid Two-Stage Architecture:** Routes predictions through specialized models based on sarcasm detection
- 🔄 **Smart Fallback:** Rule-based classifier ensures graceful degradation if models unavailable
- 📈 **Interactive Dashboard:** React frontend with real-time predictions, history tracking, and analytics
- ✨ **Advanced Preprocessing:** Sarcasm-aware feature extraction (contradiction detection, emoji analysis, keyword detection)
- 📦 **Batch Processing:** Process multiple reviews at once and export results as CSV

## 🛠️ Tech Stack

### Backend
- **Framework:** FastAPI 0.115.0+
- **Database:** SQLite with SQLAlchemy ORM
- **Server:** Uvicorn ASGI Server

### Machine Learning
- **Data Processing:** Pandas, NumPy
- **Traditional ML:** scikit-learn (Logistic Regression, SVM)
- **Deep Learning:** TensorFlow/Keras (LSTM)
- **Transformers:** PyTorch + HuggingFace (BERT, RoBERTa)
- **NLP:** NLTK, spaCy, Emoji

### Frontend
- **Framework:** React 19.2.4
- **Routing:** React Router v6
- **HTTP Client:** Axios 1.6.2+
- **Charts:** Recharts 2.10.3+
- **Styling:** CSS3 with Gradients & Flexbox

## 📁 Project Structure

```
├── backend/                          # FastAPI Application
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                  # FastAPI app & endpoints
│   │   ├── models.py                # SQLAlchemy ORM models
│   │   └── database.py              # Database configuration
│   ├── routes/                      # API route handlers
│   ├── services/
│   │   ├── __init__.py
│   │   └── prediction_service.py    # Model inference service
│   ├── run.bat                      # Windows startup script
│   └── requirements.txt             # Backend dependencies
│
├── frontend/                        # React Application
│   ├── public/
│   │   ├── index.html
│   │   ├── manifest.json
│   │   └── robots.txt
│   ├── src/
│   │   ├── App.js                  # Main app with routing
│   │   ├── App.css                 # Main styles
│   │   ├── index.js
│   │   ├── components/
│   │   │   ├── Header.js           # Navigation header
│   │   │   ├── PredictionForm.js   # Review input form
│   │   │   ├── ResultCard.js       # Prediction results display
│   │   │   ├── LoadingSpinner.js   # Loading indicator
│   │   │   └── ErrorAlert.js       # Error messages
│   │   ├── pages/
│   │   │   ├── HomePage.js         # Main prediction interface
│   │   │   ├── HistoryPage.js      # View past predictions
│   │   │   ├── AnalyticsPage.js    # Statistics & charts
│   │   │   └── BatchPredictPage.js # Bulk predictions
│   │   ├── utils/
│   │   │   └── api.js              # Axios API client
│   │   └── styles/
│   │       ├── Header.css
│   │       ├── PredictionForm.css
│   │       ├── ResultCard.css
│   │       ├── LoadingSpinner.css
│   │       ├── ErrorAlert.css
│   │       └── pages/
│   │           ├── HomePage.css
│   │           ├── HistoryPage.css
│   │           ├── AnalyticsPage.css
│   │           └── BatchPredictPage.css
│   ├── package.json
│   ├── start.bat                   # Windows startup script
│   └── README.md
│
├── ml_models/                       # Machine Learning Models
│   ├── data_generation.py           # Synthetic dataset generator
│   ├── preprocessing.py             # Text preprocessing pipeline
│   ├── model_lr_svm.py              # Logistic Regression & SVM
│   ├── model_lstm.py                # LSTM neural network
│   ├── model_bert.py                # BERT transformer model
│   ├── model_roberta.py             # RoBERTa transformer model
│   ├── model_hybrid.py              # Two-stage hybrid orchestration
│   ├── evaluation.py                # Model comparison framework
│   ├── trained_models/              # Saved model weights
│   ├── notebooks/                   # Jupyter notebooks
│   └── requirements.txt
│
├── data/
│   ├── raw/
│   │   └── reviews.csv             # Generated synthetic reviews
│   └── processed/
│       ├── train.csv               # Training split
│       ├── test.csv                # Test split
│       ├── train_preprocessed.csv  # Preprocessed training data
│       └── test_preprocessed.csv   # Preprocessed test data
│
├── docs/
│   ├── API_REFERENCE.md            # Detailed API documentation
│   └── SETUP_GUIDE.md              # Step-by-step setup guide
│
├── tests/                           # Unit & integration tests
│
├── README.md                        # This file
└── requirements.txt                 # Root dependencies
```

## 🚀 Installation & Setup

### Prerequisites

- **Python 3.8+** - [Download](https://www.python.org/)
- **Node.js 14+** - [Download](https://nodejs.org/)
- **pip** (comes with Python)
- **npm** (comes with Node.js)

### Step 1: Clone or Download the Project

```bash
cd c:\Users\Hp\sarcasm-sentiment-analysis
```

### Step 2: Set Up Python Environment

Create a virtual environment (recommended):

```bash
# Using venv
python -m venv venv
venv\Scripts\activate

# Or using conda
conda create -n sarcasm-analysis python=3.11
conda activate sarcasm-analysis
```

### Step 3: Install Backend Dependencies

```bash
# Navigate to backend directory
cd backend

# Install required packages
pip install -r requirements.txt
```

**Note:** First-time installation of PyTorch/TensorFlow may take 5-15 minutes. This is normal as these are large packages.

### Step 4: Generate Dataset & Train Models (Optional)

From the `ml_models` directory:

```bash
# Generate synthetic dataset
python data_generation.py

# Preprocess the data
python preprocessing.py

# Train traditional ML models (LR + SVM) - ~2 minutes
python model_lr_svm.py

# Train LSTM model - ~5 minutes (GPU: ~1 minute)
python model_lstm.py

# Train BERT model - ~15 minutes (GPU: ~3 minutes)
python model_bert.py

# Train RoBERTa model - ~15 minutes (GPU: ~3 minutes)
python model_roberta.py

# Evaluate all models
python evaluation.py
```

**Tip:** Training is optional. The system includes a fallback rule-based classifier that works without pre-trained models.

## 🎯 Running the Application

### Option A: Using Windows Batch Scripts (Easiest)

#### Backend (API Server)

1. Open Command Prompt
2. Navigate to the `backend` folder
3. Double-click `run.bat` or run:
   ```bash
   run.bat
   ```
4. You'll see:
   ```
   Starting FastAPI server...
   
   API Documentation: http://localhost:8000/docs
   Uvicorn running on http://0.0.0.0:8000
   ```

#### Frontend (Web Interface)

1. Open a new Command Prompt
2. Navigate to the `frontend` folder
3. Double-click `start.bat` or run:
   ```bash
   start.bat
   ```
4. Your browser will open at `http://localhost:3000`

---

### Option B: Manual Running

#### Backend

```bash
cd backend
python -m uvicorn app.main:app --reload
# Server runs on http://localhost:8000
```

#### Frontend

```bash
cd frontend
npm install  # First time only
npm start
# Opens http://localhost:3000 in your browser
```

---

## 📱 Using the Application

### Home Page
- **Review Input:** Enter an e-commerce review (max 5000 characters)
- **Instant Prediction:** Get sentiment (positive/negative/neutral) and sarcasm detection
- **Confidence Scores:** Visual progress bars showing model confidence
- **User Feedback:** Mark predictions as correct/incorrect to improve the system

### History Page
- View all past predictions
- Filter results by limit (10, 25, 50, or 100)
- See timestamp and prediction details

### Analytics Page
- View system-wide statistics
- Charts showing sentiment distribution
- Sarcasm detection breakdown
- Key insights and performance metrics
- Refresh button to reload latest data

### Batch Predict Page
- Paste multiple reviews (one per line, max 100)
- Bulk process all reviews
- Download results as CSV
- View statistics for batch processing

---

## 🔌 API Endpoints

### Base URL
```
http://localhost:8000
```

### Endpoints

#### 1. **Health Check**
```
GET /api/health
```
Returns: `{ "status": "ok", "models_loaded": true }`

#### 2. **Single Prediction**
```
POST /api/predict
Content-Type: application/json

{
  "text": "This product is absolutely amazing... said no one ever!"
}

Response:
{
  "id": "uuid-string",
  "text": "This product is absolutely amazing... said no one ever!",
  "sentiment": "negative",
  "sentiment_confidence": 0.92,
  "sarcasm": true,
  "sarcasm_confidence": 0.87,
  "confidence": 0.89,
  "model_used": "hybrid_two_stage",
  "explanation": "Detected sarcasm. Route to RoBERTa specialist.",
  "created_at": "2024-01-15T10:30:45.123Z"
}
```

#### 3. **Batch Predictions**
```
POST /api/batch-predict
Content-Type: application/json

{
  "texts": [
    "Great product!",
    "Absolutely terrible, just perfect!",
    "Average quality"
  ]
}

Response:
{
  "count": 3,
  "predictions": [...]
}
```

#### 4. **Prediction History**
```
GET /api/history?limit=50
```

#### 5. **Statistics**
```
GET /api/stats
```

#### 6. **Submit Feedback**
```
POST /api/feedback
```

For detailed API documentation with live testing, visit:
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

---

## 🧪 Testing

Test cases:

1. **Positive Sentiment:**
   - "This product exceeded my expectations! Absolutely love it!"
   - Expected: Positive, low sarcasm

2. **Sarcasm Detection:**
   - "Oh wow, another amazing purchase that fell apart!"
   - Expected: Negative, high sarcasm

3. **Neutral Sentiment:**
   - "The product has good and bad points"
   - Expected: Neutral, low sarcasm

---

## 🐛 Troubleshooting

### Backend won't start
- Check Python: `python --version`
- Check dependencies: `pip install -r requirements.txt`
- Check port 8000: Open http://localhost:8000

### Frontend won't start
- Check Node.js: `node --version`
- Clear npm cache: `npm cache clean --force`
- Reinstall: `delete node_modules && npm install`

### Models not loading
- Check files in `ml_models/trained_models/`
- System uses fallback classifier if models missing

---

## 📚 Documentation

- **[API Reference](docs/API_REFERENCE.md)** - Detailed endpoints
- **[Setup Guide](docs/SETUP_GUIDE.md)** - Step-by-step installation

---

## 🎓 Project for MSc IT

Demonstrates:

✅ Advanced ML (transformers, ensemble methods)  
✅ Full-stack development (Python + React)  
✅ Database design (SQLAlchemy ORM)  
✅ REST API design (FastAPI)  
✅ NLP & sarcasm detection  
✅ Modern UI/UX

---

## 📄 License

Educational use only.

---

**Status:** ✅ Ready for deployment

**Version:** 1.0.0

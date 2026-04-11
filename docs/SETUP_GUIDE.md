# Setup Guide - Step by Step Installation

Complete guide to set up and run the Sarcasm-Aware Sentiment Analysis System.

---

## 📋 Prerequisites

Before starting, ensure you have:

- **Windows 10/11** (or Mac/Linux)
- **Python 3.8+** installed
- **Node.js 14+** installed
- **Internet connection** for package downloads
- **At least 5GB** free disk space

### Check Prerequisites

**Check Python:**
```bash
python --version
```
Should show: `Python 3.x.x`

**Check Node.js:**
```bash
node --version
```
Should show: `v14.x.x` or higher

**Check npm:**
```bash
npm --version
```
Should show: `6.x.x` or higher

---

## 🚀 Installation Steps

### Step 1: Download the Project

Option A: If you have Git:
```bash
git clone <repository-url>
cd sarcasm-sentiment-analysis
```

Option B: If you have a ZIP file:
1. Download the ZIP file
2. Right-click → Extract All
3. Open the extracted folder in Command Prompt

### Step 2: Create Python Virtual Environment

Open Command Prompt and navigate to the project folder:

```bash
cd c:\path\to\sarcasm-sentiment-analysis
```

Create a virtual environment:

```bash
# Using Python venv
python -m venv venv

# Activate the virtual environment
venv\Scripts\activate
```

You should see `(venv)` at the beginning of your command prompt line.

---

### Step 3: Install Backend Dependencies

Navigate to the backend folder:

```bash
cd backend
```

Install all required packages:

```bash
pip install -r requirements.txt
```

**⏱️ Wait Time:** 3-10 minutes (depends on internet speed and computer specs)

**What's being installed:**
- FastAPI - Web framework
- Uvicorn - Server
- SQLAlchemy - Database ORM
- Scikit-learn - Machine Learning
- TensorFlow/PyTorch - Deep Learning
- HuggingFace Transformers - BERT/RoBERTa
- NLTK, spaCy - NLP tools
- And more...

**If installation hangs:**
- It's normal for PyTorch/TensorFlow (they're large)
- Don't close the terminal
- Wait 5-10 minutes
- If it fails, try: `pip install --upgrade pip setuptools wheel`

### Step 4: Install Frontend Dependencies

Open a new Command Prompt window (keep the first one open).

Navigate to the frontend folder:

```bash
cd c:\path\to\sarcasm-sentiment-analysis\frontend
```

Install npm packages:

```bash
npm install
```

**⏱️ Wait Time:** 2-5 minutes

---

### Step 5: Generate Dataset (Optional)

If you want to train models with real data, generate a synthetic dataset.

Navigate to ml_models:

```bash
cd c:\path\to\sarcasm-sentiment-analysis\ml_models
pip install -r requirements.txt
```

Generate dataset:

```bash
python data_generation.py
```

Output files created:
- `data/raw/reviews.csv` - Raw reviews
- `data/processed/train.csv` - Training data
- `data/processed/test.csv` - Test data

Preprocess the data:

```bash
python preprocessing.py
```

Output files created:
- `data/processed/train_preprocessed.csv`
- `data/processed/test_preprocessed.csv`

---

### Step 6: Train Models (Optional)

Training models is optional. The system includes a fallback classifier.

But if you want to train for better accuracy:

```bash
# Terminal 1: Stay in ml_models folder
cd c:\path\to\sarcasm-sentiment-analysis\ml_models

# Train LR + SVM (fastest) - ~2 minutes
python model_lr_svm.py

# Train LSTM (medium) - ~5 minutes
python model_lstm.py

# Train BERT (slower) - ~15 minutes
python model_bert.py

# Train RoBERTa (slower) - ~15 minutes
python model_roberta.py
```

Trained models saved in `ml_models/trained_models/`

---

## ▶️ Running the Application

### Method 1: Using Batch Scripts (Easiest for Windows)

**Start Backend:**

1. Open Command Prompt
2. Navigate to `backend` folder
3. Double-click `run.bat`
4. You should see:
   ```
   Starting FastAPI server...
   API Documentation: http://localhost:8000/docs
   ```

**Start Frontend:**

1. Open a NEW Command Prompt
2. Navigate to `frontend` folder
3. Double-click `start.bat`
4. Wait a few seconds...
5. Your browser opens automatically at `http://localhost:3000`

---

### Method 2: Manual Running

**Terminal 1 - Backend:**

```bash
cd c:\path\to\sarcasm-sentiment-analysis\backend
python -m uvicorn app.main:app --reload
```

Wait until you see:
```
Uvicorn running on http://127.0.0.1:8000
```

**Terminal 2 - Frontend:**

```bash
cd c:\path\to\sarcasm-sentiment-analysis\frontend
npm start
```

Your browser should open at `http://localhost:3000`

---

## ✅ Verification

### Check if Frontend is Running

1. Open browser
2. Go to: `http://localhost:3000`
3. You should see the application UI

### Check if Backend is Running

1. Open browser
2. Go to: `http://localhost:8000/docs`
3. You should see the Swagger API documentation

### Test Single Prediction

1. Go to Home page (http://localhost:3000)
2. Enter a review: "Great product!"
3. Click "Get Prediction"
4. You should see results instantly

---

## 🎯 First-Time Usage

### Step 1: Go to Home Page

- URL: `http://localhost:3000`
- You should see the input form

### Step 2: Enter a Review

Example reviews to test:

**Positive (Non-Sarcastic):**
```
This product is amazing! Great quality and fast delivery.
```

**Negative (Non-Sarcastic):**
```
Terrible product. Broke after one day. Waste of money.
```

**Sarcastic Positive:**
```
Oh wow, what a fantastic experience! The product fell apart immediately, just perfect!
```

**Sarcastic Negative:**
```
Yeah right, this is the best product ever. Sure, it works perfectly. Not!
```

### Step 3: View Results

- **Sentiment:** Positive, Negative, or Neutral
- **Sarcasm:** Yes or No
- **Confidence:** 0-100%
- **Model Used:** Which model made the prediction

### Step 4: Provide Feedback

- Click "✅ Correct" if the prediction is right
- Click "❌ Incorrect" if it made a mistake
- This helps improve the system

---

## 📊 Using Other Pages

### History Page
1. Click "History" in the header
2. View all your past predictions
3. Filter by limit (10, 25, 50, or 100)

### Analytics Page
1. Click "Analytics" in the header
2. See statistics and charts
3. View sentiment distribution
4. Check sarcasm detection rate
5. Click "Refresh" for latest data

### Batch Predict Page
1. Click "Batch Predict" in the header
2. Paste multiple reviews (one per line)
3. Click "Process Batch"
4. Download results as CSV
5. View summary statistics

---

## 🐛 Troubleshooting

### Issue: "Backend not responding"

**Solution:**
```bash
# Check if backend is running
netstat -an | findstr 8000

# If not running, start it
cd backend
python -m uvicorn app.main:app --reload
```

### Issue: "Module not found" error

**Solution:**
```bash
# Make sure you're in the right directory
cd backend

# Reinstall packages
pip install -r requirements.txt

# Try again
python -m uvicorn app.main:app --reload
```

### Issue: "Port 8000 already in use"

**Solution:**
```bash
# Kill the process using port 8000
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Or change the port in command:
python -m uvicorn app.main:app --port 8001 --reload
```

### Issue: "Port 3000 already in use"

**Solution:**
1. Edit `frontend/package.json`
2. Change `"PORT=3000"` to `"PORT=3001"`
3. Save and restart

### Issue: "npm command not found"

**Solution:**
1. Reinstall Node.js from https://nodejs.org/
2. Restart Command Prompt
3. Try: `npm --version`

### Issue: "Python command not found"

**Solution:**
1. Make sure Python is installed
2. Add Python to PATH (installation option)
3. Use `python3` instead of `python`
4. Try: `python --version`

---

## 📦 Project Structure After Setup

```
sarcasm-sentiment-analysis/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py         ✅ FastAPI app
│   │   ├── models.py       ✅ Database models
│   │   ├── database.py     ✅ DB config
│   ├── services/
│   │   └── prediction_service.py  ✅ Model loading
│   ├── database.db         📁 SQLite database (created on first run)
│   ├── run.bat             ✅ Startup script
│   └── requirements.txt    ✅
│
├── frontend/
│   ├── src/
│   │   ├── components/     ✅ React components
│   │   ├── pages/          ✅ React pages
│   │   ├── styles/         ✅ CSS files
│   │   ├── App.js          ✅ Main app
│   │   └── index.js        ✅
│   ├── node_modules/       📁 Installed packages
│   ├── start.bat           ✅ Startup script
│   └── package.json        ✅
│
├── ml_models/
│   ├── data_generation.py  ✅ Data generator
│   ├── preprocessing.py    ✅ Preprocessing
│   ├── model_*.py          ✅ Model files
│   ├── evaluation.py       ✅ Evaluation
│   ├── trained_models/     📁 Saved models (optional)
│   └── requirements.txt    ✅
│
├── data/
│   ├── raw/
│   │   └── reviews.csv       📁 Generated/raw data
│   └── processed/
│       ├── train.csv         📁 Processed data
│       └── test.csv          📁 
│
├── docs/
│   ├── API_REFERENCE.md    ✅ API docs
│   └── SETUP_GUIDE.md      ✅ This file
│
├── README.md               ✅ Main documentation
└── venv/                   📁 Python environment
```

---

## 🔗 Important URLs

| Service | URL | Purpose |
|---------|-----|---------|
| Frontend | http://localhost:3000 | Web Interface |
| Backend | http://localhost:8000 | API Server |
| API Docs | http://localhost:8000/docs | Swagger UI |
| API Docs | http://localhost:8000/redoc | ReDoc |
| Health Check | http://localhost:8000/api/health | Server Status |

---

## 📝 Next Steps

1. **Use the application:**
   - Go to http://localhost:3000
   - Enter reviews and get predictions
   - Explore different pages

2. **Train models (optional):**
   - Run model training scripts
   - Models will be saved automatically

3. **Customize:**
   - Change colors in CSS files
   - Add more features in React
   - Modify model hyperparameters

4. **Deploy (optional):**
   - Backend: Render, Railway, Heroku
   - Frontend: Vercel, Netlify, GitHub Pages
   - Database: PostgreSQL, MongoDB

---

## 🆘 Need Help?

1. **Check Status:**
   - Backend health: http://localhost:8000/api/health
   - API docs: http://localhost:8000/docs

2. **Check Logs:**
   - Backend logs in terminal
   - Frontend logs in browser console (F12)

3. **Restart Everything:**
   ```bash
   # Close all terminals
   # Close browser tab
   # Start fresh from step 1
   ```

4. **Clear Cache:**
   ```bash
   # Backend
   cd backend
   rm database.db
   
   # Frontend
   # Close browser
   # Clear cache: Ctrl+Shift+Delete
   ```

---

## 📚 Documentation Links

- [README.md](../README.md) - Project overview
- [API_REFERENCE.md](API_REFERENCE.md) - Detailed API docs
- [FastAPI Docs](https://fastapi.tiangolo.com/) - FastAPI documentation
- [React Docs](https://react.dev/) - React documentation
- [Hugging Face](https://huggingface.co/) - Transformer models

---

**Setup Complete! You're ready to use the application.** 🎉

**Need to stop the application?**
- Backend: Press Ctrl+C in the terminal
- Frontend: Press Ctrl+C in the terminal

**Want to restart?**
- Just run the startup scripts again
- Same process as starting

---

**Last Updated:** 2024
**Version:** 1.0.0
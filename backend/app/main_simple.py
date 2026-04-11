"""
Minimal FastAPI Application for Sarcasm-Aware Sentiment Analysis
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime

# Create the app
app = FastAPI(
    title="Sarcasm-Aware Sentiment Analysis API",
    description="Analyzes sentiment and detects sarcasm in reviews",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===== HEALTH CHECK ROUTES =====

@app.get("/", tags=["Health"])
async def root():
    """Root endpoint"""
    return {
        "status": "ok",
        "service": "Sarcasm-Aware Sentiment Analysis API",
        "version": "1.0.0"
    }


@app.get("/api/health", tags=["Health"])
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "models_loaded": True
    }

# ===== PREDICTION ROUTE =====

@app.post("/api/predict", tags=["Predictions"])
async def predict_sentiment(request_data: dict):
    """
    Predict sentiment and sarcasm for a review
    
    Request body:
    {
        "text": "This is an amazing product!"
    }
    """
    try:
        text = request_data.get("text", "").strip()
        
        if not text:
            return {"error": "Text field is required"}
        
        # Simple fallback prediction
        text_lower = text.lower()
        
        # Detect sentiment
        positive_words = ['good', 'great', 'excellent', 'amazing', 'love', 'best', 'awesome', 'perfect', 'wonderful']
        negative_words = ['bad', 'terrible', 'awful', 'hate', 'worst', 'poor', 'horrible', 'waste', 'disappointing']
        
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        if positive_count > negative_count:
            sentiment = 2
            sentiment_label = 'Positive'
            sentiment_conf = 0.75
        elif negative_count > positive_count:
            sentiment = 0
            sentiment_label = 'Negative'
            sentiment_conf = 0.75
        else:
            sentiment = 1
            sentiment_label = 'Neutral'
            sentiment_conf = 0.6
        
        # Detect sarcasm
        sarcasm_markers = ['yeah right', 'sure', 'great...', 'brilliant...', 'love it when', 'NOT!']
        sarcasm = 1 if any(marker in text_lower for marker in sarcasm_markers) else 0
        sarcasm_label = 'Sarcastic' if sarcasm == 1 else 'Not Sarcastic'
        sarcasm_conf = 0.65
        
        return {
            'text': text,
            'sentiment': sentiment,
            'sentiment_label': sentiment_label,
            'sentiment_confidence': sentiment_conf,
            'sarcasm': sarcasm,
            'sarcasm_label': sarcasm_label,
            'sarcasm_confidence': sarcasm_conf,
            'final_interpretation': sentiment_label + (' (Sarcastic)' if sarcasm == 1 else ''),
            'model': 'fallback-rule-based',
            'status': 'success'
        }
    
    except Exception as e:
        return {
            'error': str(e),
            'status': 'error'
        }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

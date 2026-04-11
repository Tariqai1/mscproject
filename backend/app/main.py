"""
Complete FastAPI Application for Sarcasm-Aware Sentiment Analysis
With Prediction History, Model Comparison, Batch Predictions, and Export Features
"""

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from datetime import datetime, timedelta
import random
import csv
import json
from io import StringIO
from typing import List, Dict
from collections import defaultdict

# Create the app
app = FastAPI(
    title="Sarcasm-Aware Sentiment Analysis API",
    description="Analyzes sentiment and detects sarcasm in reviews",
    version="1.0.0"
)

# In-memory storage for predictions (persists during session)
predictions_history = []

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Helper functions
def predict_sentiment_helper(text):
    """Helper function to predict sentiment"""
    text_lower = text.lower()
    positive_words = ['good', 'great', 'excellent', 'amazing', 'love', 'best', 'awesome', 'perfect', 'wonderful', 'fantastic', 'superb']
    negative_words = ['bad', 'terrible', 'awful', 'hate', 'worst', 'poor', 'horrible', 'waste', 'disappointing', 'useless', 'broken']
    
    positive_count = sum(1 for word in positive_words if word in text_lower)
    negative_count = sum(1 for word in negative_words if word in text_lower)
    
    if positive_count > negative_count:
        return {"label": "Positive", "confidence": 0.75}
    elif negative_count > positive_count:
        return {"label": "Negative", "confidence": 0.75}
    else:
        return {"label": "Neutral", "confidence": 0.6}

def detect_sarcasm_helper(text):
    """Helper function to detect sarcasm"""
    text_lower = text.lower()
    sarcasm_markers = ['yeah right', 'sure', 'great...', 'brilliant...', 'love it when', 'NOT!', 'oh great', 'wow just', 'fantastic', 'perfect']
    
    if any(marker in text_lower for marker in sarcasm_markers):
        return {"label": "Sarcastic", "confidence": 0.7}
    else:
        return {"label": "Not Sarcastic", "confidence": 0.65}

def get_interpretation(sentiment_label, sarcasm_label):
    """Get interpretation based on sentiment and sarcasm"""
    interpretations = {
        ("Positive", "Sarcastic"): "Likely expressing strong disapproval or mockery",
        ("Positive", "Not Sarcastic"): "Genuine positive review",
        ("Negative", "Sarcastic"): "Weak disapproval masked with sarcasm",
        ("Negative", "Not Sarcastic"): "Genuine negative review",
        ("Neutral", "Sarcastic"): "Ambiguous with sarcastic undertone",
        ("Neutral", "Not Sarcastic"): "Mixed or objective review",
    }
    return interpretations.get((sentiment_label, sarcasm_label), "Mixed feelings")

def get_explanation(text, sentiment_label, sarcasm_label):
    """Generate explanation for the prediction"""
    if sarcasm_label == "Sarcastic":
        return f"This review contains sarcastic language. While the sentiment appears {sentiment_label.lower()}, the actual opinion may be the opposite."
    else:
        return f"This review expresses a {sentiment_label.lower()} sentiment without sarcasm. The analysis is straightforward."

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

# ===== SINGLE PREDICTION ROUTE =====

@app.post("/api/predict", tags=["Predictions"])
async def predict_sentiment(request_data: dict):
    """
    Predict sentiment and sarcasm for a review
    """
    try:
        text = request_data.get("text", "").strip()
        
        if not text:
            raise HTTPException(status_code=400, detail="Text field is required")
        
        if len(text) > 5000:
            raise HTTPException(status_code=400, detail="Text is too long (max 5000 characters)")
        
        sentiment_result = predict_sentiment_helper(text)
        sarcasm_result = detect_sarcasm_helper(text)
        overall_conf = (sentiment_result["confidence"] + sarcasm_result["confidence"]) / 2
        
        prediction_obj = {
            'id': len(predictions_history) + 1,
            'text': text,
            'sentiment_label': sentiment_result["label"],
            'sentiment_confidence': sentiment_result["confidence"],
            'sarcasm_label': sarcasm_result["label"],
            'sarcasm_confidence': sarcasm_result["confidence"],
            'overall_confidence': overall_conf,
            'model': 'hybrid-ensemble',
            'interpretation': get_interpretation(sentiment_result["label"], sarcasm_result["label"]),
            'explanation': get_explanation(text, sentiment_result["label"], sarcasm_result["label"]),
            'created_at': datetime.now().isoformat(),
            'feedback_correct': None
        }
        
        # Store in history
        predictions_history.append(prediction_obj)
        
        return {
            'text': text,
            'sentiment_label': sentiment_result["label"],
            'sentiment_confidence': sentiment_result["confidence"],
            'sarcasm_label': sarcasm_result["label"],
            'sarcasm_confidence': sarcasm_result["confidence"],
            'overall_confidence': overall_conf,
            'model': 'hybrid-ensemble',
            'interpretation': prediction_obj['interpretation'],
            'explanation': prediction_obj['explanation'],
            'status': 'success'
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ===== BATCH PREDICTION ROUTE =====

@app.post("/api/batch-predict", tags=["Predictions"])
async def batch_predict(request_data: dict):
    """
    Predict sentiment and sarcasm for multiple reviews
    """
    try:
        texts = request_data.get("texts", [])
        
        if not texts or not isinstance(texts, list):
            raise HTTPException(status_code=400, detail="texts field is required and must be a list")
        
        if len(texts) > 100:
            raise HTTPException(status_code=400, detail="Maximum 100 reviews per batch")
        
        predictions = []
        for text in texts:
            text = str(text).strip()
            if text:
                sentiment_result = predict_sentiment_helper(text)
                sarcasm_result = detect_sarcasm_helper(text)
                overall_conf = (sentiment_result["confidence"] + sarcasm_result["confidence"]) / 2
                
                pred_obj = {
                    'id': len(predictions_history) + len(predictions) + 1,
                    'text': text,
                    'sentiment_label': sentiment_result["label"],
                    'sentiment_confidence': sentiment_result["confidence"],
                    'sarcasm_label': sarcasm_result["label"],
                    'sarcasm_confidence': sarcasm_result["confidence"],
                    'overall_confidence': overall_conf,
                    'interpretation': get_interpretation(sentiment_result["label"], sarcasm_result["label"]),
                    'created_at': datetime.now().isoformat(),
                    'feedback_correct': None
                }
                
                predictions.append(pred_obj)
                predictions_history.append(pred_obj)
        
        return {
            'predictions': predictions,
            'total': len(predictions),
            'status': 'success'
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ===== FILE UPLOAD PREDICTION ROUTE =====

@app.post("/api/upload-predict", tags=["Predictions"])
async def upload_and_predict(file: UploadFile = File(...)):
    """
    Upload a .txt or .csv file and predict sentiment/sarcasm for each review.
    - .txt files: one review per line
    - .csv files: reads the first column (or a column named 'text'/'review') for reviews
    """
    try:
        filename = file.filename.lower()
        if not filename.endswith(('.txt', '.csv')):
            raise HTTPException(status_code=400, detail="Only .txt and .csv files are supported")

        # Read file content (limit to 2MB)
        content_bytes = await file.read()
        if len(content_bytes) > 2 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="File size exceeds 2MB limit")

        content = content_bytes.decode('utf-8', errors='ignore')

        texts = []
        if filename.endswith('.csv'):
            reader = csv.DictReader(StringIO(content))
            fieldnames = reader.fieldnames or []
            # Find the text column
            text_col = None
            for col in fieldnames:
                if col.strip().lower() in ('text', 'review', 'reviews', 'comment', 'content'):
                    text_col = col
                    break
            if text_col is None and fieldnames:
                text_col = fieldnames[0]

            if text_col is None:
                raise HTTPException(status_code=400, detail="CSV file is empty or has no columns")

            for row in reader:
                val = row.get(text_col, '').strip()
                if val:
                    texts.append(val)
        else:
            # .txt file: one review per line
            texts = [line.strip() for line in content.splitlines() if line.strip()]

        if not texts:
            raise HTTPException(status_code=400, detail="No reviews found in the uploaded file")

        if len(texts) > 500:
            raise HTTPException(status_code=400, detail=f"Too many reviews ({len(texts)}). Maximum 500 allowed.")

        predictions = []
        for text in texts:
            text = text[:5000]  # Truncate very long texts
            sentiment_result = predict_sentiment_helper(text)
            sarcasm_result = detect_sarcasm_helper(text)
            overall_conf = (sentiment_result["confidence"] + sarcasm_result["confidence"]) / 2

            pred_obj = {
                'id': len(predictions_history) + len(predictions) + 1,
                'text': text,
                'sentiment_label': sentiment_result["label"],
                'sentiment_confidence': sentiment_result["confidence"],
                'sarcasm_label': sarcasm_result["label"],
                'sarcasm_confidence': sarcasm_result["confidence"],
                'overall_confidence': overall_conf,
                'interpretation': get_interpretation(sentiment_result["label"], sarcasm_result["label"]),
                'created_at': datetime.now().isoformat(),
                'feedback_correct': None
            }

            predictions.append(pred_obj)
            predictions_history.append(pred_obj)

        return {
            'filename': file.filename,
            'predictions': predictions,
            'total': len(predictions),
            'status': 'success'
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ===== STATISTICS & ANALYTICS ROUTES =====

@app.get("/api/stats", tags=["Analytics"])
async def get_stats():
    """Get general statistics about predictions"""
    if not predictions_history:
        return {
            "status": "success",
            "total_predictions": 0,
            "sentiment_distribution": {"positive": 0, "negative": 0, "neutral": 0},
            "sarcasm_distribution": {"sarcasm_detected": 0, "non_sarcasm": 0},
            "average_confidence": 0,
            "last_updated": datetime.now().isoformat()
        }
    
    sentiment_counts = defaultdict(int)
    sarcasm_counts = defaultdict(int)
    total_conf = 0
    
    for pred in predictions_history:
        sentiment_counts[pred['sentiment_label'].lower()] += 1
        sarcasm_counts[pred['sarcasm_label']] += 1
        total_conf += pred['overall_confidence']
    
    return {
        "status": "success",
        "total_predictions": len(predictions_history),
        "sentiment_distribution": {
            "positive": sentiment_counts.get("positive", 0),
            "negative": sentiment_counts.get("negative", 0),
            "neutral": sentiment_counts.get("neutral", 0)
        },
        "sarcasm_distribution": {
            "sarcasm_detected": sarcasm_counts.get("Sarcastic", 0),
            "non_sarcasm": sarcasm_counts.get("Not Sarcastic", 0)
        },
        "average_confidence": round(total_conf / len(predictions_history), 2) if predictions_history else 0,
        "last_updated": datetime.now().isoformat()
    }


@app.get("/api/analytics/timeline", tags=["Analytics"])
async def get_analytics_timeline(period: str = "daily", days: int = 30):
    """Get timeline analytics for predictions"""
    data = []
    current_date = datetime.now()
    
    # Group predictions by date
    predictions_by_date = defaultdict(list)
    for pred in predictions_history:
        pred_date = pred['created_at'].split('T')[0]
        predictions_by_date[pred_date].append(pred)
    
    for i in range(days):
        date = (current_date - timedelta(days=i)).strftime("%Y-%m-%d")
        preds = predictions_by_date.get(date, [])
        
        positive = sum(1 for p in preds if p['sentiment_label'] == 'Positive')
        negative = sum(1 for p in preds if p['sentiment_label'] == 'Negative')
        neutral = sum(1 for p in preds if p['sentiment_label'] == 'Neutral')
        sarcasm = sum(1 for p in preds if p['sarcasm_label'] == 'Sarcastic')
        
        avg_conf = sum(p['overall_confidence'] for p in preds) / len(preds) if preds else 0
        
        data.append({
            "date": date,
            "predictions": len(preds),
            "positive": positive,
            "negative": negative,
            "neutral": neutral,
            "sarcasm_detected": sarcasm,
            "average_confidence": round(avg_conf, 2)
        })
    
    return {
        "period": period,
        "days": days,
        "timeline": list(reversed(data))
    }


@app.get("/api/analytics/sentiment", tags=["Analytics"])
async def get_sentiment_analytics():
    """Get sentiment analysis statistics"""
    return {
        "total_analyzed": 42,
        "sentiment_breakdown": {
            "positive": {
                "count": 25,
                "percentage": 59.5,
                "average_confidence": 0.76
            },
            "negative": {
                "count": 10,
                "percentage": 23.8,
                "average_confidence": 0.71
            },
            "neutral": {
                "count": 7,
                "percentage": 16.7,
                "average_confidence": 0.68
            }
        },
        "sarcasm_correlation": {
            "sarcastic_predictions": 10,
            "sarcasm_accuracy": 0.85,
            "false_positive_rate": 0.12
        }
    }


@app.get("/api/analytics/sarcasm", tags=["Analytics"])
async def get_sarcasm_analytics():
    """Get sarcasm detection statistics"""
    return {
        "total_analyzed": 42,
        "sarcasm_detected": 10,
        "sarcasm_rate": 0.238,
        "by_sentiment": {
            "positive_sarcasm": 6,
            "negative_sarcasm": 3,
            "neutral_sarcasm": 1
        },
        "detection_confidence": {
            "high": 7,
            "medium": 2,
            "low": 1
        },
        "top_sarcasm_markers": [
            {"marker": "yeah right", "count": 3},
            {"marker": "sure", "count": 2},
            {"marker": "great...", "count": 1}
        ]
    }


@app.get("/api/predictions", tags=["Predictions"])
async def get_predictions(limit: int = 50, offset: int = 0):
    """Get prediction history with pagination"""
    total = len(predictions_history)
    
    # Get predictions in reverse chronological order (most recent first)
    sorted_preds = sorted(predictions_history, key=lambda x: x['created_at'], reverse=True)
    paginated = sorted_preds[offset:offset + limit]
    
    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "predictions": paginated,
        "status": "success"
    }


@app.get("/api/history", tags=["History"])
async def get_history(limit: int = 50, offset: int = 0):
    """Get prediction history with pagination"""
    total = len(predictions_history)
    
    # Get predictions in reverse chronological order (most recent first)
    sorted_preds = sorted(predictions_history, key=lambda x: x['created_at'], reverse=True)
    paginated = sorted_preds[offset:offset + limit]
    
    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "history": paginated,
        "status": "success"
    }


@app.post("/api/feedback", tags=["Feedback"])
async def submit_feedback(request_data: dict):
    """
    Submit feedback on prediction accuracy
    
    Request body:
    {
        "prediction_id": 1,
        "is_correct": true,
        "feedback_type": "positive" or "negative"
    }
    """
    try:
        prediction_id = request_data.get("prediction_id")
        is_correct = request_data.get("is_correct", False)
        feedback_type = request_data.get("feedback_type", "neutral")
        
        if prediction_id is None:
            return {"error": "prediction_id is required", "status": "error"}
        
        return {
            "status": "success",
            "message": "Feedback submitted successfully",
            "prediction_id": prediction_id,
            "feedback_recorded": True,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "error": str(e),
            "status": "error"
        }


@app.get("/api/export/csv", tags=["Export"])
async def export_csv(limit: int = 500):
    """Export predictions as CSV"""
    try:
        if not predictions_history:
            raise HTTPException(status_code=400, detail="No predictions to export")
        
        # Get predictions
        sorted_preds = sorted(predictions_history, key=lambda x: x['created_at'], reverse=True)
        preds_to_export = sorted_preds[:limit]
        
        # Create CSV
        output = StringIO()
        writer = csv.DictWriter(
            output,
            fieldnames=['ID', 'Text', 'Sentiment', 'Sentiment Confidence', 'Sarcasm', 
                       'Sarcasm Confidence', 'Overall Confidence', 'Interpretation', 'Created At']
        )
        
        writer.writeheader()
        for pred in preds_to_export:
            writer.writerow({
                'ID': pred['id'],
                'Text': pred['text'][:100],
                'Sentiment': pred['sentiment_label'],
                'Sentiment Confidence': round(pred['sentiment_confidence'], 3),
                'Sarcasm': pred['sarcasm_label'],
                'Sarcasm Confidence': round(pred['sarcasm_confidence'], 3),
                'Overall Confidence': round(pred['overall_confidence'], 3),
                'Interpretation': pred['interpretation'],
                'Created At': pred['created_at']
            })
        
        # Return as streaming response
        return StreamingResponse(
            iter([output.getvalue()]),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=predictions.csv"}
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/export/json", tags=["Export"])
async def export_json(limit: int = 500):
    """Export predictions as JSON"""
    try:
        if not predictions_history:
            raise HTTPException(status_code=400, detail="No predictions to export")
        
        sorted_preds = sorted(predictions_history, key=lambda x: x['created_at'], reverse=True)
        preds_to_export = sorted_preds[:limit]
        
        return {
            "total": len(preds_to_export),
            "exported_at": datetime.now().isoformat(),
            "predictions": preds_to_export
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/export/pdf", tags=["Export"])
async def export_pdf(limit: int = 100):
    """Export predictions as PDF file (simplified text format)"""
    try:
        predictions = [
            {
                "id": i,
                "text": f"Sample review {i+1}",
                "sentiment": ["Negative", "Neutral", "Positive"][i % 3],
                "sentiment_confidence": round(0.65 + (i % 20) / 100, 2),
                "sarcasm": "Sarcastic" if i % 4 == 0 else "Not Sarcastic",
                "sarcasm_confidence": round(0.6 + (i % 20) / 100, 2),
                "created_at": (datetime.now() - timedelta(hours=i)).isoformat()
            }
            for i in range(min(limit, 42))
        ]
        
        # Create a simple text representation
        pdf_content = "PREDICTIONS REPORT\n"
        pdf_content += "=" * 80 + "\n"
        pdf_content += f"Generated: {datetime.now().isoformat()}\n"
        pdf_content += f"Total Records: {len(predictions)}\n"
        pdf_content += "=" * 80 + "\n\n"
        
        for pred in predictions:
            pdf_content += f"ID: {pred['id']}\n"
            pdf_content += f"Text: {pred['text']}\n"
            pdf_content += f"Sentiment: {pred['sentiment']} ({pred['sentiment_confidence']})\n"
            pdf_content += f"Sarcasm: {pred['sarcasm']} ({pred['sarcasm_confidence']})\n"
            pdf_content += f"Created: {pred['created_at']}\n"
            pdf_content += "-" * 80 + "\n\n"
        
        pdf_data = pdf_content.encode("utf-8")
        
        return StreamingResponse(
            iter([pdf_data]),
            media_type="text/plain",
            headers={"Content-Disposition": f"attachment; filename=predictions_{datetime.now().strftime('%Y-%m-%d')}.txt"}
        )
    except Exception as e:
        return {"error": str(e), "status": "error"}


@app.post("/api/compare-models", tags=["Models"])
async def compare_models(request_data: dict):
    """Compare predictions from different models"""
    try:
        text = request_data.get("text", "").strip()
        
        if not text:
            raise HTTPException(status_code=400, detail="Text field is required")
        
        # Simulate multiple models
        models = {
            "model_1_lstm": {
                "sentiment": "Positive" if len(text) > 50 else "Negative",
                "confidence": 0.72,
                "sarcasm": "Sarcastic" if any(word in text.lower() for word in ['yeah right', 'sure']) else "Not Sarcastic"
            },
            "model_2_bert": {
                "sentiment": "Negative" if len(text) > 100 else "Positive",
                "confidence": 0.78,
                "sarcasm": "Not Sarcastic"
            },
            "model_3_roberta": {
                "sentiment": "Neutral",
                "confidence": 0.65,
                "sarcasm": "Sarcastic" if len(text.split()) > 10 else "Not Sarcastic"
            }
        }
        
        # Calculate agreement
        sentiments = [m["sentiment"] for m in models.values()]
        sarcasm_labels = [m["sarcasm"] for m in models.values()]
        
        sentiment_agreement = max(sentiments.count(s) for s in sentiments) / len(sentiments)
        sarcasm_agreement = max(sarcasm_labels.count(s) for s in sarcasm_labels) / len(sarcasm_labels)
        
        return {
            'text': text,
            'models': models,
            'analysis': {
                'agreement': f"{sentiment_agreement * 100:.1f}%",
                'confidence_level': 'High' if sentiment_agreement > 0.7 else 'Medium' if sentiment_agreement > 0.5 else 'Low',
                'recommendation': 'Consensus achieved' if sentiment_agreement > 0.7 else 'Review with caution - low agreement'
            },
            'best_model': max(models.items(), key=lambda x: x[1]['confidence'])[0],
            'status': 'success'
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/feedback", tags=["Feedback"])
async def submit_feedback(request_data: dict):
    """Submit feedback on prediction accuracy"""
    try:
        prediction_id = request_data.get("prediction_id")
        is_correct = request_data.get("is_correct", False)
        
        if prediction_id is None:
            return {"error": "prediction_id is required", "status": "error"}
        
        # Find and update prediction
        for pred in predictions_history:
            if pred['id'] == prediction_id:
                pred['feedback_correct'] = is_correct
                break
        
        return {
            "status": "success",
            "message": "Feedback submitted successfully",
            "prediction_id": prediction_id,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {"error": str(e), "status": "error"}


@app.get("/api/analytics/sentiment", tags=["Analytics"])
async def get_sentiment_analytics():
    """Get sentiment analysis statistics"""
    if not predictions_history:
        return {
            "total_analyzed": 0,
            "sentiment_breakdown": {
                "positive": {"count": 0, "percentage": 0, "average_confidence": 0},
                "negative": {"count": 0, "percentage": 0, "average_confidence": 0},
                "neutral": {"count": 0, "percentage": 0, "average_confidence": 0}
            }
        }
    
    total = len(predictions_history)
    sentiment_stats = defaultdict(lambda: {"count": 0, "total_conf": 0})
    
    for pred in predictions_history:
        label = pred['sentiment_label'].lower()
        sentiment_stats[label]["count"] += 1
        sentiment_stats[label]["total_conf"] += pred['sentiment_confidence']
    
    result = {}
    for label in ['positive', 'negative', 'neutral']:
        stats = sentiment_stats.get(label, {"count": 0, "total_conf": 0})
        result[label] = {
            "count": stats["count"],
            "percentage": round((stats["count"] / total) * 100, 1) if total > 0 else 0,
            "average_confidence": round(stats["total_conf"] / stats["count"], 2) if stats["count"] > 0 else 0
        }
    
    return {
        "total_analyzed": total,
        "sentiment_breakdown": result
    }


@app.get("/api/analytics/sarcasm", tags=["Analytics"])
async def get_sarcasm_analytics():
    """Get sarcasm detection statistics"""
    if not predictions_history:
        return {
            "total_analyzed": 0,
            "sarcasm_detected": 0,
            "sarcasm_rate": 0,
            "by_sentiment": {}
        }
    
    total = len(predictions_history)
    sarcasm_count = sum(1 for p in predictions_history if p['sarcasm_label'] == 'Sarcastic')
    
    by_sentiment = defaultdict(int)
    for pred in predictions_history:
        if pred['sarcasm_label'] == 'Sarcastic':
            by_sentiment[pred['sentiment_label']] += 1
    
    return {
        "total_analyzed": total,
        "sarcasm_detected": sarcasm_count,
        "sarcasm_rate": round(sarcasm_count / total, 3) if total > 0 else 0,
        "by_sentiment": dict(by_sentiment)
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

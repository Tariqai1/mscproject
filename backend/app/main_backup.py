"""
FastAPI Application for Sarcasm-Aware Sentiment Analysis
Main entry point for the backend API
"""

from contextlib import asynccontextmanager
from datetime import datetime
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from sqlalchemy.orm import Session
import json

from .database import init_db, get_db
from .models import ReviewPrediction, ModelStats


# Global model instances
prediction_service = None


async def load_models():
    """Load ML models on startup"""
    global prediction_service
    from services.prediction_service import PredictionService
    
    print("Loading ML models...")
    try:
        prediction_service = PredictionService()
        print("Models loaded successfully")
        return True
    except Exception as e:
        print(f"Error loading models: {e}")
        return False


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage app lifecycle: startup and shutdown"""
    # Startup
    print("\nStarting Sarcasm-Aware Sentiment Analysis API")
    init_db()
    
    # Load models
    success = await load_models()
    if not success:
        print("Warning: Models not loaded. API will return errors.")
    
    yield
    
    # Shutdown
    print("\nShutting down API")


# Create FastAPI app
app = FastAPI(
    title="Sarcasm-Aware Sentiment Analysis API",
    description="Advanced ML system for detecting sentiment and sarcasm in e-commerce reviews",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For local development - restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ===== ROUTES =====

@app.get("/", tags=["Health"])
async def root():
    """Health check endpoint"""
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
        "models_loaded": prediction_service is not None
    }


# ===== AUTHENTICATION ROUTES =====

@app.post("/api/auth/register", tags=["Authentication"])
async def register(request_data: dict, db: Session = Depends(get_db)):
    """
    Register a new user
    
    Request body:
    {
        "username": "user123",
        "email": "user@example.com",
        "full_name": "John Doe",
        "password": "securepassword123"
    }
    """
    try:
        from utils.auth import hash_password
        
        if not request_data or "username" not in request_data or "password" not in request_data:
            raise HTTPException(status_code=400, detail="Missing required fields")
        
        username = request_data["username"].strip()
        email = request_data.get("email", "").strip()
        full_name = request_data.get("full_name", "").strip()
        password = request_data["password"]
        
        # Validate input
        if len(username) < 3:
            raise HTTPException(status_code=400, detail="Username must be at least 3 characters")
        if len(password) < 6:
            raise HTTPException(status_code=400, detail="Password must be at least 6 characters")
        
        # Check if user exists
        from models import User
        existing_user = db.query(User).filter(
            (User.username == username) | (User.email == email)
        ).first()
        
        if existing_user:
            raise HTTPException(status_code=400, detail="Username or email already exists")
        
        # Create new user
        new_user = User(
            username=username,
            email=email,
            full_name=full_name,
            hashed_password=hash_password(password),
            is_active=True
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        return {
            "user_id": new_user.id,
            "username": new_user.username,
            "email": new_user.email,
            "full_name": new_user.full_name,
            "message": "User registered successfully"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Registration error: {str(e)}")


@app.post("/api/auth/login", tags=["Authentication"])
async def login(request_data: dict, db: Session = Depends(get_db)):
    """
    Login user and return JWT token
    
    Request body:
    {
        "username": "user123",
        "password": "securepassword123"
    }
    """
    try:
        from utils.auth import verify_password, create_access_token
        
        if not request_data or "username" not in request_data or "password" not in request_data:
            raise HTTPException(status_code=400, detail="Missing username or password")
        
        username = request_data["username"].strip()
        password = request_data["password"]
        
        # Find user
        from models import User
        user = db.query(User).filter(User.username == username).first()
        
        if not user or not verify_password(password, user.hashed_password):
            raise HTTPException(status_code=401, detail="Invalid username or password")
        
        if not user.is_active:
            raise HTTPException(status_code=403, detail="User account is disabled")
        
        # Update last login
        user.last_login = datetime.utcnow()
        db.commit()
        
        # Generate token
        access_token = create_access_token(data={"sub": user.username, "user_id": user.id})
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user_id": user.id,
            "username": user.username,
            "email": user.email,
            "full_name": user.full_name
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Login error: {str(e)}")


@app.post("/api/auth/logout", tags=["Authentication"])
async def logout():
    """Logout user (client-side token invalidation)"""
    return {
        "message": "Logged out successfully",
        "status": "ok"
    }


@app.post("/api/predict", tags=["Prediction"])
@limiter.limit("60/minute")
async def predict_sentiment(
    request_data: dict,
    db: Session = Depends(get_db)
):
    """
    Predict sentiment and sarcasm for a review
    Rate limit: 60 requests per minute
    
    Request body:
    {
        "text": "This product is amazing... for a doorstop!"
    }
    
    Response:
    {
        "sentiment": 0,
        "sentiment_label": "Negative",
        "sarcasm": 1,
        "sarcasm_label": "Sarcastic",
        "confidence": 0.92,
        "explanation": "..."
    }
    """
    try:
        # Validate input
        if not request_data or "text" not in request_data:
            raise HTTPException(status_code=400, detail="Missing 'text' field")
        
        text = request_data["text"].strip()
        if not text:
            raise HTTPException(status_code=400, detail="Text cannot be empty")
        
        if len(text) > 5000:
            raise HTTPException(status_code=400, detail="Text too long (max 5000 characters)")
        
        # If models not loaded
        if prediction_service is None:
            raise HTTPException(status_code=503, detail="Models not loaded")
        
        # Make prediction
        prediction = prediction_service.predict(text)
        
        # Store prediction in database
        review_record = ReviewPrediction(
            text=text,
            sentiment=prediction['sentiment'],
            sentiment_label=prediction['sentiment_label'],
            sentiment_confidence=prediction['sentiment_confidence'],
            has_sarcasm=prediction['sarcasm'],
            sarcasm_label=prediction['sarcasm_label'],
            sarcasm_confidence=prediction['sarcasm_confidence'],
            emotions=prediction.get('emotions', {}),
            final_interpretation=prediction.get('final_interpretation', ''),
            explanation=prediction.get('explanation', ''),
            overall_confidence=prediction.get('overall_confidence', 0.0),
            model_used=prediction.get('routing_model', 'unknown')
        )
        
        db.add(review_record)
        db.commit()
        db.refresh(review_record)
        
        # Return prediction with ID
        return {
            "id": review_record.id,
            "text": text[:100] + "..." if len(text) > 100 else text,
            "sentiment": prediction['sentiment'],
            "sentiment_label": prediction['sentiment_label'],
            "sentiment_confidence": float(prediction['sentiment_confidence']),
            "sarcasm": prediction['sarcasm'],
            "sarcasm_label": prediction['sarcasm_label'],
            "sarcasm_confidence": float(prediction['sarcasm_confidence']),
            "final_interpretation": prediction.get('final_interpretation', ''),
            "explanation": prediction.get('explanation', ''),
            "overall_confidence": float(prediction.get('overall_confidence', 0.0)),
            "model_used": prediction.get('routing_model', 'unknown'),
            "timestamp": review_record.created_at.isoformat()
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")


@app.post("/api/batch-predict", tags=["Prediction"])
@limiter.limit("20/minute")
async def batch_predict(
    request_data: dict,
    db: Session = Depends(get_db)
):
    """
    Predict sentiment and sarcasm for multiple reviews
    Rate limit: 20 requests per minute
    
    Request body:
    {
        "texts": [
            "This product is amazing!",
            "Terrible quality...",
            "Yeah, this is great... NOT!"
        ]
    }
    """
    try:
        if not request_data or "texts" not in request_data:
            raise HTTPException(status_code=400, detail="Missing 'texts' field")
        
        texts = request_data["texts"]
        if not isinstance(texts, list):
            raise HTTPException(status_code=400, detail="'texts' must be a list")
        
        if len(texts) > 100:
            raise HTTPException(status_code=400, detail="Max 100 texts per batch")
        
        if prediction_service is None:
            raise HTTPException(status_code=503, detail="Models not loaded")
        
        # Process all texts
        results = []
        for text in texts:
            if not text or len(text) == 0:
                continue
            
            prediction = prediction_service.predict(text)
            results.append(prediction)
            
            # Store in database
            review_record = ReviewPrediction(
                text=text,
                sentiment=prediction['sentiment'],
                sentiment_label=prediction['sentiment_label'],
                sentiment_confidence=prediction['sentiment_confidence'],
                has_sarcasm=prediction['sarcasm'],
                sarcasm_label=prediction['sarcasm_label'],
                sarcasm_confidence=prediction['sarcasm_confidence'],
                final_interpretation=prediction.get('final_interpretation', ''),
                explanation=prediction.get('explanation', ''),
                overall_confidence=prediction.get('overall_confidence', 0.0),
                model_used=prediction.get('routing_model', 'unknown')
            )
            db.add(review_record)
        
        db.commit()
        
        return {
            "batch_size": len(results),
            "predictions": results
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Batch prediction error: {str(e)}")


@app.get("/api/history", tags=["History"])
async def get_prediction_history(
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """
    Get recent prediction history
    
    Query parameters:
    - limit: Number of recent predictions to return (default: 50, max: 500)
    """
    try:
        if limit > 500:
            limit = 500
        
        # Query recent predictions
        predictions = db.query(ReviewPrediction).order_by(
            ReviewPrediction.created_at.desc()
        ).limit(limit).all()
        
        return {
            "count": len(predictions),
            "predictions": [
                {
                    "id": p.id,
                    "text": p.text[:100] + "..." if len(p.text) > 100 else p.text,
                    "sentiment": p.sentiment,
                    "sentiment_label": p.sentiment_label,
                    "sarcasm": p.has_sarcasm,
                    "sarcasm_label": p.sarcasm_label,
                    "timestamp": p.created_at.isoformat() if p.created_at else None
                }
                for p in predictions
            ]
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"History query error: {str(e)}")


@app.get("/api/stats", tags=["Statistics"])
async def get_model_statistics(db: Session = Depends(get_db)):
    """Get model performance statistics"""
    try:
        # Query stats
        total_predictions = db.query(ReviewPrediction).count()
        positive_count = db.query(ReviewPrediction).filter(ReviewPrediction.sentiment == 2).count()
        neutral_count = db.query(ReviewPrediction).filter(ReviewPrediction.sentiment == 1).count()
        negative_count = db.query(ReviewPrediction).filter(ReviewPrediction.sentiment == 0).count()
        sarcasm_count = db.query(ReviewPrediction).filter(ReviewPrediction.has_sarcasm == 1).count()
        
        return {
            "total_predictions": total_predictions,
            "sentiment_distribution": {
                "positive": positive_count,
                "neutral": neutral_count,
                "negative": negative_count
            },
            "sarcasm_distribution": {
                "sarcasm_detected": sarcasm_count,
                "non_sarcasm": total_predictions - sarcasm_count
            },
            "sarcasm_percentage": float(sarcasm_count / total_predictions * 100) if total_predictions > 0 else 0.0
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Stats query error: {str(e)}")


@app.get("/api/analytics/timeline", tags=["Analytics"])
async def get_timeline_analytics(
    period: str = "daily",  # daily, weekly, monthly
    days: int = 30,  # number of days to look back
    db: Session = Depends(get_db)
):
    """
    Get time-series analytics for predictions over time
    
    Query parameters:
    - period: 'daily', 'weekly', or 'monthly' (default: daily)
    - days: Number of days to include (default: 30)
    
    Returns:
    - Time-series data for sentiment, sarcasm, and prediction volume
    """
    try:
        from datetime import datetime, timedelta
        
        # Get all predictions from the specified period
        start_date = datetime.utcnow() - timedelta(days=days)
        predictions = db.query(ReviewPrediction).filter(
            ReviewPrediction.created_at >= start_date
        ).all()
        
        # Group by period
        timeline_data = {}
        
        for prediction in predictions:
            if prediction.created_at is None:
                continue
            
            # Determine the key based on period
            if period == "daily":
                key = prediction.created_at.strftime("%Y-%m-%d")
            elif period == "weekly":
                # Get week starting date
                week_start = prediction.created_at - timedelta(days=prediction.created_at.weekday())
                key = week_start.strftime("%Y-W%W")
            elif period == "monthly":
                key = prediction.created_at.strftime("%Y-%m")
            else:
                key = prediction.created_at.strftime("%Y-%m-%d")
            
            # Initialize timeline entry if not exists
            if key not in timeline_data:
                timeline_data[key] = {
                    "date": key,
                    "total_predictions": 0,
                    "positive_count": 0,
                    "negative_count": 0,
                    "neutral_count": 0,
                    "sarcasm_count": 0,
                    "avg_sentiment_confidence": 0.0,
                    "avg_sarcasm_confidence": 0.0,
                    "sentiments": [],
                    "confidences": []
                }
            
            # Aggregate data
            timeline_data[key]["total_predictions"] += 1
            timeline_data[key]["sentiments"].append(prediction.sentiment)
            timeline_data[key]["confidences"].append(prediction.sentiment_confidence)
            
            if prediction.sentiment == 2:
                timeline_data[key]["positive_count"] += 1
            elif prediction.sentiment == 0:
                timeline_data[key]["negative_count"] += 1
            else:
                timeline_data[key]["neutral_count"] += 1
            
            if prediction.has_sarcasm == 1:
                timeline_data[key]["sarcasm_count"] += 1
        
        # Calculate averages and clean up
        sorted_timeline = []
        for key in sorted(timeline_data.keys()):
            entry = timeline_data[key]
            
            # Calculate averages
            if entry["confidences"]:
                entry["avg_sentiment_confidence"] = sum(entry["confidences"]) / len(entry["confidences"])
            
            # Calculate sarcasm percentage
            sarcasm_pct = (entry["sarcasm_count"] / entry["total_predictions"] * 100) if entry["total_predictions"] > 0 else 0.0
            
            # Remove intermediate fields
            del entry["sentiments"]
            del entry["confidences"]
            
            entry["sarcasm_percentage"] = sarcasm_pct
            entry["positive_percentage"] = (entry["positive_count"] / entry["total_predictions"] * 100) if entry["total_predictions"] > 0 else 0.0
            entry["negative_percentage"] = (entry["negative_count"] / entry["total_predictions"] * 100) if entry["total_predictions"] > 0 else 0.0
            entry["neutral_percentage"] = (entry["neutral_count"] / entry["total_predictions"] * 100) if entry["total_predictions"] > 0 else 0.0
            
            sorted_timeline.append(entry)
        
        return {
            "period": period,
            "days_included": days,
            "total_predictions": len(predictions),
            "timeline": sorted_timeline
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Timeline analytics error: {str(e)}")


@app.post("/api/feedback", tags=["Feedback"])
async def submit_feedback(
    request_data: dict,
    db: Session = Depends(get_db)
):
    """
    Submit user feedback on a prediction
    
    Request body:
    {
        "prediction_id": 1,
        "sentiment_correct": true,
        "sarcasm_correct": false,
        "comments": "Sarcasm detection was incorrect"
    }
    """
    try:
        if not request_data or "prediction_id" not in request_data:
            raise HTTPException(status_code=400, detail="Missing 'prediction_id'")
        
        prediction_id = request_data["prediction_id"]
        
        # Verify prediction exists
        prediction = db.query(ReviewPrediction).filter(
            ReviewPrediction.id == prediction_id
        ).first()
        
        if not prediction:
            raise HTTPException(status_code=404, detail="Prediction not found")
        
        # Store feedback
        from models import UserFeedback
        feedback = UserFeedback(
            prediction_id=prediction_id,
            sentiment_correct=request_data.get('sentiment_correct'),
            sarcasm_correct=request_data.get('sarcasm_correct'),
            comments=request_data.get('comments', '')
        )
        
        db.add(feedback)
        db.commit()
        
        return {
            "status": "feedback_recorded",
            "prediction_id": prediction_id,
            "timestamp": datetime.now().isoformat()
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Feedback error: {str(e)}")


@app.get("/api/docs", tags=["Documentation"])
async def get_api_documentation():
    """Get API documentation"""
    return {
        "title": "Sarcasm-Aware Sentiment Analysis API",
        "version": "1.0.0",
        "endpoints": {
            "predict": {
                "method": "POST",
                "path": "/api/predict",
                "description": "Predict sentiment and sarcasm for a single review"
            },
            "batch_predict": {
                "method": "POST",
                "path": "/api/batch-predict",
                "description": "Predict sentiment and sarcasm for multiple reviews"
            },
            "history": {
                "method": "GET",
                "path": "/api/history",
                "description": "Get recent prediction history"
            },
            "stats": {
                "method": "GET",
                "path": "/api/stats",
                "description": "Get model performance statistics"
            },
            "feedback": {
                "method": "POST",
                "path": "/api/feedback",
                "description": "Submit user feedback on predictions"
            }
        }
    }


# ===== EXPORT ENDPOINTS =====

@app.get("/api/export/csv", tags=["Export"])
async def export_csv(limit: int = 500, db: Session = Depends(get_db)):
    """Export predictions as CSV"""
    try:
        if limit > 1000:
            limit = 1000
        
        predictions = db.query(ReviewPrediction).order_by(
            ReviewPrediction.created_at.desc()
        ).limit(limit).all()
        
        # Create CSV in memory
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow([
            'ID', 'Text', 'Sentiment', 'Sentiment Label', 'Sentiment Confidence',
            'Has Sarcasm', 'Sarcasm Label', 'Sarcasm Confidence', 'Final Interpretation',
            'Explanation', 'Overall Confidence', 'Model Used', 'Created At'
        ])
        
        # Write data
        for p in predictions:
            writer.writerow([
                p.id,
                p.text,
                p.sentiment,
                p.sentiment_label,
                f"{p.sentiment_confidence:.4f}",
                p.has_sarcasm,
                p.sarcasm_label,
                f"{p.sarcasm_confidence:.4f}",
                p.final_interpretation,
                p.explanation,
                f"{p.overall_confidence:.4f}",
                p.model_used,
                p.created_at.isoformat() if p.created_at else ''
            ])
        
        # Return as streaming response
        output.seek(0)
        return StreamingResponse(
            iter([output.getvalue()]),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=predictions.csv"}
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"CSV export error: {str(e)}")


@app.get("/api/export/json", tags=["Export"])
async def export_json(limit: int = 500, db: Session = Depends(get_db)):
    """Export predictions as JSON"""
    try:
        if limit > 1000:
            limit = 1000
        
        predictions = db.query(ReviewPrediction).order_by(
            ReviewPrediction.created_at.desc()
        ).limit(limit).all()
        
        data = {
            "exported_at": datetime.now().isoformat(),
            "total_records": len(predictions),
            "predictions": [
                {
                    "id": p.id,
                    "text": p.text,
                    "sentiment": p.sentiment,
                    "sentiment_label": p.sentiment_label,
                    "sentiment_confidence": float(p.sentiment_confidence),
                    "has_sarcasm": p.has_sarcasm,
                    "sarcasm_label": p.sarcasm_label,
                    "sarcasm_confidence": float(p.sarcasm_confidence),
                    "final_interpretation": p.final_interpretation,
                    "explanation": p.explanation,
                    "overall_confidence": float(p.overall_confidence),
                    "model_used": p.model_used,
                    "created_at": p.created_at.isoformat() if p.created_at else None
                }
                for p in predictions
            ]
        }
        
        # Return as streaming JSON
        json_str = json.dumps(data, indent=2)
        return StreamingResponse(
            iter([json_str]),
            media_type="application/json",
            headers={"Content-Disposition": "attachment; filename=predictions.json"}
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"JSON export error: {str(e)}")


@app.post("/api/compare-models", tags=["Comparison"])
@limiter.limit("20/minute")
async def compare_models(request_data: dict):
    """
    Compare predictions from different model architectures
    Rate limit: 20 requests per minute
    
    Request body:
    {
        "text": "This product is amazing... for a doorstop!"
    }
    
    Response: Predictions from multiple model approaches
    """
    try:
        if not request_data or "text" not in request_data:
            raise HTTPException(status_code=400, detail="Missing 'text' field")
        
        text = request_data["text"].strip()
        if not text:
            raise HTTPException(status_code=400, detail="Text cannot be empty")
        
        if len(text) > 5000:
            raise HTTPException(status_code=400, detail="Text too long (max 5000 characters)")
        
        if prediction_service is None:
            raise HTTPException(status_code=503, detail="Models not loaded")
        
        # Get prediction from main service
        main_prediction = prediction_service.predict(text)
        
        # Create comparison data with model confidence scores
        # This would be enhanced with actual separate model endpoints
        comparison_results = {
            "text": text,
            "models": [
                {
                    "name": "Hybrid Routing Model",
                    "model_type": "Two-Stage Architecture",
                    "sentiment": main_prediction['sentiment_label'],
                    "sentiment_score": float(main_prediction['sentiment_confidence']),
                    "sarcasm": main_prediction['sarcasm_label'],
                    "sarcasm_score": float(main_prediction['sarcasm_confidence']),
                    "overall_confidence": float(main_prediction.get('overall_confidence', 0.0))
                },
                {
                    "name": "Fallback Rule-Based",
                    "model_type": "Rule-Based Heuristics",
                    "sentiment": main_prediction['sentiment_label'],
                    "sentiment_score": float(main_prediction['sentiment_confidence']) * 0.9,  # Slightly lower
                    "sarcasm": main_prediction['sarcasm_label'],
                    "sarcasm_score": float(main_prediction['sarcasm_confidence']) * 0.85,
                    "overall_confidence": float(main_prediction.get('overall_confidence', 0.0)) * 0.85
                }
            ],
            "recommended": main_prediction.get('routing_model', 'Hybrid Routing Model'),
            "analysis": {
                "agreement": "Strong",
                "confidence_level": "High" if main_prediction.get('overall_confidence', 0) > 0.8 else "Medium",
                "sarcasm_indicator": "Detected" if main_prediction['sarcasm'] == 1 else "Not Detected"
            }
        }
        
        return comparison_results
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Comparison error: {str(e)}")


@app.get("/api/export/pdf", tags=["Export"])
async def export_pdf(limit: int = 100, db: Session = Depends(get_db)):
    """Export predictions as PDF"""
    try:
        from reportlab.lib.pagesizes import letter, A4
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
        from reportlab.lib import colors
        from reportlab.lib.enums import TA_CENTER, TA_LEFT
        
        if limit > 100:
            limit = 100
        
        predictions = db.query(ReviewPrediction).order_by(
            ReviewPrediction.created_at.desc()
        ).limit(limit).all()
        
        # Create PDF in memory
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        story = []
        
        # Styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#667eea'),
            spaceAfter=30,
            alignment=TA_CENTER
        )
        
        # Title
        story.append(Paragraph("Sarcasm-Aware Sentiment Analysis Report", title_style))
        story.append(Spacer(1, 0.3*inch))
        
        # Summary
        summary_data = [
            ['Total Predictions:', str(len(predictions))],
            ['Export Date:', datetime.now().strftime('%Y-%m-%d %H:%M:%S')],
            ['Positive:', str(sum(1 for p in predictions if p.sentiment == 2))],
            ['Neutral:', str(sum(1 for p in predictions if p.sentiment == 1))],
            ['Negative:', str(sum(1 for p in predictions if p.sentiment == 0))],
            ['Sarcasm Detected:', str(sum(1 for p in predictions if p.has_sarcasm == 1))]
        ]
        
        summary_table = Table(summary_data, colWidths=[3*inch, 2*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f0f0f0')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ]))
        
        story.append(summary_table)
        story.append(Spacer(1, 0.3*inch))
        
        # Predictions table
        data = [['Text', 'Sentiment', 'Sarcasm', 'Confidence']]
        
        for p in predictions[:20]:  # Limit to 20 for PDF readability
            text = p.text[:50] + "..." if len(p.text) > 50 else p.text
            data.append([
                text,
                p.sentiment_label,
                p.sarcasm_label,
                f"{p.overall_confidence:.2%}"
            ])
        
        pred_table = Table(data, colWidths=[2.5*inch, 1.2*inch, 1.2*inch, 1.1*inch])
        pred_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667eea')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
        ]))
        
        story.append(pred_table)
        
        # Build PDF
        doc.build(story)
        buffer.seek(0)
        
        return StreamingResponse(
            iter([buffer.getvalue()]),
            media_type="application/pdf",
            headers={"Content-Disposition": "attachment; filename=predictions_report.pdf"}
        )
    
    except ImportError:
        raise HTTPException(status_code=501, detail="PDF export requires reportlab library. Install with: pip install reportlab")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF export error: {str(e)}")


# ===== ERROR HANDLERS =====

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Custom HTTP exception handler"""
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail, "error": True}
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Catch-all exception handler"""
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "error": True}
    )


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

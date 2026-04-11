"""
SQLAlchemy ORM Models for the application
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean, JSON
from sqlalchemy.sql import func
from .database import Base
from datetime import datetime


class ReviewPrediction(Base):
    """Model for storing prediction results"""
    __tablename__ = "review_predictions"
    
    id = Column(Integer, primary_key=True, index=True)
    text = Column(Text, nullable=False)
    
    # Sentiment prediction
    sentiment = Column(Integer, nullable=False)  # 0=negative, 1=neutral, 2=positive
    sentiment_label = Column(String(50), nullable=False)  # "Negative", "Neutral", "Positive"
    sentiment_confidence = Column(Float, nullable=False)
    
    # Sarcasm prediction
    has_sarcasm = Column(Integer, nullable=False)  # 0=no sarcasm, 1=sarcasm
    sarcasm_label = Column(String(50), nullable=False)  # "Sarcastic", "Not Sarcastic"
    sarcasm_confidence = Column(Float, nullable=False)
    
    # Emotions (JSON field)
    emotions = Column(JSON, nullable=True, default={})  # {"joy": 0.8, "sadness": 0.2, ...}
    
    # Overall
    final_interpretation = Column(String(100), nullable=True)
    explanation = Column(Text, nullable=True)
    overall_confidence = Column(Float, nullable=False)
    
    # Model info
    model_used = Column(String(100), nullable=False)  # Which model made the prediction
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<ReviewPrediction(id={self.id}, sentiment={self.sentiment_label}, sarcasm={self.sarcasm_label})>"


class User(Base):
    """Model for storing user accounts"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(120), unique=True, nullable=False, index=True)
    full_name = Column(String(120), nullable=True)
    
    # Security
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    
    # Preferences
    theme_preference = Column(String(10), default='light')  # light or dark
    notifications_enabled = Column(Boolean, default=True)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login = Column(DateTime(timezone=True), nullable=True)
    
    def __repr__(self):
        return f"<User(id={self.id}, username={self.username}, email={self.email})>"


class UserPrediction(Base):
    """Model for storing predictions linked to users"""
    __tablename__ = "user_predictions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)  # Foreign key to User
    prediction_id = Column(Integer, nullable=False)  # Foreign key to ReviewPrediction
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<UserPrediction(user_id={self.user_id}, prediction_id={self.prediction_id})>"


class UserFeedback(Base):
    """Model for storing user feedback on predictions"""
    __tablename__ = "user_feedback"
    
    id = Column(Integer, primary_key=True, index=True)
    prediction_id = Column(Integer, nullable=False)
    
    # Feedback
    sentiment_correct = Column(Boolean, nullable=True)  # Is sentiment prediction correct?
    sarcasm_correct = Column(Boolean, nullable=True)  # Is sarcasm prediction correct?
    
    # Comments
    comments = Column(Text, nullable=True)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<UserFeedback(id={self.id}, prediction_id={self.prediction_id})>"


class ModelStats(Base):
    """Model for storing overall model statistics"""
    __tablename__ = "model_stats"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # timestamps
    date = Column(DateTime(timezone=True), server_default=func.now())
    
    # Metrics
    total_predictions = Column(Integer, default=0)
    sentiment_accuracy = Column(Float, nullable=True)
    sarcasm_accuracy = Column(Float, nullable=True)
    avg_inference_time_ms = Column(Float, nullable=True)
    
    # Sarcasm distribution
    sarcasm_detected_count = Column(Integer, default=0)
    non_sarcasm_count = Column(Integer, default=0)
    
    # Sentiment distribution
    positive_count = Column(Integer, default=0)
    neutral_count = Column(Integer, default=0)
    negative_count = Column(Integer, default=0)
    
    def __repr__(self):
        return f"<ModelStats(id={self.id}, date={self.date}, total_predictions={self.total_predictions})>"

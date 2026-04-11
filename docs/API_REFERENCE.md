# API Reference

Complete documentation of all FastAPI endpoints for the Sarcasm-Aware Sentiment Analysis System.

## Base URL

```
http://localhost:8000
```

## Authentication

Currently, no authentication is required for development. For production deployment, add API keys as needed.

---

## Endpoints

### 1. Health Check

Check if the API server is running and models are loaded.

```
GET /api/health
```

**Response (200 OK):**
```json
{
  "status": "ok",
  "models_loaded": true
}
```

**Response (200 OK - Fallback Mode):**
```json
{
  "status": "ok",
  "models_loaded": false,
  "message": "Models not found. Using fallback rule-based classifier."
}
```

**Example:**
```bash
curl http://localhost:8000/api/health
```

---

### 2. Single Prediction

Get sentiment and sarcasm prediction for a single review.

```
POST /api/predict
```

**Request Headers:**
```
Content-Type: application/json
```

**Request Body:**
```json
{
  "text": "This product is absolutely amazing... said no one ever!"
}
```

**Response (200 OK):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
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

**Sentiment Values:**
- `"positive"` - Positive sentiment
- `"negative"` - Negative sentiment
- `"neutral"` - Neutral sentiment

**Confidence Scores:**
- Range: 0.0 to 1.0
- Higher = more confident
- `confidence` = Average of sentiment and sarcasm confidence

**Model Used (Routing):**
- `"logistic_regression"` - LR model (no sarcasm)
- `"svm"` - SVM model (no sarcasm)
- `"lstm"` - LSTM model (no sarcasm)
- `"bert"` - BERT model
- `"roberta"` - RoBERTa model (sarcasm)
- `"hybrid_two_stage"` - Combined routing
- `"fallback_rule_based"` - Using fallback classifier

**Validation Errors (400):**
```json
{
  "detail": "Text is required and cannot be empty"
}
```

**Example:**
```bash
curl -X POST http://localhost:8000/api/predict \
  -H "Content-Type: application/json" \
  -d '{"text": "This product exceeded my expectations!"}'
```

---

### 3. Batch Predictions

Process multiple reviews at once (max 100 per request).

```
POST /api/batch-predict
```

**Request Body:**
```json
{
  "texts": [
    "Great product!",
    "Absolutely terrible, just perfect!",
    "Average quality product"
  ]
}
```

**Response (200 OK):**
```json
{
  "count": 3,
  "processed": 3,
  "failed": 0,
  "predictions": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "text": "Great product!",
      "sentiment": "positive",
      "sentiment_confidence": 0.95,
      "sarcasm": false,
      "sarcasm_confidence": 0.08,
      "confidence": 0.51
    },
    {
      "id": "550e8400-e29b-41d4-a716-446655440001",
      "text": "Absolutely terrible, just perfect!",
      "sentiment": "negative",
      "sentiment_confidence": 0.89,
      "sarcasm": true,
      "sarcasm_confidence": 0.91,
      "confidence": 0.90
    },
    {
      "id": "550e8400-e29b-41d4-a716-446655440002",
      "text": "Average quality product",
      "sentiment": "neutral",
      "sentiment_confidence": 0.82,
      "sarcasm": false,
      "sarcasm_confidence": 0.05,
      "confidence": 0.43
    }
  ]
}
```

**Validation Errors (400):**
```json
{
  "detail": "Maximum 100 reviews allowed per request"
}
```

**Example:**
```bash
curl -X POST http://localhost:8000/api/batch-predict \
  -H "Content-Type: application/json" \
  -d '{
    "texts": [
      "Great product!",
      "Terrible!",
      "Not bad"
    ]
  }'
```

---

### 4. Prediction History

Retrieve past predictions with pagination.

```
GET /api/history?limit=50
```

**Query Parameters:**
- `limit` (optional, default: 50, max: 1000) - Number of records to return

**Response (200 OK):**
```json
{
  "count": 50,
  "limit": 50,
  "total": 1250,
  "predictions": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "text": "This product exceeded my expectations!",
      "sentiment": "positive",
      "sentiment_confidence": 0.95,
      "sarcasm": false,
      "sarcasm_confidence": 0.08,
      "confidence": 0.51,
      "model_used": "logistic_regression",
      "created_at": "2024-01-15T10:30:45.123Z"
    }
    // ... more predictions
  ]
}
```

**Example:**
```bash
curl "http://localhost:8000/api/history?limit=100"
```

---

### 5. Aggregate Statistics

Get system-wide statistics and aggregated metrics.

```
GET /api/stats
```

**Response (200 OK):**
```json
{
  "total_predictions": 1250,
  "positive_count": 450,
  "negative_count": 550,
  "neutral_count": 250,
  "sarcasm_detected": 320,
  "sarcasm_percentage": 25.6,
  "positive_percentage": 36.0,
  "negative_percentage": 44.0,
  "neutral_percentage": 20.0,
  "average_confidence": 0.88,
  "models_used": {
    "logistic_regression": 320,
    "roberta": 450,
    "bert": 480
  }
}
```

**Example:**
```bash
curl http://localhost:8000/api/stats
```

---

### 6. Submit Feedback

Provide feedback on predictions to improve model accuracy.

```
POST /api/feedback
```

**Request Body:**
```json
{
  "prediction_id": "550e8400-e29b-41d4-a716-446655440000",
  "sentiment_correct": true,
  "sarcasm_correct": false,
  "comments": "Model got sentiment right but missed the sarcasm"
}
```

**Response (200 OK):**
```json
{
  "message": "Feedback recorded successfully",
  "prediction_id": "550e8400-e29b-41d4-a716-446655440000",
  "feedback_id": "f123456789"
}
```

**Validation Errors (400):**
```json
{
  "detail": "Invalid prediction ID"
}
```

**Example:**
```bash
curl -X POST http://localhost:8000/api/feedback \
  -H "Content-Type: application/json" \
  -d '{
    "prediction_id": "550e8400-e29b-41d4-a716-446655440000",
    "sentiment_correct": true,
    "sarcasm_correct": true,
    "comments": "Perfect prediction!"
  }'
```

---

### 7. API Documentation

FastAPI automatically generates interactive API documentation.

```
GET /docs
```

Opens Swagger UI with interactive endpoint testing:
- Try out API endpoints directly
- See request/response schemas
- View parameter descriptions

```
GET /redoc
```

Opens ReDoc with detailed API documentation:
- Read-only documentation
- Beautiful formatted reference

---

## Error Responses

### 400 Bad Request

```json
{
  "detail": "Invalid request format"
}
```

### 404 Not Found

```json
{
  "detail": "Resource not found"
}
```

### 422 Unprocessable Entity

```json
{
  "detail": [
    {
      "loc": ["body", "text"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

### 500 Internal Server Error

```json
{
  "detail": "Internal server error. Please try again."
}
```

---

## Rate Limiting

Currently not implemented. For production, add rate limiting:

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/api/predict")
@limiter.limit("30/minute")
async def predict(request: Request):
    ...
```

---

## Data Types

### Sentiment
- `positive` - Positive sentiment detected
- `negative` - Negative sentiment detected
- `neutral` - Neutral sentiment (neither positive nor negative)

### Confidence
Float between 0.0 and 1.0:
- 0.0 - 0.4: Low confidence
- 0.4 - 0.7: Medium confidence
- 0.7 - 1.0: High confidence

### Timestamp Format
ISO 8601 format: `2024-01-15T10:30:45.123Z`

---

## Status Codes

| Code | Meaning |
|------|---------|
| 200 | OK - Request successful |
| 400 | Bad Request - Invalid input |
| 404 | Not Found - Resource doesn't exist |
| 422 | Unprocessable Entity - Validation error |
| 500 | Internal Server Error |

---

## Code Examples

### Python (Requests)

```python
import requests
import json

API_URL = "http://localhost:8000"

# Single prediction
response = requests.post(
    f"{API_URL}/api/predict",
    json={"text": "This product is amazing!"}
)
result = response.json()
print(f"Sentiment: {result['sentiment']}")
print(f"Sarcasm: {result['sarcasm']}")

# Batch predictions
response = requests.post(
    f"{API_URL}/api/batch-predict",
    json={
        "texts": [
            "Great product!",
            "Terrible quality",
            "Not bad"
        ]
    }
)
results = response.json()
print(f"Processed: {results['count']} reviews")

# Get history
response = requests.get(f"{API_URL}/api/history?limit=100")
history = response.json()
print(f"Total predictions: {history['total']}")

# Get stats
response = requests.get(f"{API_URL}/api/stats")
stats = response.json()
print(f"Sarcasm rate: {stats['sarcasm_percentage']}%")
```

### JavaScript (Fetch API)

```javascript
const API_URL = "http://localhost:8000";

// Single prediction
const response = await fetch(`${API_URL}/api/predict`, {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ text: "This product is amazing!" })
});
const result = await response.json();
console.log(`Sentiment: ${result.sentiment}`);
console.log(`Sarcasm: ${result.sarcasm}`);

// Get stats
const statsResponse = await fetch(`${API_URL}/api/stats`);
const stats = await statsResponse.json();
console.log(`Total predictions: ${stats.total_predictions}`);
```

### cURL

```bash
# Single prediction
curl -X POST http://localhost:8000/api/predict \
  -H "Content-Type: application/json" \
  -d '{"text": "This is awesome!"}'

# Batch prediction
curl -X POST http://localhost:8000/api/batch-predict \
  -H "Content-Type: application/json" \
  -d '{
    "texts": ["Great!", "Terrible", "Okay"]
  }'

# Get history
curl "http://localhost:8000/api/history?limit=50"

# Get stats
curl http://localhost:8000/api/stats

# Submit feedback
curl -X POST http://localhost:8000/api/feedback \
  -H "Content-Type: application/json" \
  -d '{
    "prediction_id": "550e8400-e29b-41d4-a716-446655440000",
    "sentiment_correct": true,
    "sarcasm_correct": true
  }'
```

---

## Web UI

The React frontend provides a user-friendly interface:

- **Home Page:** Single review prediction
- **History Page:** View past predictions
- **Analytics Page:** View statistics and charts
- **Batch Predict Page:** Bulk processing with CSV export

Access at: `http://localhost:3000`

---

## Best Practices

1. **Input Validation:** Always validate input before sending
2. **Error Handling:** Handle all HTTP error codes gracefully
3. **Batch Requests:** Use batch endpoint for multiple reviews (more efficient)
4. **Feedback:** Submit feedback to improve model accuracy
5. **Caching:** Cache responses to reduce API calls
6. **Rate Limiting:** Implement client-side rate limiting

---

## Support

For issues:
1. Check API documentation: http://localhost:8000/docs
2. Review error response messages
3. Check server logs for detailed errors
4. Verify backend server is running
5. Test with simple reviews first

---

**Last Updated:** 2024
**API Version:** 1.0.0
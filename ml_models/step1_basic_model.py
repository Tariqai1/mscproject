print("HELLO WORLD")
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.feature_extraction.text import CountVectorizer

print("Program Started...")

# Step 1: Dummy dataset
data = {
    "text": [
        "This product is amazing",
        "Very bad quality",
        "I love this",
        "Worst experience ever",
        "Not good",
        "Excellent product",
        "Terrible service",
        "I am happy",
        "Very disappointing",
        "Superb quality"
    ],
    "label": [1, 0, 1, 0, 0, 1, 0, 1, 0, 1]
}

df = pd.DataFrame(data)

# Step 2: Features and labels
X = df["text"]
y = df["label"]

# Step 3: Train-test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

# Step 4: Convert text → numbers
vectorizer = CountVectorizer()
X_train_vec = vectorizer.fit_transform(X_train)

# Step 5: Train model
model = LogisticRegression()
model.fit(X_train_vec, y_train)

print("Model trained successfully!")

# Step 6: Test
test_text = ["This product is awesome"]
test_vec = vectorizer.transform(test_text)

prediction = model.predict(test_vec)

print("Prediction raw:", prediction)

# Output
if prediction[0] == 1:
    print("Sentiment: Positive 😊")
else:
    print("Sentiment: Negative 😡")
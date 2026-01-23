import pandas as pd
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report

# Load dataset
df = pd.read_csv("data/phishing_email.csv")

# Explicit column mapping (based on your CSV)
X = df["text_combined"]
y = df["label"]

# Vectorization
vectorizer = TfidfVectorizer(
    stop_words="english",
    max_features=3000
)

X_vec = vectorizer.fit_transform(X)

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(
    X_vec, y, test_size=0.2, random_state=42
)

# Train model
model = LogisticRegression(max_iter=1000)
model.fit(X_train, y_train)

# Evaluate
y_pred = model.predict(X_test)

print("✅ Accuracy:", accuracy_score(y_test, y_pred))
print("\n📊 Classification Report:\n")
print(classification_report(y_test, y_pred))

# Save model
pickle.dump(model, open("ml/model.pkl", "wb"))
pickle.dump(vectorizer, open("ml/vectorizer.pkl", "wb"))

print("💾 Model & vectorizer saved successfully")
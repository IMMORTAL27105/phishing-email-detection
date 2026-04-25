import pandas as pd
import pickle

from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report


# LOAD DATASETS
kaggle_df = pd.read_csv("data/phishing_email.csv")
enron_df = pd.read_csv("data/emails.csv")

# PREPARE DATA

#kaggle dataset uses "text_combined"
kaggle_df["text"] = kaggle_df["text_combined"]
# enron dataset uses "message"
enron_df["text"] = enron_df["message"]

# Labels
kaggle_df["label"] = 1
enron_df["label"] = 0

# Combine
df = pd.concat([kaggle_df, enron_df], ignore_index=True)

# Remove nulls
df = df.dropna(subset=["text"])

# Shuffle
df = df.sample(frac=1, random_state=42)

X = df["text"]
y = df["label"]


# TRAIN TEST SPLIT
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# VECTORIZATION
vectorizer = TfidfVectorizer(
    stop_words="english",
    max_features=5000,
    ngram_range=(1, 2)
)
X_train_vec = vectorizer.fit_transform(X_train)
X_test_vec = vectorizer.transform(X_test)


# MODEL TRAINING
model = LogisticRegression(max_iter=1000)
model.fit(X_train_vec, y_train)

# EVALUATION
y_pred = model.predict(X_test_vec)
print("=== MODEL PERFORMANCE ===")
print(classification_report(y_test, y_pred))


# SAVE MODEL
pickle.dump(model, open("ml/model.pkl", "wb"))
pickle.dump(vectorizer, open("ml/vectorizer.pkl", "wb"))

print("\n✅ Model and vectorizer saved in /ml folder")
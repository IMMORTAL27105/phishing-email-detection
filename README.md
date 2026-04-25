# Phishing Email Detection – Setup & Run Guide

This repository contains a **machine-learning based phishing email detection prototype** with:

* a Python backend (FastAPI + ML model)
* a Chrome extension for Gmail

Follow the steps below to set up and run the project locally.



## 1. Prerequisites

Ensure the following are installed on your system:

* Python **3.8 or above**
* Google Chrome browser
* Git



## 2. Clone the Repository

```bash
git clone https://github.com/IMMORTAL27105/phishing-email-detection.git
cd phishing-email-detection
```



## 3. Backend Setup (Python)

### 3.1 Create Virtual Environment (Recommended)

```bash
python -m venv venv
```

Activate it:

* **Windows**

  ```bash
  venv\Scripts\activate
  ```
* **macOS / Linux**

  ```bash
  source venv/bin/activate
  ```



### 3.2 Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```


### 3.3 Add Dataset

The dataset is **not included** in the repository.

1. Download a phishing email dataset (CSV format), here we used kaggle phishing email dataset and enron dataset.

2. Place it in:

   ```
   backend/data/
   ```

Example:

```
backend/data/phishing_email.csv
```



### 3.4 Train the Model

```bash
python train.py
```

This will generate:

```
backend/ml/model.pkl
backend/ml/vectorizer.pkl
```



### 3.5 Run the Backend Server

```bash
uvicorn app:app --reload
```

Keep this terminal **running**.

Backend will be available at:

```
http://127.0.0.1:8000
```



## 4. Chrome Extension Setup (Gmail)

### 4.1 Open Chrome Extensions Page

Open in Chrome:

```
chrome://extensions/
```

Enable **Developer Mode** (top-right).


### 4.2 Load the Extension

1. Click **Load unpacked**
2. Select the `extension/` folder from this repository


### 4.3 Open Gmail

Go to:

```
https://mail.google.com
```

The extension will automatically run on Gmail.


## 5. How to Verify It Is Working

* Ensure the backend server is running
* Open Gmail
* Open Chrome DevTools → Console
* You should see logs from `content.js`
* Backend terminal should receive requests when Gmail is opened


## 6. Notes

* This is an **academic prototype**
* The system provides **risk indication only**, not definitive classification
* Legitimate emails may occasionally be flagged


## 7. Common Issues

* **Backend not running** → Extension will not receive results
* **Dataset missing** → Model training will fail
* **Wrong folder loaded** → Extension will not run

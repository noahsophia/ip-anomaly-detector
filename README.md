# 🌍 IP Anomaly Detector

An ML-powered tool for detecting suspicious logins using IP geolocation and travel speed analysis.

## 🚀 Overview

This project demonstrate the combination IP geolocation data from IP2Location.io with machine learning anomaly detection to flag suspicious login activities.
It helps detect impossible travel logins (e.g., user logs in from Malaysia and then from Europe within an hour) and visualizes login locations on a world map.

## ✨ Features

- 🌐 Enrich login records with IP geolocation (via IP2Location.io API).

- 🧮 Calculate travel distance & velocity between consecutive logins.

- 🤖 Detect anomalies using Isolation Forest (ML).

- 📍 Flag logins that exceed realistic travel speeds.

- 🗺️ Visualize login activity on a world map overlay with suspicious logins marked in red.


## 📦 Requirements

Install dependencies with:

```bash
pip install -r requirements.txt
```

**requirements.txt**

```
pandas
scikit-learn
geopy
requests
matplotlib
cartopy
```

## ⚙️ Usage

1. Prepare your dataset

Update the script with your dataset.

Example login history with IP addresses:

```python
raw_logins = [
    {"user_id": "1234", "timestamp": "2025-09-10T08:30:00", "ip": "8.8.8.8"},
    {"user_id": "1234", "timestamp": "2025-09-11T09:00:00", "ip": "202.188.0.133"},
    {"user_id": "1234", "timestamp": "2025-09-11T11:00:00", "ip": "91.198.174.192"},  # sudden Europe login
]
```

2. Run the script

```bash
python main.py
```

## 🔑 Setup API Key

Sign up at IP2Location.io and get a free API key.
Replace it in the script:

```python
API_KEY = "YOUR_API_KEY"
```

## 📜 License

MIT License. Free for personal and commercial use.

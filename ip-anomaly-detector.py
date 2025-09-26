import requests
import pandas as pd
from sklearn.ensemble import IsolationForest
from geopy.distance import geodesic
from datetime import datetime
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature

# ==========================
# 1. Get Geolocation from IP2Location.io
# ==========================
def get_ip_geolocation(ip, api_key="YOUR_API_KEY"):
    url = f"https://api.ip2location.io/?key={api_key}&ip={ip}"
    resp = requests.get(url)

    if resp.status_code == 200:
        data = resp.json()
        return {
            "ip": data.get("ip", ""),
            "country": data.get("country_name", ""),
            "region": data.get("region_name", ""),
            "city": data.get("city_name", ""),
            "lat": float(data.get("latitude", 0)),
            "lon": float(data.get("longitude", 0)),
            "timezone": data.get("time_zone", ""),
            "asn": data.get("asn", ""),
            "isp": data.get("as", "")
        }
    else:
        return None

# ==========================
# 2. Feature Engineering
# ==========================
def build_features(logins):
    enriched = []
    last_location, last_time = None, None

    for login in logins:
        ts = datetime.fromisoformat(login["timestamp"])
        entry = login.copy()
        entry["hour"] = ts.hour
        entry["weekday"] = ts.weekday()

        # distance & velocity calc
        if last_location:
            dist = geodesic((entry["lat"], entry["lon"]), last_location).km
            time_diff = (ts - last_time).total_seconds() / 3600.0
            velocity = dist / time_diff if time_diff > 0 else 0
        else:
            dist, velocity = 0, 0

        entry["distance_km"] = dist
        entry["velocity_kmh"] = velocity

        enriched.append(entry)
        last_location = (entry["lat"], entry["lon"])
        last_time = ts

    return pd.DataFrame(enriched)

# ==========================
# 3. Train & Detect Anomalies
# ==========================
def train_and_detect(features_df):
    X = features_df[["hour", "weekday", "distance_km", "velocity_kmh"]]
    model = IsolationForest(contamination=0.2, random_state=42)
    model.fit(X)
    preds = model.predict(X)  # -1 = anomaly
    features_df["is_suspicious"] = preds == -1
    return features_df

# ==========================
# 4. Visualization (Cartopy World Map)
# ==========================
def plot_logins_worldmap(features_df, title="Login Locations on World Map"):
    plt.figure(figsize=(12, 6))
    ax = plt.axes(projection=ccrs.PlateCarree())

    # Base map
    ax.add_feature(cfeature.COASTLINE)
    ax.add_feature(cfeature.BORDERS, linestyle=":")
    ax.add_feature(cfeature.LAND, facecolor="lightgray")
    ax.add_feature(cfeature.OCEAN, facecolor="lightblue")

    normal = features_df[~features_df["is_suspicious"]]
    anomalies = features_df[features_df["is_suspicious"]]

    ax.scatter(normal["lon"], normal["lat"], transform=ccrs.PlateCarree(),
               label="Normal", s=60, alpha=0.7, c="blue")
    ax.scatter(anomalies["lon"], anomalies["lat"], transform=ccrs.PlateCarree(),
               marker="x", s=120, label="Suspicious", alpha=0.9, c="red")

    # annotate
    for _, r in features_df.iterrows():
        label = f"{r['city'] or r['ip']}"
        ax.text(r["lon"] + 1, r["lat"] + 1, label,
                transform=ccrs.PlateCarree(), fontsize=8)

    plt.title(title)
    plt.legend()
    plt.show()

# ==========================
# 5. Example Run
# ==========================
if __name__ == "__main__":
    API_KEY = "YOUR_API_KEY"

    # Initial example dataset
    raw_logins = [
        {"user_id": "1234", "timestamp": "2025-09-10T08:30:00", "ip": "8.8.8.8"},
        {"user_id": "1234", "timestamp": "2025-09-11T09:00:00", "ip": "202.188.0.133"},
        {"user_id": "1234", "timestamp": "2025-09-11T11:00:00", "ip": "91.198.174.192"},  # sudden Europe login
    ]

    # Add extra test records
    extra_ips = [
        "1.1.1.1",       # Cloudflare (Australia/US)
        "23.236.62.147", # US
        "175.139.142.25",# Malaysia
        "81.2.69.142",   # UK
        "104.244.42.1",  # US (Twitter)
        "139.130.4.5",   # Australia
        "118.189.187.43" # Singapore
    ]
    for i, ip in enumerate(extra_ips):
        raw_logins.append({
            "user_id": "1234",
            "timestamp": f"2025-09-12T{8 + (i % 8):02d}:00:00",
            "ip": ip
        })

    # Enrich with IP geolocation
    enriched = []
    for login in raw_logins:
        geo = get_ip_geolocation(login["ip"], API_KEY)
        if geo:
            enriched.append({**login, **geo})

    # Build features
    features = build_features(enriched)

    # Train model & detect suspicious
    results = train_and_detect(features)

    # Show table
    print(results[["ip", "city", "country", "hour", "distance_km", "velocity_kmh", "is_suspicious"]])

    # Plot on world map
    plot_logins_worldmap(results)

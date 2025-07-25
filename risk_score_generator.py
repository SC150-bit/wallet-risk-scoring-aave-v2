import pandas as pd
import requests
import time

# === Configuration ===
COVALENT_API_KEY = "cqt_rQH74FvCg86CRy7FXCK4dRhhKH4J"
CHAIN_ID = 1  # Ethereum mainnet
INPUT_EXCEL_FILE = "Wallet id.xlsx"
OUTPUT_CSV_FILE = "wallet_scores.csv"

# === Fetch wallet transaction data ===
def fetch_transaction_count(wallet):
    url = f"https://api.covalenthq.com/v1/{CHAIN_ID}/address/{wallet}/transactions_v2/"
    params = {"key": COVALENT_API_KEY}
    response = requests.get(url, params=params)
    if response.status_code != 200:
        print(f"❌ API error for wallet {wallet}: {response.status_code}")
        return 0, 0

    data = response.json()
    items = data.get("data", {}).get("items", [])

    tx_count = len(items)
    total_value = sum(float(tx.get("value", 0)) / 1e18 for tx in items if tx.get("value"))
    avg_tx_amount = total_value / tx_count if tx_count > 0 else 0

    return tx_count, avg_tx_amount

# === Extract features per wallet ===
def extract_features(wallet):
    try:
        tx_count, avg_tx_amount = fetch_transaction_count(wallet)
        active_days = min(365, tx_count // 3)
        return {
            "tx_count": tx_count,
            "avg_tx_amount": avg_tx_amount,
            "active_days": active_days,
            "default_rate": 0.1,
            "deposit_volume": avg_tx_amount * tx_count * 0.5,
            "borrow_volume": avg_tx_amount * tx_count * 0.3
        }
    except Exception as e:
        print(f"⚠️ Error processing wallet {wallet}: {e}")
        return {
            "tx_count": 0,
            "avg_tx_amount": 0,
            "active_days": 0,
            "default_rate": 0.2,
            "deposit_volume": 0,
            "borrow_volume": 0
        }

# === Scoring logic ===
def normalize(value, min_val, max_val):
    return (value - min_val) / (max_val - min_val) if max_val != min_val else 0

def score_wallet(features):
    tx_score = normalize(features["tx_count"], 0, 500) * 200
    amount_score = normalize(features["avg_tx_amount"], 0, 2000) * 200
    active_score = normalize(features["active_days"], 0, 365) * 150
    borrow_score = normalize(features["borrow_volume"], 0, 30000) * 200
    deposit_score = normalize(features["deposit_volume"], 0, 50000) * 200
    risk_penalty = (1 - features["default_rate"]) * 50

    total_score = tx_score + amount_score + active_score + borrow_score + deposit_score + risk_penalty
    return round(min(max(total_score, 0), 1000), 2)

# === Main pipeline ===
def generate_scores():
    df = pd.read_excel(INPUT_EXCEL_FILE, sheet_name=0)

    # Automatically detect and rename column if needed
    for col in df.columns:
        if "wallet" in col.lower():
            df.rename(columns={col: "wallet_id"}, inplace=True)
            break

    scores = []
    for idx, wallet in enumerate(df["wallet_id"]):
        print(f"🔄 Processing ({idx+1}/{len(df)}): {wallet}")
        features = extract_features(wallet)
        score = score_wallet(features)
        scores.append({"wallet_id": wallet, "score": score})
        time.sleep(0.5)  # Protect API limits

    pd.DataFrame(scores).to_csv(OUTPUT_CSV_FILE, index=False)
    print(f"\n✅ Risk scores saved to '{OUTPUT_CSV_FILE}'.")

if __name__ == "__main__":
    generate_scores()

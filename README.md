# Wallet Risk Scoring – Aave V2 / Compound V2 Round 2

This project computes a credit/risk score (0–1000) for DeFi wallets based on real on-chain activity using the Covalent API. It processes a list of wallet addresses, extracts behavioral features, and generates a final score reflecting a wallet's trustworthiness and financial responsibility.

---

## 📊 Data Collection

Wallet transaction data is collected in real-time from the Ethereum Mainnet using the [Covalent API](https://www.covalenthq.com/). Each wallet’s historical activity is pulled via:

- `/transactions_v2/` endpoint  
- Metrics such as transaction count and average transaction amount are calculated.
- API key (free tier) is used to avoid rate limits and handle authentication.

Input file: `Wallet id.xlsx`  
Output: `wallet_scores.csv`

---

## 🧠 Feature Selection Rationale

The features extracted per wallet are:

| Feature            | Description                                         | Rationale                                  |
|--------------------|-----------------------------------------------------|--------------------------------------------|
| `tx_count`         | Number of total transactions                        | More transactions = higher activity        |
| `avg_tx_amount`    | Average ETH value per transaction                   | High average implies larger value users    |
| `active_days`      | Approximated from tx count (tx_count // 3)          | Measures consistent usage over time        |
| `deposit_volume`   | Estimated based on avg_tx × tx × 0.5                | Proxy for funds provided to protocols      |
| `borrow_volume`    | Estimated based on avg_tx × tx × 0.3                | Proxy for protocol debt taken              |
| `default_rate`     | Assumed static (0.1)                                | Placeholder for future protocol-level data |

These features give a good balance of **volume**, **engagement**, and **behavioral intent**.

---

## 🧮 Scoring Method

The scoring formula uses **weighted normalized values** of all features. Each feature contributes positively or negatively to the final score (max 1000):

```
Score = 
    + 200 × normalized(tx_count)
    + 200 × normalized(avg_tx_amount)
    + 150 × normalized(active_days)
    + 200 × normalized(deposit_volume)
    + 200 × normalized(borrow_volume)
    + 50  × (1 - default_rate)
```

The result is then clamped to the range [0, 1000] and saved as a rounded integer.

---

## ⚖️ Justification of Risk Indicators

- **High deposit volume** and **repayment behavior** signal **financial responsibility**.
- **Active wallets** with frequent, consistent usage are **less likely to be malicious** or dormant.
- **High borrowing volume** increases risk, but also reflects credit demand — so it’s balanced with other features.
- **Default rate** (once integrated with protocol data) will penalize risky repayment histories.

This scoring strategy aims to emulate a **credit-like risk profile**, applicable in decentralized finance scenarios.

---

## ✅ Output

The script produces:
- `wallet_scores.csv`: Contains wallet IDs and scores.
- Ready to be used for ranking, risk segmentation, or visualization.

---

## 🛠️ To Run

```bash
pip install pandas requests openpyxl
python risk_score_generator.py
```

---

```
Developed for Risk Scoring Round 2 - Aave / Compound Protocols
```
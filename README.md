# Virtus Dashboard MVP

A Streamlit dashboard that turns Uber Eats, DoorDash, and Grubhub CSV exports into a unified financial intelligence dashboard for restaurant operators.

## What it does

- Upload multiple delivery-platform CSVs
- Auto-detect Uber Eats, DoorDash, and Grubhub reports
- Normalize orders into one table
- Calculate gross sales, net payout, fees, commissions, promos, ad spend, AOV, deposit %, and net margin
- Show platform performance comparison
- Show recent order-level payout breakdowns
- Surface simple financial leak alerts

## Local run

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Deploy to Streamlit Cloud

1. Create a GitHub repo.
2. Upload `app.py`, `requirements.txt`, and the `.streamlit` folder.
3. Go to Streamlit Community Cloud.
4. Click **New app**.
5. Select your repo and set the main file as `app.py`.
6. Deploy.

Do not upload private restaurant CSVs to GitHub. Use the app uploader after the app is deployed.

## Deploy to Render

Build command:

```bash
pip install -r requirements.txt
```

Start command:

```bash
streamlit run app.py --server.port $PORT --server.address 0.0.0.0
```

## Important note

This dashboard calculates delivery-platform financial performance and estimated net payout margin. It does not calculate true restaurant profit until you add COGS, labor, packaging, rent allocation, and other operating costs.

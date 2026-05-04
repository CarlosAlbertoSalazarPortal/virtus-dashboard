import io
import re
from datetime import date, timedelta

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title="Virtus | Delivery Financial Intelligence", page_icon="V", layout="wide")

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');
html, body, [class*="css"] {font-family: 'Inter', sans-serif;}
.block-container{padding-top:1.25rem; padding-bottom:2.5rem; max-width:1320px;}
[data-testid="stAppViewContainer"]{background:radial-gradient(circle at 20% -10%, rgba(59,130,246,.18), transparent 30%), #050814;}
[data-testid="stSidebar"]{background:#070b16;border-right:1px solid rgba(148,163,184,.14);}
[data-testid="stSidebar"] *{font-family:'Inter',sans-serif;}
hr{border-color:rgba(148,163,184,.15)!important;}
.virtus-topbar{display:flex;align-items:center;justify-content:space-between;margin-bottom:14px;color:#94a3b8;font-size:.88rem;}
.virtus-brand{font-weight:900;color:#f8fafc;font-size:1.1rem;letter-spacing:-.03em;}
.virtus-pill{display:inline-flex;align-items:center;gap:8px;border:1px solid rgba(59,130,246,.35);background:rgba(37,99,235,.14);color:#bfdbfe;border-radius:999px;padding:7px 11px;font-size:.78rem;font-weight:800;text-transform:uppercase;letter-spacing:.07em;}
.virtus-hero{padding:30px 32px;border:1px solid rgba(148,163,184,.22);border-radius:28px;background:linear-gradient(135deg,#0f172a 0%,#0b1224 48%,#172554 100%);box-shadow:0 28px 90px rgba(0,0,0,.28);margin-bottom:18px;position:relative;overflow:hidden;}
.virtus-hero:after{content:"";position:absolute;right:-120px;top:-130px;width:340px;height:340px;border-radius:999px;background:rgba(96,165,250,.18);filter:blur(10px);}
.virtus-eyebrow{color:#93c5fd;font-weight:800;letter-spacing:.1em;text-transform:uppercase;font-size:.76rem;margin-bottom:.6rem;}
.virtus-title{font-size:2.65rem;line-height:1.04;font-weight:900;color:#f8fafc;margin-bottom:.7rem;letter-spacing:-.055em;max-width:930px;}
.virtus-subtitle{font-size:1.05rem;color:#cbd5e1;max-width:920px;line-height:1.65;}
.hero-grid{display:grid;grid-template-columns:1.35fr .65fr;gap:18px;margin-bottom:18px;}
.hero-metric{border:1px solid rgba(34,197,94,.30);border-radius:28px;padding:26px;background:linear-gradient(135deg,rgba(15,23,42,.98),rgba(6,78,59,.38));box-shadow:0 20px 70px rgba(0,0,0,.22);min-height:180px;}
.hero-label{color:#a7f3d0;text-transform:uppercase;letter-spacing:.08em;font-size:.8rem;font-weight:900;}
.hero-value{color:#f8fafc;font-weight:950;font-size:3.55rem;line-height:1;margin-top:12px;letter-spacing:-.06em;}
.hero-context{color:#cbd5e1;margin-top:12px;font-size:.98rem;}
.leak-card{border:1px solid rgba(251,113,133,.26);border-radius:28px;padding:24px;background:linear-gradient(135deg,rgba(15,23,42,.98),rgba(127,29,29,.34));min-height:180px;}
.leak-value{font-size:2.35rem;font-weight:950;color:#fb7185;margin-top:14px;letter-spacing:-.05em;}
.kpi-card{border:1px solid rgba(148,163,184,.18);border-radius:24px;padding:18px 18px;background:rgba(15,23,42,.72);box-shadow:0 12px 42px rgba(0,0,0,.16);min-height:132px;}
.kpi-card:hover{border-color:rgba(96,165,250,.35);}
.kpi-label{color:#94a3b8;font-size:.76rem;font-weight:900;text-transform:uppercase;letter-spacing:.07em;}
.kpi-value{font-size:1.75rem;font-weight:900;color:#f8fafc;margin-top:10px;letter-spacing:-.04em;}
.kpi-help{color:#a7f3d0;font-size:.84rem;margin-top:8px;}
.section-title{font-size:1.23rem;font-weight:900;color:#f8fafc;margin:10px 0 10px;letter-spacing:-.035em;}
.panel{border:1px solid rgba(148,163,184,.16);border-radius:24px;background:rgba(15,23,42,.62);padding:18px;margin-bottom:16px;}
.warning-card{border:1px solid rgba(251,191,36,.30);border-radius:18px;background:rgba(120,53,15,.25);padding:14px 16px;color:#fde68a;margin-bottom:10px;}
.danger-card{border:1px solid rgba(248,113,113,.32);border-radius:18px;background:rgba(127,29,29,.24);padding:14px 16px;color:#fecaca;margin-bottom:10px;}
.good-card{border:1px solid rgba(34,197,94,.32);border-radius:18px;background:rgba(20,83,45,.23);padding:14px 16px;color:#bbf7d0;margin-bottom:10px;}
.info-card{border:1px solid rgba(96,165,250,.28);border-radius:18px;background:rgba(30,64,175,.18);padding:14px 16px;color:#bfdbfe;margin-bottom:10px;}
.small-muted{color:#94a3b8;font-size:.88rem;line-height:1.55;}
.order-box{border:1px solid rgba(148,163,184,.2);border-radius:22px;background:rgba(2,6,23,.48);padding:18px;}
.breakdown-row{display:flex;justify-content:space-between;border-bottom:1px solid rgba(148,163,184,.12);padding:9px 0;color:#cbd5e1;}
.breakdown-row strong{color:#f8fafc;}
.net-row{display:flex;justify-content:space-between;padding-top:14px;margin-top:6px;color:#f8fafc;font-size:1.25rem;font-weight:900;}
.badge{display:inline-flex;border-radius:999px;padding:5px 9px;font-size:.76rem;font-weight:800;background:rgba(59,130,246,.15);color:#bfdbfe;border:1px solid rgba(59,130,246,.24);}
[data-testid="stMetric"]{background:rgba(15,23,42,.62);border:1px solid rgba(148,163,184,.16);border-radius:20px;padding:16px;}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

MONEY_COLS = ["gross_sales", "net_payout", "promo_cost", "ad_spend", "commission", "total_fees", "refunds", "tax", "adjustments"]


def clean_money(value):
    if pd.isna(value):
        return 0.0
    if isinstance(value, (int, float, np.number)):
        return float(value)
    s = str(value).strip().replace("$", "").replace(",", "").replace("%", "")
    if s in {"", "nan", "None", "-"}:
        return 0.0
    s = s.replace("(", "-").replace(")", "")
    try:
        return float(s)
    except Exception:
        return 0.0


def pick_col(df, candidates):
    lower = {c.lower().strip(): c for c in df.columns}
    for cand in candidates:
        if cand.lower().strip() in lower:
            return lower[cand.lower().strip()]
    for c in df.columns:
        c_low = c.lower()
        for cand in candidates:
            if cand.lower() in c_low:
                return c
    return None


def signed_abs(series):
    return pd.to_numeric(series, errors="coerce").fillna(0).abs()


def classify_file(filename, df):
    name = filename.lower()
    cols = " ".join([c.lower() for c in df.columns])
    if "uber" in name or "uber eats" in cols or "uber eats manager" in cols:
        return "Uber Eats"
    if "doordash" in name or "doordash" in cols or "delivery uuid" in cols:
        return "DoorDash"
    if "grubhub" in name or "grubhub" in cols or "gh_plus" in cols or "gh_" in name:
        return "Grubhub"
    return "Unknown"


def normalize_ubereats(df, filename):
    store = pick_col(df, ["Store name as per Uber Eats manager", "Store name"])
    order_id = pick_col(df, ["Order ID as per Uber Eats manager", "Unique ID to identify the order ", "order id"])
    date_col = pick_col(df, ["Local date the order was placed, or local date of the original order placed for which there is a refund", "Date"])
    status = pick_col(df, ["Either: Completed (eater received food), Cancelled (order cancelled by eater or support), Refund (eater was refunded for order), or Unfulfilled (order was not able to be completed)"])
    gross = pick_col(df, ["Total item sales incl tax", "Total item sales excl tax "])
    net = pick_col(df, ["Total payout associated with this order", "Total payout"])
    commission = pick_col(df, ["The fee Uber charges to merchant", "Marketplace fee", "% Marketplace fee"])
    promo = pick_col(df, ["Merchant promotions applied to the order", "Merchant promotions"])
    ad = pick_col(df, ["All miscellaneous payments like Ad payments", "Ad payments"])
    tax = pick_col(df, ["Tax on total item sales in the order", "Sales tax Uber Eats"])
    refund = pick_col(df, ["Amount merchants are responsible for refunding customers when they report order errors (incl tax)"])
    out = pd.DataFrame()
    out["platform"] = "Uber Eats"
    out["source_file"] = filename
    out["store"] = df[store].astype(str) if store else "Unknown Store"
    out["order_id"] = df[order_id].astype(str) if order_id else [f"uber-{i}" for i in range(len(df))]
    out["date"] = pd.to_datetime(df[date_col], errors="coerce") if date_col else pd.NaT
    out["status"] = df[status].astype(str) if status else "Completed"
    out["gross_sales"] = df[gross].map(clean_money) if gross else 0.0
    out["net_payout"] = df[net].map(clean_money) if net else 0.0
    out["commission"] = signed_abs(df[commission].map(clean_money)) if commission else 0.0
    out["promo_cost"] = signed_abs(df[promo].map(clean_money)) if promo else 0.0
    out["ad_spend"] = signed_abs(df[ad].map(clean_money)) if ad else 0.0
    out["tax"] = signed_abs(df[tax].map(clean_money)) if tax else 0.0
    out["refunds"] = signed_abs(df[refund].map(clean_money)) if refund else 0.0
    return out


def normalize_doordash(df, filename):
    store = pick_col(df, ["Store name", "Business name"])
    order_id = pick_col(df, ["DoorDash order ID", "Delivery UUID", "Merchant delivery ID"])
    date_col = pick_col(df, ["Timestamp local date", "Order received local time", "Payout date"])
    status = pick_col(df, ["Final order status", "Transaction type"])
    gross = pick_col(df, ["Subtotal", "Pre-adjusted subtotal"])
    net = pick_col(df, ["Net total"])
    commission = pick_col(df, ["Commission"])
    tablet = pick_col(df, ["Tablet fee"])
    marketing = pick_col(df, ["Marketing fees | (including any applicable taxes)"])
    promo = pick_col(df, ["Customer discounts from marketing | (funded by you)"])
    error = pick_col(df, ["Error charges"])
    adj = pick_col(df, ["Adjustments"])
    tax = pick_col(df, ["Subtotal tax passed to merchant", "Subtotal tax remitted by DoorDash to tax authorities"])
    out = pd.DataFrame()
    out["platform"] = "DoorDash"
    out["source_file"] = filename
    out["store"] = df[store].astype(str) if store else "Unknown Store"
    out["order_id"] = df[order_id].astype(str) if order_id else [f"dd-{i}" for i in range(len(df))]
    out["date"] = pd.to_datetime(df[date_col], errors="coerce") if date_col else pd.NaT
    out["status"] = df[status].astype(str) if status else "Completed"
    out["gross_sales"] = df[gross].map(clean_money) if gross else 0.0
    out["net_payout"] = df[net].map(clean_money) if net else 0.0
    out["commission"] = signed_abs(df[commission].map(clean_money)) if commission else 0.0
    out["promo_cost"] = signed_abs(df[promo].map(clean_money)) if promo else 0.0
    out["ad_spend"] = signed_abs(df[marketing].map(clean_money)) if marketing else 0.0
    out["total_fees"] = (signed_abs(df[tablet].map(clean_money)) if tablet else 0.0) + out["ad_spend"]
    out["refunds"] = signed_abs(df[error].map(clean_money)) if error else 0.0
    out["adjustments"] = df[adj].map(clean_money) if adj else 0.0
    out["tax"] = signed_abs(df[tax].map(clean_money)) if tax else 0.0
    return out


def normalize_grubhub(df, filename):
    store = pick_col(df, ["store_name"])
    order_id = pick_col(df, ["order_number", "transaction_id", "deposit_id"])
    date_col = pick_col(df, ["transaction_date", "payout_date", "start_date"])
    status = pick_col(df, ["transaction_type", "payout_type"])
    gross = pick_col(df, ["subtotal", "subtotal_sales", "merchant_total"])
    net = pick_col(df, ["merchant_net_total", "payout_amount"])
    commission = pick_col(df, ["commission"])
    delivery_commission = pick_col(df, ["delivery_commission"])
    processing = pick_col(df, ["processing_fee", "order_processing_fee"])
    promo = pick_col(df, ["merchant_funded_promotion", "merchant_funded_promotion_and_loyalty"])
    loyalty = pick_col(df, ["merchant_funded_loyalty"])
    tax = pick_col(df, ["sales_tax", "subtotal_sales_tax"])
    adj = pick_col(df, ["account_adjustments"])
    out = pd.DataFrame()
    out["platform"] = "Grubhub"
    out["source_file"] = filename
    out["store"] = df[store].astype(str) if store else "Unknown Store"
    out["order_id"] = df[order_id].astype(str) if order_id else [f"gh-{i}" for i in range(len(df))]
    out["date"] = pd.to_datetime(df[date_col], errors="coerce") if date_col else pd.NaT
    out["status"] = df[status].astype(str) if status else "Completed"
    out["gross_sales"] = df[gross].map(clean_money) if gross else 0.0
    out["net_payout"] = df[net].map(clean_money) if net else 0.0
    comm = signed_abs(df[commission].map(clean_money)) if commission else 0.0
    deliv = signed_abs(df[delivery_commission].map(clean_money)) if delivery_commission else 0.0
    out["commission"] = comm + deliv
    proc = signed_abs(df[processing].map(clean_money)) if processing else 0.0
    out["total_fees"] = proc
    p1 = signed_abs(df[promo].map(clean_money)) if promo else 0.0
    p2 = signed_abs(df[loyalty].map(clean_money)) if loyalty else 0.0
    out["promo_cost"] = p1 + p2
    out["ad_spend"] = 0.0
    out["tax"] = signed_abs(df[tax].map(clean_money)) if tax else 0.0
    out["adjustments"] = df[adj].map(clean_money) if adj else 0.0
    out["refunds"] = np.where(out["gross_sales"] < 0, out["gross_sales"].abs(), 0.0)
    return out


def normalize_unknown(df, filename):
    platform = classify_file(filename, df)
    if platform == "Uber Eats":
        return normalize_ubereats(df, filename)
    if platform == "DoorDash":
        return normalize_doordash(df, filename)
    if platform == "Grubhub":
        return normalize_grubhub(df, filename)
    out = pd.DataFrame()
    out["platform"] = "Unknown"
    out["source_file"] = filename
    out["store"] = "Unknown Store"
    out["order_id"] = [f"unknown-{i}" for i in range(len(df))]
    out["date"] = pd.NaT
    out["status"] = "Unknown"
    for c in MONEY_COLS:
        out[c] = 0.0
    return out


def finalize(df):
    for c in MONEY_COLS:
        if c not in df.columns:
            df[c] = 0.0
        df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0.0)
    df["total_fees"] = df["total_fees"] + df["commission"]
    df["estimated_leak"] = np.maximum(df["gross_sales"] - df["net_payout"], 0)
    df["net_margin"] = np.where(df["gross_sales"] != 0, df["net_payout"] / df["gross_sales"], 0)
    df["fee_rate"] = np.where(df["gross_sales"] != 0, df["total_fees"] / df["gross_sales"], 0)
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["store"] = df["store"].replace({"nan": "Unknown Store", "None": "Unknown Store"}).fillna("Unknown Store")
    df["status"] = df["status"].fillna("Unknown")
    return df


def load_uploaded(files):
    frames, errors = [], []
    for f in files:
        try:
            raw = f.getvalue()
            df = pd.read_csv(io.BytesIO(raw))
            frames.append(normalize_unknown(df, f.name))
        except Exception as e:
            errors.append(f"{f.name}: {e}")
    if not frames:
        return pd.DataFrame(), errors
    return finalize(pd.concat(frames, ignore_index=True)), errors


def demo_data():
    rng = np.random.default_rng(7)
    stores = ["Gyro Factory", "Smart Bowls", "Hayati Mediterranean"]
    platforms = ["Uber Eats", "DoorDash", "Grubhub"]
    rows = []
    start = pd.Timestamp.today().normalize() - pd.Timedelta(days=29)
    for i in range(420):
        gross = float(np.clip(rng.normal(31, 13), 8, 95))
        platform = rng.choice(platforms, p=[.42, .38, .20])
        commission_rate = {"Uber Eats": .27, "DoorDash": .24, "Grubhub": .30}[platform]
        promo = gross * rng.choice([0, .05, .10, .15, .20, .35], p=[.55,.13,.12,.10,.06,.04])
        ad = gross * rng.choice([0, .03, .05, .08], p=[.62,.18,.13,.07])
        commission = gross * commission_rate
        fees = gross * rng.uniform(.02,.06)
        refunds = gross if rng.random() < .025 else 0
        net = gross - commission - promo - ad - fees - refunds
        status = "Refund/Adjustment" if refunds else "Delivered"
        rows.append({
            "platform": platform,
            "source_file": "demo_data.csv",
            "store": rng.choice(stores),
            "order_id": f"DEMO-{10000+i}",
            "date": start + pd.Timedelta(days=int(rng.integers(0,30))),
            "status": status,
            "gross_sales": gross,
            "net_payout": max(net, 0),
            "promo_cost": promo,
            "ad_spend": ad,
            "commission": commission,
            "total_fees": commission + fees,
            "refunds": refunds,
            "tax": gross * .07,
            "adjustments": -refunds if refunds else 0,
        })
    return finalize(pd.DataFrame(rows))


def fmt_money(x):
    return f"${x:,.2f}"


def fmt_pct(x):
    if pd.isna(x) or np.isinf(x):
        return "0.0%"
    return f"{x*100:,.1f}%"


def kpi(label, value, help_text=""):
    st.markdown(f"""
    <div class='kpi-card'>
        <div class='kpi-label'>{label}</div>
        <div class='kpi-value'>{value}</div>
        <div class='kpi-help'>{help_text}</div>
    </div>
    """, unsafe_allow_html=True)


def hero_metric(label, value, help_text):
    st.markdown(f"""
    <div class='hero-metric'>
        <div class='hero-label'>{label}</div>
        <div class='hero-value'>{value}</div>
        <div class='hero-context'>{help_text}</div>
    </div>
    """, unsafe_allow_html=True)


def leak_metric(label, value, help_text):
    st.markdown(f"""
    <div class='leak-card'>
        <div class='kpi-label'>{label}</div>
        <div class='leak-value'>{value}</div>
        <div class='hero-context'>{help_text}</div>
    </div>
    """, unsafe_allow_html=True)


def apply_date_filter(df, option, custom_range):
    if df.empty or df["date"].isna().all():
        return df
    today = df["date"].max().normalize()
    if option == "Today": start, end = today, today
    elif option == "Yesterday": start, end = today - pd.Timedelta(days=1), today - pd.Timedelta(days=1)
    elif option == "This week": start, end = today - pd.Timedelta(days=today.weekday()), today
    elif option == "Last 7 days": start, end = today - pd.Timedelta(days=6), today
    elif option == "Last week":
        end = today - pd.Timedelta(days=today.weekday()+1)
        start = end - pd.Timedelta(days=6)
    elif option == "Month to date": start, end = today.replace(day=1), today
    elif option == "Last month":
        first_this = today.replace(day=1)
        end = first_this - pd.Timedelta(days=1)
        start = end.replace(day=1)
    elif option == "Last 3 months": start, end = today - pd.DateOffset(months=3), today
    elif option == "Year to date": start, end = today.replace(month=1, day=1), today
    else:
        if custom_range and len(custom_range) == 2:
            start, end = pd.Timestamp(custom_range[0]), pd.Timestamp(custom_range[1])
        else:
            return df
    return df[(df["date"] >= start) & (df["date"] <= end)]


def compute_summary(df):
    orders = int(len(df))
    gross = df["gross_sales"].sum()
    net = df["net_payout"].sum()
    promo = df["promo_cost"].sum()
    ad = df["ad_spend"].sum()
    commission = df["commission"].sum()
    fees = df["total_fees"].sum()
    refunds = df["refunds"].sum()
    aov = gross / orders if orders else 0
    deposit_pct = net / gross if gross else 0
    ad_pct = ad / gross if gross else 0
    promo_pct = promo / gross if gross else 0
    net_margin = net / gross if gross else 0
    money_lost = max(gross - net, 0)
    suspicious = df[(df["net_margin"] < .45) | (df["refunds"] > 0) | (df["promo_cost"] > df["gross_sales"]*.15) | (df["fee_rate"] > .38)]
    potential_recovery = suspicious["estimated_leak"].sum() * .18
    return locals()


def insight_cards(filtered, s):
    if filtered.empty:
        st.info("No data for selected filters.")
        return
    p = filtered.groupby("platform", as_index=False).agg(gross_sales=("gross_sales","sum"), net_payout=("net_payout","sum"), total_fees=("total_fees","sum"), promo_cost=("promo_cost","sum"), ad_spend=("ad_spend","sum"), refunds=("refunds","sum"))
    p["margin"] = np.where(p["gross_sales"] != 0, p["net_payout"] / p["gross_sales"], 0)
    worst = p.sort_values("margin").iloc[0]
    best = p.sort_values("margin", ascending=False).iloc[0]
    st.markdown(f"<div class='danger-card'><b>{len(s['suspicious'])} financial leaks detected.</b> Potential recoverable revenue: <b>{fmt_money(s['potential_recovery'])}</b>.</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='warning-card'><b>{worst['platform']} has the lowest payout margin:</b> {fmt_pct(worst['margin'])}. Review commissions, promos, and adjustments.</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='good-card'><b>{best['platform']} is currently the strongest platform:</b> {fmt_pct(best['margin'])} payout margin.</div>", unsafe_allow_html=True)
    if s['promo_pct'] > .08:
        st.markdown(f"<div class='warning-card'><b>Promotion pressure:</b> promos consumed {fmt_pct(s['promo_pct'])} of gross sales.</div>", unsafe_allow_html=True)
    if s['ad_pct'] > .04:
        st.markdown(f"<div class='warning-card'><b>Ad spend watch:</b> ads consumed {fmt_pct(s['ad_pct'])} of gross sales. Tie campaigns to net payout, not gross sales.</div>", unsafe_allow_html=True)


def order_breakdown(order):
    rows = [
        ("Gross Sales", order["gross_sales"], False),
        ("Tax", -order.get("tax", 0), True),
        ("Platform Commission", -order.get("commission", 0), True),
        ("Promo Deduction", -order.get("promo_cost", 0), True),
        ("Ad / Marketing Spend", -order.get("ad_spend", 0), True),
        ("Refunds", -order.get("refunds", 0), True),
        ("Adjustments", order.get("adjustments", 0), True),
    ]
    html = "<div class='order-box'>"
    html += f"<div style='display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;'><div><span class='badge'>{order['platform']}</span><h3 style='margin:10px 0 0;color:#f8fafc;'>{order['order_id']}</h3><div class='small-muted'>{order['store']} · {order['status']}</div></div><div class='badge'>Margin {fmt_pct(order['net_margin'])}</div></div>"
    for name, value, deduction in rows:
        val = fmt_money(value)
        color = "#fb7185" if value < 0 else "#a7f3d0"
        html += f"<div class='breakdown-row'><span>{name}</span><strong style='color:{color}'>{val}</strong></div>"
    html += f"<div class='net-row'><span>Net Payout</span><span>{fmt_money(order['net_payout'])}</span></div>"
    html += "</div>"
    st.markdown(html, unsafe_allow_html=True)


# Sidebar
st.sidebar.markdown("# Virtus")
st.sidebar.markdown("Financial truth layer for delivery apps.")
page = st.sidebar.radio("Navigation", ["Dashboard", "Orders", "Insights", "Payouts & Reports", "Settings", "Help & Support"])

with st.sidebar:
    st.divider()
    use_demo = st.toggle("Use demo data", value=True)
    files = st.file_uploader("Upload delivery CSV reports", type=["csv"], accept_multiple_files=True)

if use_demo and not files:
    data = demo_data()
    errors = []
else:
    data, errors = load_uploaded(files or [])

if errors:
    for e in errors:
        st.warning(e)

if data.empty:
    st.markdown("""
    <div class='virtus-hero'>
      <div class='virtus-eyebrow'>Delivery Financial Intelligence</div>
      <div class='virtus-title'>Upload delivery statements. See what you actually kept.</div>
      <div class='virtus-subtitle'>Virtus normalizes payout, promo, ad, refund, commission, and fee data into one financial truth layer.</div>
    </div>
    """, unsafe_allow_html=True)
    st.info("Upload CSV files or turn on demo data to view the dashboard.")
    st.stop()

with st.sidebar:
    st.divider()
    date_option = st.selectbox("Date", ["Today", "Yesterday", "This week", "Last 7 days", "Last week", "Month to date", "Last month", "Last 3 months", "Year to date", "Custom period"], index=6)
    custom_range = None
    if date_option == "Custom period":
        custom_range = st.date_input("Custom period", value=(data["date"].min().date(), data["date"].max().date()))
    stores = sorted(data["store"].dropna().unique())
    platforms = sorted(data["platform"].dropna().unique())
    selected_stores = st.multiselect("Store selector", stores, default=stores)
    selected_platforms = st.multiselect("Platform selector", platforms, default=platforms)

filtered = apply_date_filter(data, date_option, custom_range)
filtered = filtered[filtered["store"].isin(selected_stores) & filtered["platform"].isin(selected_platforms)]
s = compute_summary(filtered)

st.markdown("""
<div class='virtus-topbar'>
  <div class='virtus-brand'>Virtus</div>
  <div><span class='virtus-pill'>Live Financial Demo</span></div>
</div>
<div class='virtus-hero'>
  <div class='virtus-eyebrow'>Delivery Financial Intelligence</div>
  <div class='virtus-title'>Know what you actually keep from every delivery order.</div>
  <div class='virtus-subtitle'>Uber Eats, DoorDash, Grubhub, and POS data unified into one financial intelligence layer. Virtus reconciles gross sales, commissions, promos, ads, refunds, taxes, and hidden fees at the order level.</div>
</div>
""", unsafe_allow_html=True)

if page == "Dashboard":
    st.markdown("<div class='hero-grid'>", unsafe_allow_html=True)
    left, right = st.columns([1.35, .65])
    with left:
        hero_metric("Actual Net Payout", fmt_money(s['net']), f"From {s['orders']:,} orders · effective margin {fmt_pct(s['net_margin'])}")
    with right:
        leak_metric("Money Lost to Apps", fmt_money(s['money_lost']), "Commissions, promos, ads, refunds, and payout leakage")
    st.markdown("</div>", unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    with c1: kpi("Gross Sales", fmt_money(s['gross']), f"AOV {fmt_money(s['aov'])}")
    with c2: kpi("Net Margin", fmt_pct(s['net_margin']), f"Deposit % {fmt_pct(s['deposit_pct'])}")
    with c3: kpi("Recoverable Revenue", fmt_money(s['potential_recovery']), f"{len(s['suspicious'])} suspicious orders")
    with c4: kpi("Platform Commissions", fmt_money(s['commission']), fmt_pct(s['commission']/s['gross'] if s['gross'] else 0))

    c5, c6, c7, c8 = st.columns(4)
    with c5: kpi("Promo Cost", fmt_money(s['promo']), fmt_pct(s['promo_pct']))
    with c6: kpi("Ad Spend", fmt_money(s['ad']), fmt_pct(s['ad_pct']))
    with c7: kpi("Refunds", fmt_money(s['refunds']), fmt_pct(s['refunds']/s['gross'] if s['gross'] else 0))
    with c8: kpi("Total Fees", fmt_money(s['fees']), fmt_pct(s['fees']/s['gross'] if s['gross'] else 0))

    left, right = st.columns([1.1, .9])
    with left:
        st.markdown("<div class='section-title'>Platform Profitability Comparison</div>", unsafe_allow_html=True)
        platform = filtered.groupby("platform", as_index=False).agg(
            orders=("order_id", "count"), gross_sales=("gross_sales", "sum"), net_payout=("net_payout", "sum"),
            promo_cost=("promo_cost", "sum"), ad_spend=("ad_spend", "sum"), total_fees=("total_fees", "sum")
        )
        platform["net_margin"] = np.where(platform["gross_sales"] != 0, platform["net_payout"] / platform["gross_sales"], 0)
        fig = px.bar(platform, x="platform", y=["gross_sales", "net_payout"], barmode="group", text_auto=".2s")
        fig.update_layout(height=370, legend_title_text="", margin=dict(l=10,r=10,t=20,b=10), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#cbd5e1")
        st.plotly_chart(fig, use_container_width=True)
    with right:
        st.markdown("<div class='section-title'>AI Financial Insights</div>", unsafe_allow_html=True)
        insight_cards(filtered, s)

    left, right = st.columns([.92, 1.08])
    with left:
        st.markdown("<div class='section-title'>Money Flow</div>", unsafe_allow_html=True)
        flow = pd.DataFrame({"Category":["Gross Sales","Commissions","Promos","Ads","Refunds","Other Fees","Net Payout"],"Amount":[s['gross'], -s['commission'], -s['promo'], -s['ad'], -s['refunds'], -(s['fees']-s['commission']), s['net']]})
        fig2 = go.Figure(go.Waterfall(x=flow["Category"], y=flow["Amount"], connector={"line":{"color":"rgba(148,163,184,.45)"}}))
        fig2.update_layout(height=360, margin=dict(l=10,r=10,t=20,b=10), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#cbd5e1")
        st.plotly_chart(fig2, use_container_width=True)
    with right:
        st.markdown("<div class='section-title'>Order-Level Payout Breakdown</div>", unsafe_allow_html=True)
        order_options = filtered.sort_values("estimated_leak", ascending=False).head(80).copy()
        labels = (order_options["order_id"].astype(str) + " · " + order_options["platform"].astype(str) + " · " + order_options["store"].astype(str)).tolist()
        choice = st.selectbox("Select an order to inspect", labels)
        idx = labels.index(choice)
        order_breakdown(order_options.iloc[idx])

    st.markdown("<div class='section-title'>Recent Orders Summary</div>", unsafe_allow_html=True)
    show = filtered.sort_values("date", ascending=False).head(18).copy()
    cols = ["date", "platform", "store", "order_id", "status", "gross_sales", "commission", "promo_cost", "ad_spend", "total_fees", "net_payout", "net_margin"]
    st.dataframe(show[cols], use_container_width=True, hide_index=True)

elif page == "Orders":
    st.markdown("<div class='section-title'>Orders</div>", unsafe_allow_html=True)
    q = st.text_input("Search order, store, platform, or status")
    show = filtered.copy()
    if q:
        mask = show.astype(str).apply(lambda col: col.str.contains(q, case=False, na=False)).any(axis=1)
        show = show[mask]
    st.dataframe(show.sort_values("date", ascending=False), use_container_width=True, hide_index=True)
    st.markdown("<div class='section-title'>Inspect Order</div>", unsafe_allow_html=True)
    if not show.empty:
        labels = (show["order_id"].astype(str) + " · " + show["platform"].astype(str) + " · " + show["store"].astype(str)).head(200).tolist()
        choice = st.selectbox("Choose order", labels)
        order_breakdown(show.iloc[labels.index(choice)])

elif page == "Insights":
    st.markdown("<div class='section-title'>Financial Leak Detection</div>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    c1.metric("Orders flagged", len(s['suspicious']))
    c2.metric("Potential recoverable", fmt_money(s['potential_recovery']))
    c3.metric("Average margin", fmt_pct(s['net_margin']))
    insight_cards(filtered, s)
    st.dataframe(s['suspicious'].sort_values("estimated_leak", ascending=False).head(100), use_container_width=True, hide_index=True)

elif page == "Payouts & Reports":
    st.markdown("<div class='section-title'>Payouts & Reports</div>", unsafe_allow_html=True)
    report = filtered.groupby(["platform", "store"], as_index=False).agg(
        orders=("order_id", "count"), gross_sales=("gross_sales", "sum"), net_payout=("net_payout", "sum"),
        promo_cost=("promo_cost", "sum"), ad_spend=("ad_spend", "sum"), commission=("commission", "sum"), total_fees=("total_fees", "sum"), refunds=("refunds", "sum")
    )
    report["deposit_pct"] = np.where(report["gross_sales"] != 0, report["net_payout"] / report["gross_sales"], 0)
    report["net_margin"] = report["deposit_pct"]
    st.dataframe(report, use_container_width=True, hide_index=True)
    st.download_button("Download normalized transactions CSV", filtered.to_csv(index=False).encode("utf-8"), "virtus_normalized_transactions.csv", "text/csv")
    st.download_button("Download summary report CSV", report.to_csv(index=False).encode("utf-8"), "virtus_summary_report.csv", "text/csv")

elif page == "Settings":
    st.markdown("<div class='section-title'>Settings</div>", unsafe_allow_html=True)
    st.markdown("<div class='info-card'><b>MVP mode:</b> upload-based data ingestion. Production version will use API connectors, persistent storage, authentication, alert rules, and dispute workflows.</div>", unsafe_allow_html=True)
    st.write("Planned integrations: Uber Eats, DoorDash, Grubhub, Toast, Square, Clover, bank deposits, and accounting exports.")

else:
    st.markdown("<div class='section-title'>Help & Support</div>", unsafe_allow_html=True)
    st.write("Upload CSV files from Uber Eats, DoorDash, and Grubhub. Virtus auto-detects the platform based on filename and columns.")
    st.write("For best results, upload detailed transactions, payout summaries, promotions, sponsored listings, refunds, and adjustments together.")

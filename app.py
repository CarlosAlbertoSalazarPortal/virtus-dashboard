import io
import re
from datetime import date, timedelta

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="Virtus | Delivery Financial Intelligence", page_icon="V", layout="wide")
st.success("App loaded successfully.")

CSS = """
<style>
.block-container{padding-top:1.5rem; padding-bottom:2rem;}
[data-testid="stSidebar"]{background:#070b16;}
.virtus-hero{padding:28px 30px;border:1px solid rgba(148,163,184,.25);border-radius:26px;background:linear-gradient(135deg,#0f172a 0%,#111827 50%,#172554 100%);box-shadow:0 24px 80px rgba(0,0,0,.25);margin-bottom:18px;}
.virtus-eyebrow{color:#93c5fd;font-weight:700;letter-spacing:.08em;text-transform:uppercase;font-size:.78rem;margin-bottom:.5rem;}
.virtus-title{font-size:2.35rem;line-height:1.08;font-weight:850;color:#f8fafc;margin-bottom:.65rem;}
.virtus-subtitle{font-size:1.02rem;color:#cbd5e1;max-width:880px;}
.kpi-card{border:1px solid rgba(148,163,184,.22);border-radius:22px;padding:18px 18px;background:rgba(15,23,42,.88);box-shadow:0 12px 40px rgba(0,0,0,.18);min-height:132px;}
.kpi-label{color:#94a3b8;font-size:.82rem;font-weight:700;text-transform:uppercase;letter-spacing:.05em;}
.kpi-value{font-size:1.8rem;font-weight:850;color:#f8fafc;margin-top:9px;}
.kpi-help{color:#a7f3d0;font-size:.86rem;margin-top:8px;}
.section-title{font-size:1.25rem;font-weight:800;color:#f8fafc;margin:8px 0 8px;}
.warning-card{border:1px solid rgba(251,191,36,.35);border-radius:18px;background:rgba(120,53,15,.25);padding:14px 16px;color:#fde68a;margin-bottom:10px;}
.good-card{border:1px solid rgba(34,197,94,.35);border-radius:18px;background:rgba(20,83,45,.23);padding:14px 16px;color:#bbf7d0;margin-bottom:10px;}
.small-muted{color:#94a3b8;font-size:.88rem;}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

MONEY_COLS = [
    "gross_sales", "net_payout", "promo_cost", "ad_spend", "commission", "total_fees",
    "refunds", "tax", "adjustments"
]


def clean_money(value):
    if pd.isna(value):
        return 0.0
    if isinstance(value, (int, float, np.number)):
        return float(value)
    s = str(value).strip().replace("$", "").replace(",", "").replace("%", "")
    if s in {"", "nan", "None", "-"}:
        return 0.0
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
    out["status"] = df[status].astype(str) if status else "Unknown"
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
    out["status"] = df[status].astype(str) if status else "Unknown"
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
    out["status"] = df[status].astype(str) if status else "Unknown"
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
    for c in MONEY_COLS + ["adjustments", "tax", "refunds"]:
        out[c] = 0.0
    return out


def finalize(df):
    for c in MONEY_COLS + ["adjustments", "tax", "refunds"]:
        if c not in df.columns:
            df[c] = 0.0
        df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0.0)
    if "total_fees" not in df.columns or df["total_fees"].sum() == 0:
        df["total_fees"] = 0.0
    df["total_fees"] = df["total_fees"] + df["commission"]
    df["estimated_leak"] = np.maximum(df["gross_sales"] - df["net_payout"], 0)
    df["net_margin"] = np.where(df["gross_sales"] != 0, df["net_payout"] / df["gross_sales"], 0)
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["store"] = df["store"].replace({"nan": "Unknown Store", "None": "Unknown Store"}).fillna("Unknown Store")
    df["status"] = df["status"].fillna("Unknown")
    return df


def load_uploaded(files):
    frames = []
    errors = []
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
        gross = float(rng.normal(31, 13).clip(8, 95))
        platform = rng.choice(platforms, p=[.42, .38, .20])
        commission_rate = {"Uber Eats": .27, "DoorDash": .24, "Grubhub": .30}[platform]
        promo = gross * rng.choice([0, .05, .10, .15, .20], p=[.58,.14,.12,.10,.06])
        ad = gross * rng.choice([0, .03, .05, .08], p=[.62,.18,.13,.07])
        commission = gross * commission_rate
        fees = gross * rng.uniform(.02,.06)
        refunds = gross if rng.random() < .025 else 0
        net = gross - commission - promo - ad - fees - refunds
        rows.append({
            "platform": platform,
            "source_file": "demo_data.csv",
            "store": rng.choice(stores),
            "order_id": f"DEMO-{10000+i}",
            "date": start + pd.Timedelta(days=int(rng.integers(0,30))),
            "status": "Delivered" if refunds == 0 else "Refund/Adjustment",
            "gross_sales": gross,
            "net_payout": net,
            "promo_cost": promo,
            "ad_spend": ad,
            "commission": commission,
            "total_fees": commission + fees,
            "refunds": refunds,
            "tax": gross * .07,
            "adjustments": 0,
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


st.sidebar.markdown("# Virtus")
st.sidebar.markdown("Financial truth layer for delivery apps.")
page = st.sidebar.radio("Navigation", ["Dashboard", "Orders", "Insights", "Payouts & Reports", "Settings", "Help & Support"])

st.markdown("""
<div class='virtus-hero'>
  <div class='virtus-eyebrow'>Delivery Financial Intelligence</div>
  <div class='virtus-title'>Know what you actually keep from every delivery order.</div>
  <div class='virtus-subtitle'>Upload Uber Eats, DoorDash, and Grubhub CSVs to reconcile gross sales, fees, commissions, promos, ad spend, refunds, and net payouts in one dashboard.</div>
</div>
""", unsafe_allow_html=True)

with st.sidebar:
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

orders = int(len(filtered))
gross = filtered["gross_sales"].sum()
net = filtered["net_payout"].sum()
promo = filtered["promo_cost"].sum()
ad = filtered["ad_spend"].sum()
commission = filtered["commission"].sum()
fees = filtered["total_fees"].sum()
refunds = filtered["refunds"].sum()
aov = gross / orders if orders else 0
deposit_pct = net / gross if gross else 0
ad_pct = ad / gross if gross else 0
promo_pct = promo / gross if gross else 0
net_margin = net / gross if gross else 0
money_lost = max(gross - net, 0)

if page == "Dashboard":
    c1, c2, c3, c4 = st.columns(4)
    with c1: kpi("Net Payout", fmt_money(net), f"Deposit %: {fmt_pct(deposit_pct)}")
    with c2: kpi("Gross Sales", fmt_money(gross), f"Orders: {orders:,}")
    with c3: kpi("Money Lost to Apps", fmt_money(money_lost), "Fees, promos, ads, refunds")
    with c4: kpi("Net Margin", fmt_pct(net_margin), f"AOV: {fmt_money(aov)}")

    c5, c6, c7, c8 = st.columns(4)
    with c5: kpi("Promo Cost", fmt_money(promo), fmt_pct(promo_pct))
    with c6: kpi("Ad Spend", fmt_money(ad), fmt_pct(ad_pct))
    with c7: kpi("Platform Commissions", fmt_money(commission), fmt_pct(commission/gross if gross else 0))
    with c8: kpi("Total Fees", fmt_money(fees), fmt_pct(fees/gross if gross else 0))

    left, right = st.columns([1.25, 1])
    with left:
        st.markdown("<div class='section-title'>Platform Performance Comparison</div>", unsafe_allow_html=True)
        platform = filtered.groupby("platform", as_index=False).agg(
            orders=("order_id", "count"), gross_sales=("gross_sales", "sum"), net_payout=("net_payout", "sum"),
            promo_cost=("promo_cost", "sum"), ad_spend=("ad_spend", "sum"), total_fees=("total_fees", "sum")
        )
        platform["net_margin"] = np.where(platform["gross_sales"] != 0, platform["net_payout"] / platform["gross_sales"], 0)
        fig = px.bar(platform, x="platform", y=["gross_sales", "net_payout"], barmode="group", text_auto=".2s")
        fig.update_layout(height=390, legend_title_text="", margin=dict(l=10,r=10,t=20,b=10), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True)
    with right:
        st.markdown("<div class='section-title'>Insights</div>", unsafe_allow_html=True)
        if gross and money_lost / gross > .35:
            st.markdown(f"<div class='warning-card'><b>High delivery leakage:</b> {fmt_pct(money_lost/gross)} of gross sales did not convert into payout.</div>", unsafe_allow_html=True)
        if promo_pct > .08:
            st.markdown(f"<div class='warning-card'><b>Promo pressure:</b> promotions consumed {fmt_pct(promo_pct)} of gross sales.</div>", unsafe_allow_html=True)
        if ad_pct > .05:
            st.markdown(f"<div class='warning-card'><b>Ad spend watch:</b> ad spend is {fmt_pct(ad_pct)} of gross sales.</div>", unsafe_allow_html=True)
        if net_margin > .60:
            st.markdown("<div class='good-card'><b>Healthy payout margin:</b> net payout is above 60% of gross sales.</div>", unsafe_allow_html=True)
        st.markdown("<div class='small-muted'>Next product layer: connect COGS, labor, packaging, and rent allocation to calculate true net profit instead of payout margin.</div>", unsafe_allow_html=True)

    st.markdown("<div class='section-title'>Recent Orders Summary</div>", unsafe_allow_html=True)
    show = filtered.sort_values("date", ascending=False).head(20).copy()
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

elif page == "Insights":
    st.markdown("<div class='section-title'>Financial Leak Detection</div>", unsafe_allow_html=True)
    suspicious = filtered[(filtered["net_margin"] < .45) | (filtered["refunds"] > 0) | (filtered["promo_cost"] > filtered["gross_sales"]*.15)].copy()
    st.metric("Orders flagged", len(suspicious))
    st.dataframe(suspicious.sort_values("estimated_leak", ascending=False).head(100), use_container_width=True, hide_index=True)

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
    st.write("Current MVP settings are upload-based. In production, this section would manage platform connections, POS integrations, user roles, alert rules, and billing.")

else:
    st.markdown("<div class='section-title'>Help & Support</div>", unsafe_allow_html=True)
    st.write("Upload CSV files from Uber Eats, DoorDash, and Grubhub. The dashboard auto-detects the platform based on the filename and columns.")
    st.write("For best results, upload detailed transaction files, payout summaries, promotion reports, and sponsored listing/ad reports together.")

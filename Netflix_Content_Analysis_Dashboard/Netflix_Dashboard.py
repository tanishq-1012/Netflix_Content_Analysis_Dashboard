
# app.py
# -------------------------------------------------------------
# Netflix Content Strategy Analysis — Interactive Streamlit Dashboard
# Author: Tanishq Sharma
# -------------------------------------------------------------

import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st
from datetime import datetime

# --------------------------
# Page config
# --------------------------
st.set_page_config(
    page_title="Netflix Content Strategy Analysis — 2023",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --------------------------
# Helpers
# --------------------------
SEASON_ORDER = ["Winter", "Spring", "Summer", "Fall"]
WEEKDAY_ORDER = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
MONTH_ORDER = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def get_season(month: int) -> str:
    if month in [12, 1, 2]:
        return "Winter"
    elif month in [3, 4, 5]:
        return "Spring"
    elif month in [6, 7, 8]:
        return "Summer"
    return "Fall"


@st.cache_data(show_spinner=False)
def load_data(csv_path: str) -> pd.DataFrame:
    df = pd.read_csv(csv_path)

    # Clean & types
    if df["Hours Viewed"].dtype == object:
        df["Hours Viewed"] = df["Hours Viewed"].replace(",", "", regex=True).astype(float)

    df["Release Date"] = pd.to_datetime(df["Release Date"], errors="coerce")
    df["Release Month"] = df["Release Date"].dt.month
    df["Release Month Name"] = df["Release Date"].dt.month_name().str[:3]
    df["Release Day"] = df["Release Date"].dt.day_name()
    df["Release Season"] = df["Release Month"].apply(get_season)

    # Order categoricals for nicer plotting
    df["Release Season"] = pd.Categorical(df["Release Season"], categories=SEASON_ORDER, ordered=True)
    df["Release Day"] = pd.Categorical(df["Release Day"], categories=WEEKDAY_ORDER, ordered=True)
    df["Release Month Name"] = pd.Categorical(df["Release Month Name"], categories=MONTH_ORDER, ordered=True)

    return df


def kpi_block(df: pd.DataFrame):
    total_hours = df["Hours Viewed"].sum()
    n_titles = df.shape[0]
    avg_hours = total_hours / n_titles if n_titles else 0

    # % shows vs movies
    if "Content Type" in df.columns:
        content_counts = df["Content Type"].value_counts(normalize=True) * 100
        show_pct = content_counts.get("Show", 0.0)
        movie_pct = content_counts.get("Movie", 0.0)
    else:
        show_pct = movie_pct = 0

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Hours Viewed (M)", f"{total_hours:,.1f}")
    c2.metric("Total Titles", f"{n_titles:,}")
    c3.metric("Avg Hours per Title (M)", f"{avg_hours:,.1f}")
    c4.metric("Shows vs Movies (%)", f"{show_pct:.1f}% / {movie_pct:.1f}%")


def plot_viewership_by_content_type(df: pd.DataFrame):
    content_view = df.groupby("Content Type")["Hours Viewed"].sum().reset_index()
    fig = px.bar(
        content_view,
        x="Content Type",
        y="Hours Viewed",
        color="Content Type",
        title="Total Viewership Hours by Content Type (2023)",
        text_auto=".2s",
    )
    fig.update_traces(textposition="outside")
    fig.update_layout(showlegend=False, yaxis_title="Total Hours Viewed (millions)")
    st.plotly_chart(fig, use_container_width=True)


def plot_viewership_by_language(df: pd.DataFrame):
    lang_view = df.groupby("Language Indicator")["Hours Viewed"].sum().sort_values(ascending=False).reset_index()
    fig = px.bar(
        lang_view,
        x="Language Indicator",
        y="Hours Viewed",
        title="Total Viewership Hours by Language (2023)",
        text_auto=".2s",
    )
    fig.update_traces(marker_color="#f87171")
    fig.update_layout(xaxis_tickangle=45, yaxis_title="Total Hours Viewed (millions)")
    st.plotly_chart(fig, use_container_width=True)


def plot_monthly_viewership(df: pd.DataFrame):
    monthly_view = (
        df.groupby("Release Month Name")["Hours Viewed"].sum().reindex(MONTH_ORDER).reset_index()
    )
    fig = px.line(
        monthly_view,
        x="Release Month Name",
        y="Hours Viewed",
        markers=True,
        title="Total Viewership Hours by Release Month (2023)",
    )
    st.plotly_chart(fig, use_container_width=True)


def plot_monthly_viewership_by_type(df: pd.DataFrame):
    pivot = (
        df.pivot_table(index="Release Month Name", columns="Content Type", values="Hours Viewed", aggfunc="sum")
        .reindex(MONTH_ORDER)
        .reset_index()
    )
    fig = go.Figure()
    for col in [c for c in pivot.columns if c not in ["Release Month Name"]]:
        fig.add_trace(
            go.Scatter(
                x=pivot["Release Month Name"],
                y=pivot[col],
                mode="lines+markers",
                name=col,
            )
        )
    fig.update_layout(
        title="Viewership Trends by Content Type and Release Month (2023)",
        xaxis_title="Month",
        yaxis_title="Total Hours Viewed (millions)",
    )
    st.plotly_chart(fig, use_container_width=True)


def plot_seasonal_viewership(df: pd.DataFrame):
    seasonal = df.groupby("Release Season")["Hours Viewed"].sum().reindex(SEASON_ORDER).reset_index()
    fig = px.bar(
        seasonal,
        x="Release Season",
        y="Hours Viewed",
        title="Total Viewership Hours by Release Season (2023)",
        text_auto=".2s",
    )
    fig.update_traces(marker_color="#fb923c")
    fig.update_layout(yaxis_title="Total Hours Viewed (millions)")
    st.plotly_chart(fig, use_container_width=True)


def plot_monthly_release_vs_viewership(df: pd.DataFrame):
    monthly_releases = df["Release Month Name"].value_counts().reindex(MONTH_ORDER).reset_index()
    monthly_releases.columns = ["Release Month Name", "Num Releases"]

    monthly_view = df.groupby("Release Month Name")["Hours Viewed"].sum().reindex(MONTH_ORDER).reset_index()

    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(
        go.Bar(x=monthly_releases["Release Month Name"], y=monthly_releases["Num Releases"], name="Number of Releases", opacity=0.7),
        secondary_y=False,
    )
    fig.add_trace(
        go.Scatter(x=monthly_view["Release Month Name"], y=monthly_view["Hours Viewed"], name="Viewership Hours", mode="lines+markers"),
        secondary_y=True,
    )

    fig.update_layout(title="Monthly Release Patterns and Viewership Hours (2023)")
    fig.update_xaxes(title_text="Month")
    fig.update_yaxes(title_text="Number of Releases", secondary_y=False)
    fig.update_yaxes(title_text="Total Hours Viewed (millions)", secondary_y=True)

    st.plotly_chart(fig, use_container_width=True)


def plot_weekday_release_vs_viewership(df: pd.DataFrame):
    weekday_releases = df["Release Day"].value_counts().reindex(WEEKDAY_ORDER).reset_index()
    weekday_releases.columns = ["Release Day", "Num Releases"]

    weekday_view = df.groupby("Release Day")["Hours Viewed"].sum().reindex(WEEKDAY_ORDER).reset_index()

    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(
        go.Bar(x=weekday_releases["Release Day"], y=weekday_releases["Num Releases"], name="Number of Releases", opacity=0.6),
        secondary_y=False,
    )
    fig.add_trace(
        go.Scatter(x=weekday_view["Release Day"], y=weekday_view["Hours Viewed"], name="Viewership Hours", mode="lines+markers"),
        secondary_y=True,
    )

    fig.update_layout(title="Weekly Release Patterns and Viewership Hours (2023)")
    fig.update_xaxes(title_text="Day of the Week")
    fig.update_yaxes(title_text="Number of Releases", secondary_y=False)
    fig.update_yaxes(title_text="Total Hours Viewed (millions)", secondary_y=True)

    st.plotly_chart(fig, use_container_width=True)


def plot_top_titles(df: pd.DataFrame, k: int = 10):
    top_titles = df.nlargest(k, "Hours Viewed")[
        ["Title", "Hours Viewed", "Language Indicator", "Content Type", "Release Date"]
    ]
    st.subheader(f"Top {k} Titles by Hours Viewed")
    st.dataframe(top_titles.reset_index(drop=True))


def holiday_analysis(df: pd.DataFrame):
    st.subheader("Holiday / Event Impact Analyzer")
    st.caption("Checks titles released within ±N days of the given dates")

    default_dates = [
        "2023-01-01",  # New Year
        "2023-02-14",  # Valentine's Day
        "2023-07-04",  # US Independence Day
        "2023-10-31",  # Halloween
        "2023-12-25",  # Christmas
    ]
    date_strings = st.text_area(
        "Important Dates (comma-separated YYYY-MM-DD):",
        value=", ".join(default_dates),
        help="Enter comma-separated dates you want to analyze around",
    )
    window = st.slider("Day window (±N days)", 0, 14, 3)

    try:
        dates = [d.strip() for d in date_strings.split(",") if d.strip()]
        dates = pd.to_datetime(dates, errors="coerce").dropna()
    except Exception:
        st.error("Please provide valid dates in YYYY-MM-DD format")
        return

    mask = df["Release Date"].apply(lambda x: any(abs((x - d).days) <= window for d in dates))
    holiday_releases = df[mask].copy()

    if holiday_releases.empty:
        st.info("No releases found within the selected window.")
        return

    viewership_by_date = holiday_releases.groupby("Release Date")["Hours Viewed"].sum().reset_index()
    fig = px.bar(viewership_by_date, x="Release Date", y="Hours Viewed", title="Viewership for Releases Near Important Dates", text_auto=".2s")
    st.plotly_chart(fig, use_container_width=True)

    st.dataframe(
        holiday_releases[["Title", "Release Date", "Hours Viewed", "Language Indicator", "Content Type"]]
        .sort_values("Release Date")
        .reset_index(drop=True)
    )


# --------------------------
# Sidebar controls
# --------------------------
st.sidebar.header("⚙️ Controls")

dataset_source = st.sidebar.radio(
    "Choose data source",
    ["Upload CSV", "Use local path"],
    index=0,
)

if dataset_source == "Upload CSV":
    uploaded = st.sidebar.file_uploader("Upload netflix_content_2023.csv", type=["csv"])
    if uploaded is None:
        st.sidebar.info("Upload a CSV to proceed.")
        st.stop()
    df = load_data(uploaded)
else:
    path = st.sidebar.text_input("Local CSV path", "netflix_content_2023.csv")
    try:
        df = load_data(path)
    except FileNotFoundError:
        st.sidebar.error("File not found. Please provide a valid path or upload a CSV.")
        st.stop()

# Filters
content_types = sorted(df["Content Type"].dropna().unique()) if "Content Type" in df.columns else []
languages = sorted(df["Language Indicator"].dropna().unique()) if "Language Indicator" in df.columns else []

selected_types = st.sidebar.multiselect("Content Type", options=content_types, default=content_types)
selected_langs = st.sidebar.multiselect("Language", options=languages, default=languages[:5] if len(languages) > 5 else languages)

min_date = df["Release Date"].min().date() if df["Release Date"].notna().any() else datetime(2023, 1, 1).date()
max_date = df["Release Date"].max().date() if df["Release Date"].notna().any() else datetime(2023, 12, 31).date()

start_date, end_date = st.sidebar.date_input(
    "Release date range", value=(min_date, max_date), min_value=min_date, max_value=max_date
)

# Apply filters
mask = (
    (df["Release Date"].dt.date >= start_date)
    & (df["Release Date"].dt.date <= end_date)
)
if selected_types:
    mask &= df["Content Type"].isin(selected_types)
if selected_langs:
    mask &= df["Language Indicator"].isin(selected_langs)

fdf = df[mask].copy()

# --------------------------
# Main layout
# --------------------------
st.title("🎬 Netflix Content Strategy Analysis — 2023 Dashboard")
st.caption("Interactive dashboard to explore viewership by content type, language, time, and release strategy.")

# KPIs
kpi_block(fdf)

# Tabs
overview_tab, language_tab, time_tab, weekday_tab, top_tab, holiday_tab = st.tabs(
    ["Overview", "Language", "Time Trends", "Weekday Strategy", "Top Titles", "Holidays & Events"]
)

with overview_tab:
    st.subheader("Content Type vs Viewership")
    plot_viewership_by_content_type(fdf)

with language_tab:
    st.subheader("Language-wise Viewership")
    plot_viewership_by_language(fdf)

with time_tab:
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Monthly Viewership Trend")
        plot_monthly_viewership(fdf)
    with c2:
        st.subheader("Monthly Trend by Content Type")
        plot_monthly_viewership_by_type(fdf)

    st.subheader("Seasonal Viewership")
    plot_seasonal_viewership(fdf)

    st.subheader("Monthly Releases vs Viewership")
    plot_monthly_release_vs_viewership(fdf)

with weekday_tab:
    st.subheader("Weekly Release Patterns & Viewership")
    plot_weekday_release_vs_viewership(fdf)

with top_tab:
    k = st.slider("Top N titles", 5, 50, 10, 5)
    plot_top_titles(fdf, k)

with holiday_tab:
    holiday_analysis(fdf)

st.markdown("---")
st.write("Built using Streamlit & Plotly by **Tanishq Sharma**")




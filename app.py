import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl
from datetime import datetime
import anthropic
import os
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="Tennis Era Explorer",
    page_icon="🎾",
    layout="wide"
)

# ── Custom CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@400;600;700;800&family=Barlow:wght@300;400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'Barlow', sans-serif;
    background-color: #0e0e0e;
    color: #f0f0f0;
}
.stApp { background-color: #0e0e0e; }

[data-testid="stSidebar"] {
    background-color: #161616;
    border-right: 1px solid #2a2a2a;
}
[data-testid="stSidebar"] * {
    color: #c0c0c0 !important;
    font-family: 'Barlow', sans-serif !important;
}

h1 {
    font-family: 'Barlow Condensed', sans-serif !important;
    font-size: 4rem !important;
    font-weight: 800 !important;
    letter-spacing: -1px !important;
    color: #ffffff !important;
    line-height: 1 !important;
    text-transform: uppercase;
}
h2 {
    font-family: 'Barlow Condensed', sans-serif !important;
    font-size: 1.6rem !important;
    font-weight: 700 !important;
    letter-spacing: 2px !important;
    text-transform: uppercase !important;
    color: #c9f31d !important;
    border-bottom: 2px solid #c9f31d;
    padding-bottom: 6px;
    margin-top: 2rem !important;
}
h3 {
    font-family: 'Barlow Condensed', sans-serif !important;
    font-size: 1.3rem !important;
    font-weight: 700 !important;
    letter-spacing: 3px !important;
    text-transform: uppercase !important;
    color: #ffffff !important;
}
p, li {
    font-family: 'Barlow', sans-serif !important;
    font-weight: 300 !important;
    color: #c0c0c0 !important;
    font-size: 1rem !important;
    line-height: 1.7 !important;
}

[data-testid="stMetric"] {
    background-color: #1a1a1a;
    border: 1px solid #2a2a2a;
    border-radius: 4px;
    padding: 1.2rem 1.5rem !important;
}
[data-testid="stMetricLabel"] {
    font-family: 'Barlow Condensed', sans-serif !important;
    font-size: 0.75rem !important;
    letter-spacing: 3px !important;
    text-transform: uppercase !important;
    color: #888 !important;
}
[data-testid="stMetricValue"] {
    font-family: 'Barlow Condensed', sans-serif !important;
    font-size: 2.5rem !important;
    font-weight: 700 !important;
    color: #ffffff !important;
}

[data-testid="stDataFrame"] {
    border: 1px solid #2a2a2a !important;
    border-radius: 4px !important;
}

hr { border-color: #2a2a2a !important; margin: 2rem 0 !important; }

[data-testid="stExpander"] {
    background-color: #161616 !important;
    border: 1px solid #2a2a2a !important;
    border-radius: 4px !important;
}
[data-testid="stCaptionContainer"] p {
    color: #555 !important;
    font-size: 0.75rem !important;
    letter-spacing: 1px !important;
}

.insight-box {
    background-color: #161616;
    border-left: 3px solid #c9f31d;
    padding: 1rem 1.5rem;
    border-radius: 0 4px 4px 0;
    margin: 0.5rem 0;
}
.insight-box p { margin: 0 !important; color: #e0e0e0 !important; }

.ai-box {
    background-color: #111;
    border: 1px solid #2a2a2a;
    border-top: 3px solid #c9f31d;
    border-radius: 4px;
    padding: 1.5rem 2rem;
    margin: 1rem 0;
}
.ai-box .ai-label {
    font-family: 'Barlow Condensed', sans-serif;
    font-size: 0.65rem;
    letter-spacing: 4px;
    text-transform: uppercase;
    color: #c9f31d;
    margin-bottom: 0.75rem;
}
.ai-box p {
    color: #d0d0d0 !important;
    font-size: 1rem !important;
    line-height: 1.8 !important;
    font-weight: 300 !important;
}

.stButton > button {
    background-color: #c9f31d !important;
    color: #0e0e0e !important;
    font-family: 'Barlow Condensed', sans-serif !important;
    font-size: 1rem !important;
    font-weight: 700 !important;
    letter-spacing: 2px !important;
    text-transform: uppercase !important;
    border: none !important;
    border-radius: 3px !important;
    padding: 0.6rem 2rem !important;
}
.stButton > button:hover {
    background-color: #d8ff2a !important;
}
</style>
""", unsafe_allow_html=True)

# ── Load data ────────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    players = pd.read_csv("data/atp_players.csv", encoding="latin-1")
    players.columns = ["player_id", "first_name", "last_name", "hand",
                       "birth_date", "country_code", "height", "wikidata_id"]
    players["full_name"] = players["first_name"] + " " + players["last_name"]
    players["player_id"] = players["player_id"].astype(str)
    players["height"] = pd.to_numeric(players["height"], errors="coerce")

    def load_rankings(path):
        df = pd.read_csv(path, header=None,
                         names=["ranking_date", "rank", "player_id", "points"],
                         low_memory=False)
        df = df[df["ranking_date"] != "ranking_date"]
        df["ranking_date"] = df["ranking_date"].astype(str)
        df["rank"] = pd.to_numeric(df["rank"], errors="coerce")
        df["points"] = pd.to_numeric(df["points"], errors="coerce")
        df["player_id"] = df["player_id"].astype(str)
        return df

    r10s = load_rankings("data/atp_rankings_10s.csv")
    r20s = load_rankings("data/atp_rankings_20s.csv")
    rcur = load_rankings("data/atp_rankings_current.csv")

    rankings = pd.concat([r10s, r20s, rcur], ignore_index=True)
    rankings = rankings.dropna(subset=["rank"])
    rankings["year"] = rankings["ranking_date"].str[:4]
    return players, rankings

players, rankings = load_data()

def calculate_age(birth_date_str, reference_year):
    try:
        birth_date = datetime.strptime(str(int(birth_date_str)), "%Y%m%d")
        return reference_year - birth_date.year
    except:
        return None

def cm_to_ft_in(cm):
    try:
        total_inches = float(cm) / 2.54
        feet = int(total_inches // 12)
        inches = round(total_inches % 12)
        return f"{feet}'" + f"{inches}''"
    except:
        return "N/A"

def get_top10(year_str, players_df, rankings_df):
    year_data = rankings_df[rankings_df["year"] == year_str]
    if year_data.empty:
        return None
    last_date = sorted(year_data["ranking_date"].unique())[-1]
    top10 = year_data[year_data["ranking_date"] == last_date].sort_values("rank").head(10).copy()
    top10 = top10.merge(players_df, on="player_id", how="left")
    top10["age"] = top10["birth_date"].apply(lambda x: calculate_age(x, int(year_str)))
    top10["points"] = pd.to_numeric(top10["points"], errors="coerce")
    top10["height"] = pd.to_numeric(top10["height"], errors="coerce")
    return top10

# ── Claude API call ──────────────────────────────────────────────────────────
def generate_ai_analysis(year_a, year_b, top_a, top_b,
                          avg_age_a, avg_age_b,
                          avg_h_a, avg_h_b,
                          avg_p_a, avg_p_b):

    players_a = ", ".join(top_a["full_name"].dropna().tolist())
    players_b = ", ".join(top_b["full_name"].dropna().tolist())

    prompt = f"""You are an expert tennis analyst writing for a sports data product.

Compare the ATP top 10 from {year_a} vs {year_b} and write a compelling 3-4 sentence analysis.

Data:
- {year_a} top 10: {players_a}
- {year_a} avg age: {avg_age_a:.1f} | avg height: {avg_h_a:.1f}cm | avg points: {avg_p_a:,.0f}

- {year_b} top 10: {players_b}
- {year_b} avg age: {avg_age_b:.1f} | avg height: {avg_h_b:.1f}cm | avg points: {avg_p_b:,.0f}

Write a sharp, insightful paragraph that:
- explains what changed and why it matters
- references specific players by name where relevant
- reads like a smart sports journalist, not a data report
- is direct and confident, no hedging

Return only the paragraph, no titles or labels."""

    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=300,
        messages=[{"role": "user", "content": prompt}]
    )
    return message.content[0].text

# ── Sidebar ───────────────────────────────────────────────────────────────────
available_years = sorted(rankings["year"].unique())
available_years = [y for y in available_years if y.isdigit() and 2010 <= int(y) <= 2024]

st.sidebar.markdown("## ⚙️ Settings")
year_a = st.sidebar.selectbox("Year A — Earlier", available_years, index=available_years.index("2015"))
year_b = st.sidebar.selectbox("Year B — Later", available_years, index=available_years.index("2024"))
st.sidebar.markdown("---")
st.sidebar.markdown(
    "<p style='font-size:0.8rem; color:#666; line-height:1.6;'>"
    "Data from Jeff Sackmann's open-source ATP dataset. "
    "Rankings taken from the final week of each year.</p>",
    unsafe_allow_html=True
)

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("# 🎾 Tennis Era Explorer")
st.markdown(
    "<p style='font-size:1.1rem; color:#888; margin-top:-0.5rem;'>"
    "Has the profile of a top ATP player changed over time? "
    "Pick any two years and find out.</p>",
    unsafe_allow_html=True
)
st.markdown("---")

if year_a == year_b:
    st.warning("Please select two different years.")
    st.stop()

top_a = get_top10(year_a, players, rankings)
top_b = get_top10(year_b, players, rankings)

if top_a is None or top_b is None:
    st.error("No data found for one of those years.")
    st.stop()

# ── Player tables ─────────────────────────────────────────────────────────────
st.markdown(f"## Top 10 Players — {year_a} vs {year_b}")

col1, col2 = st.columns(2)

def show_table(df, year):
    display = df[["rank", "full_name", "age", "height", "points"]].copy()
    display["Height"] = display["height"].apply(cm_to_ft_in)
    display = (
        display[["rank", "full_name", "age", "Height", "points"]]
        .rename(columns={"full_name": "Player", "age": "Age", "points": "Points"})
        .set_index("rank")
    )
    st.markdown(f"### {year}")
    st.dataframe(display, use_container_width=True, height=385)

with col1:
    show_table(top_a, year_a)
with col2:
    show_table(top_b, year_b)

# ── Metrics ───────────────────────────────────────────────────────────────────
st.markdown("## Profile Shift")

avg_age_a = top_a["age"].mean()
avg_age_b = top_b["age"].mean()
avg_h_a   = top_a["height"].mean()
avg_h_b   = top_b["height"].mean()
avg_p_a   = top_a["points"].mean()
avg_p_b   = top_b["points"].mean()

m1, m2, m3 = st.columns(3)
m1.metric("Avg Age",            f"{avg_age_b:.1f} yrs", f"{avg_age_b - avg_age_a:+.1f} vs {year_a}")
m2.metric("Avg Height",         f"{cm_to_ft_in(avg_h_b)}",    f"{avg_h_b - avg_h_a:+.1f} vs {year_a}")
m3.metric("Avg Ranking Points", f"{avg_p_b:,.0f}",      f"{avg_p_b - avg_p_a:+,.0f} vs {year_a}")

# ── Quick insights ────────────────────────────────────────────────────────────
st.markdown("## What This Means")

age_diff = avg_age_b - avg_age_a
h_diff   = avg_h_b - avg_h_a
pts_diff = avg_p_b - avg_p_a

insights = []
if abs(age_diff) >= 1:
    direction = "younger" if age_diff < 0 else "older"
    insights.append(
        f"The {year_b} top 10 is <strong>{abs(age_diff):.1f} years {direction}</strong> on average — "
        + ("a new generation has arrived." if age_diff < 0 else "experience is dominating the tour.")
    )
if abs(h_diff) >= 1:
    direction = "taller" if h_diff > 0 else "shorter"
    insights.append(
        f"They are <strong>{cm_to_ft_in(avg_h_b)} avg height ({"taller" if h_diff > 0 else "shorter"})</strong> — "
        + ("the game increasingly favours bigger servers and longer reach." if h_diff > 0
           else "agility is gaining an edge over raw power.")
    )
if abs(pts_diff) > 500:
    direction = "higher" if pts_diff > 0 else "lower"
    insights.append(
        f"Average points are <strong>{direction}</strong> in {year_b} — "
        + ("the gap between elite and everyone else has grown." if pts_diff > 0
           else "the top of the tour is more compressed and competitive than ever.")
    )

if insights:
    for insight in insights:
        st.markdown(f'<div class="insight-box"><p>{insight}</p></div>', unsafe_allow_html=True)
else:
    st.markdown('<div class="insight-box"><p>These two eras look surprisingly similar across all three metrics.</p></div>', unsafe_allow_html=True)

# ── AI Analysis ───────────────────────────────────────────────────────────────
st.markdown("## AI Analysis")

# Reset analysis when years change
cache_key = f"{year_a}_{year_b}"
if "analysis_cache_key" not in st.session_state or st.session_state.analysis_cache_key != cache_key:
    st.session_state.analysis_text = None
    st.session_state.analysis_cache_key = cache_key

if st.button("✦ Generate AI Analysis"):
    with st.spinner("Analysing era data..."):
        try:
            analysis = generate_ai_analysis(
                year_a, year_b, top_a, top_b,
                avg_age_a, avg_age_b,
                avg_h_a, avg_h_b,
                avg_p_a, avg_p_b
            )
            st.session_state.analysis_text = analysis
        except Exception as e:
            st.error(f"Could not generate analysis: {e}")

if st.session_state.get("analysis_text"):
    st.markdown(
        f'<div class="ai-box">'
        f'<div class="ai-label">✦ AI Analysis — {year_a} vs {year_b}</div>'
        f'<p>{st.session_state.analysis_text}</p>'
        f'</div>',
        unsafe_allow_html=True
    )

# ── Charts ─────────────────────────────────────────────────────────────────────
st.markdown("## Charts")

mpl.rcParams.update({
    "figure.facecolor": "#0e0e0e",
    "axes.facecolor":   "#0e0e0e",
    "axes.edgecolor":   "#2a2a2a",
    "axes.labelcolor":  "#888888",
    "xtick.color":      "#888888",
    "ytick.color":      "#888888",
    "text.color":       "#f0f0f0",
    "grid.color":       "#1e1e1e",
    "grid.linewidth":   0.5,
})

fig, axes = plt.subplots(1, 3, figsize=(14, 4.5))
fig.patch.set_facecolor("#0e0e0e")
fig.suptitle(f"{year_a}  →  {year_b}   |   Top 10 ATP Players",
             fontsize=11, color="#666", fontweight="normal", y=1.02)

bar_colors = ["#3a3a3a", "#c9f31d"]
categories = [year_a, year_b]

chart_data = [
    (avg_age_a, avg_age_b, "Average Age",        "Years",  False),
    (avg_h_a,   avg_h_b,   "Average Height",     "ft/in",  True),
    (avg_p_a,   avg_p_b,   "Avg Ranking Points", "Points", False),
]

for ax, (val_a, val_b, title, ylabel, is_height) in zip(axes, chart_data):
    vals = (val_a, val_b)
    bars = ax.bar(categories, vals, color=bar_colors, width=0.45, zorder=3)
    ax.set_title(title, fontsize=10, color="#888", pad=10, fontweight="normal")
    ax.set_ylabel(ylabel, fontsize=8, color="#666")
    ax.set_ylim(max(0, min(vals) * 0.92), max(vals) * 1.08)
    ax.yaxis.grid(True, zorder=0)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_visible(False)
    ax.tick_params(axis="both", labelsize=9)
    for bar, val in zip(bars, vals):
        label = cm_to_ft_in(val) if is_height else (f"{val:.1f}" if val < 1000 else f"{val:,.0f}")
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + max(vals) * 0.01,
                label, ha="center", va="bottom", fontsize=9, color="#f0f0f0", fontweight="bold")
    if is_height:
        ax.set_yticklabels([])

plt.tight_layout()
st.pyplot(fig)

# ── Raw data expander ─────────────────────────────────────────────────────────
with st.expander("View raw data"):
    c1, c2 = st.columns(2)
    with c1:
        st.caption(f"{year_a} — ranking date: {sorted(rankings[rankings['year'] == year_a]['ranking_date'].unique())[-1]}")
    with c2:
        st.caption(f"{year_b} — ranking date: {sorted(rankings[rankings['year'] == year_b]['ranking_date'].unique())[-1]}")

st.markdown("---")
st.caption("Data: Jeff Sackmann / tennis_atp on GitHub · Built with Python & Streamlit · AI analysis powered by Claude")
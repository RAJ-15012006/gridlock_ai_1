# app.py
import streamlit as st
import pandas as pd
import folium
from folium.plugins import HeatMap
from streamlit_folium import st_folium
import plotly.express as px
import plotly.graph_objects as go
import os

st.set_page_config(
    page_title="ParkSense AI - Bengaluru",
    page_icon="🚨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── CUSTOM CSS ─────────────────────────────────────────────
st.markdown("""
<style>
    :root {
        --bg: #0b1120;
        --surface: #101a31;
        --surface-2: #0f172a;
        --surface-3: #14213d;
        --text: #eef6ff;
        --muted: #94a3b8;
        --border: rgba(148, 163, 184, 0.12);
        --primary: #ff5a5f;
        --primary-2: #ff8a3d;
        --accent: #38bdf8;
        --success: #22c55e;
        --warning: #f59e0b;
    }

    html, body, [class*="css"] {
        background: var(--bg);
    }

    .stApp {
        background:
            radial-gradient(circle at top, rgba(255, 90, 95, 0.08), transparent 18%),
            linear-gradient(180deg, #0f172a 0%, #0b1120 100%);
    }

    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 3rem;
    }

    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f172a, #111827);
        border-right: 1px solid var(--border);
    }

    [data-testid="stSidebar"] section {
        background: transparent;
    }

    h1, h2, h3, h4 {
        color: var(--text) !important;
        letter-spacing: 0.2px;
    }

    p, li, span, div {
        color: var(--muted);
    }

    div[data-testid="stMetric"] {
        background: linear-gradient(180deg, rgba(17, 24, 39, 0.98), rgba(15, 23, 42, 0.98));
        border: 1px solid var(--border);
        border-radius: 16px;
        padding: 0.8rem 1rem;
        box-shadow: inset 0 1px 0 rgba(255,255,255,0.03);
    }

    div[data-testid="stMetricLabel"] {
        color: var(--muted) !important;
    }

    div[data-testid="stMetricValue"] {
        font-size: 1.8rem !important;
        color: var(--text) !important;
    }

    div[data-testid="stMetricDelta"] {
        color: var(--warning) !important;
    }

    .section-card {
        background: linear-gradient(180deg, rgba(15, 23, 42, 0.96), rgba(17, 24, 39, 0.98));
        border: 1px solid var(--border);
        border-radius: 18px;
        padding: 1rem;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.18);
    }

    .app-hero {
        background: linear-gradient(90deg, rgba(255, 90, 95, 0.1), rgba(56, 189, 248, 0.06));
        border: 1px solid var(--border);
        border-radius: 18px;
        padding: 1rem 1.2rem;
        margin-bottom: 1rem;
    }

    div[data-testid="stDataFrame"] {
        border-radius: 14px;
        overflow: hidden;
        border: 1px solid var(--border);
    }

    .stPlotlyChart {
        filter: drop-shadow(0 15px 25px rgba(0,0,0,0.18));
    }

    .stButton > button {
        background: linear-gradient(90deg, var(--primary), var(--primary-2));
        color: white;
        border: none;
        border-radius: 999px;
        padding: 0.45rem 1rem;
    }
</style>
""", unsafe_allow_html=True)

# ── LOAD DATA ─────────────────────────────────────────────
@st.cache_data
def load_data():
    violations = pd.read_csv("cleaned_violations.csv.gz")
    stations   = pd.read_csv("station_scores.csv")
    junctions  = pd.read_csv("junction_summary.csv")
    trend      = pd.read_csv("daily_trend.csv")

    violations['created_datetime'] = pd.to_datetime(
        violations['created_datetime'], utc=True, errors='coerce'
    )
    trend['date'] = pd.to_datetime(trend['date'], errors='coerce')
    # FIX 1 — show only date, not full datetime
    trend['date'] = trend['date'].dt.date

    return violations, stations, junctions, trend

df, station_score, junction_impact, daily_trend = load_data()

# ── SIDEBAR ───────────────────────────────────────────────
current_dir = os.path.dirname(os.path.abspath(__file__))
st.sidebar.image(os.path.join(current_dir, "assets", "traffic_light.png"), width=120)
st.sidebar.title("🚨 ParkSense AI")
st.sidebar.markdown("**AI-driven Parking Intelligence**\nBengaluru Traffic Enforcement")
st.sidebar.divider()

page = st.sidebar.radio("Navigate", [
    "📊 Overview Dashboard",
    "🗺️ Hotspot Heatmap",
    "🏢 Zone Analysis",
    "⏰ Time Intelligence",
    "🎯 Enforcement Planner",
    "📈 Trend Analysis"
])
# FIX 2 — removed broken sidebar station filter

st.sidebar.write("")
st.sidebar.write("")
st.sidebar.divider()
st.sidebar.caption("Powered by")
st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/thumb/a/a6/Flipkart_logo.svg/200px-Flipkart_logo.svg.png", width=100)

# ── PAGE 1: OVERVIEW ──────────────────────────────────────
if page == "📊 Overview Dashboard":
    st.markdown("""
    <div class="app-hero">
        <h1 style="margin:0 0 0.25rem 0;">🚨 ParkSense AI</h1>
        <p style="margin:0; color:#cbd5e1;">Bengaluru Traffic Police · AI-Driven Enforcement Dashboard</p>
    </div>
    """, unsafe_allow_html=True)
    st.divider()

    # KPI Row
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("Total Violations", f"{len(df):,}")
    with col2:
        st.metric("Hotspot Clusters", "62")
    with col3:
        gap = int((~df['validated']).sum())
        st.metric("Enforcement Gap", f"{gap:,}", delta="-61.3% unresolved", delta_color="inverse")
    with col4:
        st.metric("Metro Zone Violations", f"{df['near_metro'].sum():,}")
    with col5:
        st.metric("Commercial Violations", f"{df['near_commercial'].sum():,}")

    st.divider()

    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.subheader("🏆 Top 10 High Risk Stations")
        top10 = station_score.head(10)
        fig = px.bar(
            top10,
            x='congestion_score',
            y='police_station',
            orientation='h',
            color='congestion_score',
            color_continuous_scale='Reds',
            labels={'congestion_score': 'Congestion Score', 'police_station': 'Station'}
        )
        fig.update_layout(
            plot_bgcolor='#0b1120',
            paper_bgcolor='#0b1120',
            font_color='#e5eefc',
            showlegend=False,
            yaxis={'categoryorder': 'total ascending'},
            margin=dict(l=10, r=10, t=10, b=10)
        )
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.subheader("🚗 Violation Type Breakdown")
        viol_counts = df['primary_violation'].value_counts().head(8)
        fig2 = px.pie(
            values=viol_counts.values,
            names=viol_counts.index,
            hole=0.45,
            color_discrete_sequence=px.colors.sequential.Reds_r
        )
        fig2.update_layout(
            plot_bgcolor='#0b1120',
            paper_bgcolor='#0b1120',
            font_color='#e5eefc',
            margin=dict(l=10, r=10, t=10, b=10)
        )
        st.plotly_chart(fig2, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.subheader("⚠️ Enforcement Gap by Station")
    gap_df = station_score[['police_station', 'total_violations',
                              'enforcement_gap', 'congestion_score']].copy()
    gap_df['gap_pct'] = (gap_df['enforcement_gap'] / gap_df['total_violations'] * 100).round(1)
    gap_df = gap_df.sort_values('gap_pct', ascending=False).head(15)
    gap_df.columns = ['Station', 'Total', 'Unresolved', 'Score', 'Gap %']
    st.dataframe(gap_df, use_container_width=True, hide_index=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ── PAGE 2: HEATMAP ───────────────────────────────────────
elif page == "🗺️ Hotspot Heatmap":
    st.title("🗺️ Parking Violation Heatmap — Bengaluru")
    st.markdown("Red = high violation density | Markers = top junctions with capacity impact")

    col1, col2 = st.columns([3, 1])
    with col2:
        map_type = st.radio("Map Layer", ["Violation Density", "Congestion Impact"])
        sample_size = st.slider("Data Points", 10000, 100000, 50000, 10000)

    with col1:
        m = folium.Map(
            location=[12.9716, 77.5946],
            zoom_start=12,
            tiles='CartoDB dark_matter'
        )

        if map_type == "Violation Density":
            sample = df[['latitude', 'longitude', 'vehicle_severity']].dropna().sample(
                min(sample_size, len(df)), random_state=42).copy()
            # Normalize severity to [0.1, 1.0] to prevent Leaflet.heat saturation
            max_sev = sample['vehicle_severity'].max() if not sample['vehicle_severity'].empty else 1
            min_sev = sample['vehicle_severity'].min() if not sample['vehicle_severity'].empty else 0
            if max_sev > min_sev:
                sample['weight'] = 0.1 + 0.9 * (sample['vehicle_severity'] - min_sev) / (max_sev - min_sev)
            else:
                sample['weight'] = 1.0

            HeatMap(
                sample[['latitude', 'longitude', 'weight']].values.tolist(),
                radius=10, blur=15,
                gradient={0.2: 'blue', 0.4: 'lime', 0.6: 'orange', 1.0: 'red'}
            ).add_to(m)
        else:
            station_geo = df.dropna(subset=['latitude', 'longitude']).merge(
                station_score[['police_station', 'congestion_score']], on='police_station')
            geo_sample = station_geo.dropna(subset=['congestion_score']).sample(
                min(sample_size, len(station_geo)), random_state=42).copy()
            # Normalize congestion_score to [0.1, 1.0] to show distinct relative impact
            max_cong = geo_sample['congestion_score'].max() if not geo_sample['congestion_score'].empty else 1
            min_cong = geo_sample['congestion_score'].min() if not geo_sample['congestion_score'].empty else 0
            if max_cong > min_cong:
                geo_sample['weight'] = 0.1 + 0.9 * (geo_sample['congestion_score'] - min_cong) / (max_cong - min_cong)
            else:
                geo_sample['weight'] = 1.0

            HeatMap(
                geo_sample[['latitude', 'longitude', 'weight']].values.tolist(),
                radius=15, blur=20,
                gradient={0.2: 'green', 0.5: 'yellow', 0.8: 'orange', 1.0: 'red'}
            ).add_to(m)

        for _, row in junction_impact.head(20).iterrows():
            color = 'red' if row['capacity_reduction_pct'] > 20 else \
                    'orange' if row['capacity_reduction_pct'] > 15 else 'green'
            folium.CircleMarker(
                location=[row['lat'], row['lon']],
                radius=8, color=color, fill=True, fill_opacity=0.8,
                popup=folium.Popup(
                    f"<b>{row['junction_name']}</b><br>"
                    f"Violations: {row['total_violations']:,}<br>"
                    f"Capacity Reduction: {row['capacity_reduction_pct']}%<br>"
                    f"Zone: {row['zone_type']}",
                    max_width=250
                )
            ).add_to(m)

        st_folium(m, width=900, height=600)

# ── PAGE 3: ZONE ANALYSIS ─────────────────────────────────
elif page == "🏢 Zone Analysis":
    st.title("🏢 Zone-wise Violation Analysis")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("🚇 Metro Zone", f"{df['near_metro'].sum():,}")
    with col2:
        st.metric("🏪 Commercial Zone", f"{df['near_commercial'].sum():,}")
    with col3:
        st.metric("🎪 Event Zone", f"{df['near_event'].sum():,}")

    st.divider()
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Zone Distribution")
        zone_counts = df['zone_type'].value_counts().reset_index()
        zone_counts.columns = ['Zone', 'Count']
        color_map = {
            'Commercial Zone': '#ff4b4b',
            'Metro Zone': '#ff8800',
            'Event Zone': '#ffdd00',
            'General': '#1a1a2e'
        }
        zone_counts['color'] = zone_counts['Zone'].map(color_map)
        fig = px.pie(
            zone_counts, values='Count', names='Zone',
            hole=0.4,
            color='Zone',
            color_discrete_map=color_map
        )
        fig.update_layout(paper_bgcolor='#0e1117', font_color='white')
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Top Junctions by Zone")
        zone_filter = st.selectbox("Select Zone", ['All', 'Commercial Zone', 'Metro Zone', 'Event Zone', 'General'])
        if zone_filter == 'All':
            jdf = junction_impact.head(15)
        else:
            jdf = junction_impact[junction_impact['zone_type'] == zone_filter].head(15)

        fig2 = px.bar(
            jdf, x='total_violations', y='junction_name',
            orientation='h', color='capacity_reduction_pct',
            color_continuous_scale='Reds',
            labels={'total_violations': 'Violations', 'junction_name': 'Junction'}
        )
        fig2.update_layout(
            paper_bgcolor='#0e1117', plot_bgcolor='#0e1117',
            font_color='white', yaxis={'categoryorder': 'total ascending'}
        )
        st.plotly_chart(fig2, use_container_width=True)

# ── PAGE 4: TIME INTELLIGENCE ─────────────────────────────
elif page == "⏰ Time Intelligence":
    st.title("⏰ Time-based Violation Patterns")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Violations by Hour (IST)")
        hourly = df['hour_IST'].value_counts().sort_index().reset_index()
        hourly.columns = ['Hour', 'Count']
        fig = px.bar(
            hourly, x='Hour', y='Count',
            color='Count', color_continuous_scale='Reds'
        )
        fig.update_layout(paper_bgcolor='#0e1117', plot_bgcolor='#0e1117', font_color='white')
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Violations by Day of Week")
        day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        daily = df['day_of_week'].value_counts().reindex(day_order).reset_index()
        daily.columns = ['Day', 'Count']
        fig2 = px.bar(
            daily, x='Day', y='Count',
            color='Count', color_continuous_scale='Oranges'
        )
        fig2.update_layout(paper_bgcolor='#0e1117', plot_bgcolor='#0e1117', font_color='white')
        st.plotly_chart(fig2, use_container_width=True)

    st.subheader("Monthly Trend")
    month_order = ['November', 'December', 'January', 'February', 'March', 'April']
    monthly = df['month'].value_counts().reindex(month_order).reset_index()
    monthly.columns = ['Month', 'Count']
    fig3 = px.line(
        monthly, x='Month', y='Count',
        markers=True, line_shape='spline',
        color_discrete_sequence=['#ff4b4b']
    )
    fig3.update_layout(paper_bgcolor='#0e1117', plot_bgcolor='#0e1117', font_color='white')
    st.plotly_chart(fig3, use_container_width=True)

# ── PAGE 5: ENFORCEMENT PLANNER ───────────────────────────
elif page == "🎯 Enforcement Planner":
    st.title("🎯 AI Enforcement Recommendation Engine")
    st.markdown("Select a station to get data-driven patrol deployment recommendations")

    station_name = st.selectbox(
        "Select Police Station",
        sorted(station_score['police_station'].tolist())
    )

    if station_name:
        row = station_score[station_score['police_station'] == station_name].iloc[0]
        station_df = df[df['police_station'] == station_name]

        score = row['congestion_score']
        if score >= 60:   priority, color, units = "CRITICAL", "🔴", 5
        elif score >= 40: priority, color, units = "HIGH",     "🟠", 3
        elif score >= 20: priority, color, units = "MEDIUM",   "🟡", 2
        else:             priority, color, units = "LOW",      "🟢", 1

        top_hours = station_df['hour_IST'].value_counts()
        daytime = top_hours[top_hours.index.isin(range(6, 22))]
        peak_hour = int(daytime.idxmax()) if not daytime.empty else int(top_hours.idxmax())

        st.markdown(f"## {color} Priority: {priority}")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Congestion Score", f"{score}/100")
        with col2:
            st.metric("Patrol Units Needed", units)
        with col3:
            st.metric("Deploy At", f"{peak_hour}:00 - {peak_hour+2}:00 IST")
        with col4:
            st.metric("Unresolved Cases", f"{int(row['enforcement_gap']):,}")

        st.divider()
        col1, col2 = st.columns(2)
        with col1:
            st.info(f"**Peak Day:** {station_df['day_of_week'].mode()[0]}")
            st.info(f"**Top Violation:** {station_df['primary_violation'].mode()[0]}")
            st.info(f"**Zone Type:** {station_df['zone_type'].mode()[0]}")
            st.info(f"**Junction Violations:** {int(row['junction_violations']):,}")

        with col2:
            st.subheader("Hourly Pattern")
            hourly_s = station_df['hour_IST'].value_counts().sort_index().reset_index()
            hourly_s.columns = ['Hour', 'Count']
            fig = px.bar(hourly_s, x='Hour', y='Count',
                        color='Count', color_continuous_scale='Reds')
            fig.update_layout(paper_bgcolor='#0e1117', plot_bgcolor='#0e1117', font_color='white')
            st.plotly_chart(fig, use_container_width=True)

        st.subheader("All Stations — Priority Rankings")
        rec_df = station_score[['police_station', 'total_violations',
                                  'junction_violations', 'enforcement_gap',
                                  'congestion_score']].copy()
        rec_df['Priority'] = rec_df['congestion_score'].apply(
            lambda s: 'CRITICAL' if s >= 60 else 'HIGH' if s >= 40 else 'MEDIUM' if s >= 20 else 'LOW')
        rec_df['Patrol Units'] = rec_df['congestion_score'].apply(
            lambda s: 5 if s >= 60 else 3 if s >= 40 else 2 if s >= 20 else 1)
        st.dataframe(rec_df, use_container_width=True, hide_index=True)

# ── PAGE 6: TREND ANALYSIS ────────────────────────────────
elif page == "📈 Trend Analysis":
    st.title("📈 7-Day Rolling Violation Trend")

    top_stations = station_score.head(5)['police_station'].tolist()
    selected = st.multiselect("Select Stations", top_stations, default=top_stations[:3])

    if selected:
        trend_filtered = daily_trend[daily_trend['police_station'].isin(selected)]
        fig = px.line(
            trend_filtered, x='date', y='7day_avg',
            color='police_station', line_shape='spline',
            labels={'7day_avg': '7-Day Avg Violations', 'date': 'Date'},
            color_discrete_sequence=px.colors.qualitative.Bold
        )
        fig.update_layout(
            paper_bgcolor='#0e1117', plot_bgcolor='#0e1117',
            font_color='white', legend_title='Station'
        )
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Raw Daily Data")
    st.dataframe(
        daily_trend[daily_trend['police_station'].isin(selected)],
        use_container_width=True, hide_index=True
    )
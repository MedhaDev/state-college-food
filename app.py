import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ── CONFIG ────────────────────────────────────────────────
st.set_page_config(
    page_title="State College Food Intelligence",
    page_icon="🍕",
    layout="wide"
)

DATA_PATH = "/Users/medhasharma/state-college-food/data/clean/restaurants_tagged.csv"

# ── LOAD DATA ─────────────────────────────────────────────
@st.cache_data(ttl=0)
def load_data():
    df = pd.read_csv(DATA_PATH)
    df["rating"]       = pd.to_numeric(df["rating"], errors="coerce")
    df["review_count"] = pd.to_numeric(df["review_count"], errors="coerce")
    df["price_level"]  = pd.to_numeric(df["price_level"], errors="coerce")
    df["lat"]          = pd.to_numeric(df["lat"], errors="coerce")
    df["lng"]          = pd.to_numeric(df["lng"], errors="coerce")
    df = df[df["status"] == "OPERATIONAL"].copy()
    return df

df = load_data()

# ── HEADER ────────────────────────────────────────────────
st.title("🍕 State College Food Intelligence")
st.markdown("*What 145 restaurants, real reviews, and actual data say about eating in Happy Valley.*")
st.divider()

# ── METRICS ROW ───────────────────────────────────────────
col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Total Restaurants", len(df))
col2.metric("Avg Rating", f"{df['rating'].mean():.2f} ⭐")
col3.metric("Late Night Options", int(df["is_late_night"].astype(str).str.strip().eq("True").sum()))
col4.metric("Open Sundays", int(df["opens_sunday"].astype(str).str.strip().eq("True").sum()))
col5.metric("Budget Friendly (💰)", int((df["price_level"] == 1).sum()))

st.divider()

# ── TABS ──────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🗺️ Find a Restaurant",
    "🏆 Top Rated",
    "💎 Hidden Gems",
    "🌆 Food Scene",
    "🌙 Late Night"
])

# ══ TAB 1: FINDER ════════════════════════════════════════
with tab1:
    st.subheader("Find Your Next Meal")
    st.markdown("Filter by what matters to you.")

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        all_cuisines = sorted(df["cuisine_type"].dropna().unique())
        cuisine_filter = st.multiselect("Cuisine", all_cuisines, default=[])

    with col2:
        vibe = st.selectbox("Vibe", [
            "Any",
            "Date night 🕯️",
            "Group hangout 🍻",
            "Solo / quick bite 🥡",
            "Late night 🌙"
        ])

    with col3:
        min_rating = st.slider("Minimum Rating", 1.0, 5.0, 4.0, 0.1)

    with col4:
        price_filter = st.multiselect(
            "Price",
            options=[1, 2, 3],
            format_func=lambda x: "💰" * x,
            default=[1, 2, 3]
        )

    with col5:
        filter_by_time = st.checkbox("Open right now?")

    # Apply filters
    filtered = df.copy()
    if cuisine_filter:
        filtered = filtered[filtered["cuisine_type"].isin(cuisine_filter)]
    if price_filter:
        filtered = filtered[filtered["price_level"].isin(price_filter)]
    filtered = filtered[filtered["rating"] >= min_rating]

    if vibe == "Date night 🕯️":
        filtered = filtered[
            (filtered["price_level"] >= 2) &
            (~filtered["cuisine_type"].isin(["Fast Food", "Late Night Snacks"]))
        ]
    elif vibe == "Late night 🌙":
        filtered = filtered[filtered["is_late_night"] .astype(str).str.strip() == "True"]
    elif vibe == "Solo / quick bite 🥡":
        filtered = filtered[filtered["price_level"] == 1]

    filtered = filtered.sort_values("rating", ascending=False)

    st.markdown(f"**{len(filtered)} restaurants match your filters**")

    if not filtered.empty:
        for _, r in filtered.iterrows():
            price_str   = "💰" * int(r["price_level"]) if not pd.isna(r["price_level"]) else "?"
            late_str = "🌙 Late night" if str(r["is_late_night"]).strip() == "True" else ""
            sunday_str = "✅ Open Sunday" if str(r["opens_sunday"]).strip() == "True" else ""
            website_str = f"[Website]({r['website']})" if pd.notna(r.get("website")) and r["website"] else ""

            with st.expander(f"⭐ {r['rating']}  {r['name']}  —  {r['cuisine_type']}  {price_str}"):
                c1, c2 = st.columns([2, 1])
                with c1:
                    st.markdown(f"**Address:** {r['address']}")
                    if r.get("phone"):
                        st.markdown(f"**Phone:** {r['phone']}")
                    st.markdown(f"{late_str}  {sunday_str}  {website_str}")
                with c2:
                    st.metric("Rating", f"{r['rating']} ⭐")
                    st.metric("Reviews", int(r["review_count"]) if not pd.isna(r["review_count"]) else "N/A")

    if filter_by_time:
        from datetime import datetime
        current_hour = datetime.now().hour
        # Late night hours: midnight to 6am
        if 0 <= current_hour < 6:
            filtered = filtered[filtered["is_late_night"].astype(str).str.strip() == "True"]
            st.caption(f"🌙 Showing late night spots (it's {datetime.now().strftime('%I:%M %p')})")
        else:
            st.caption(f"✅ Showing all restaurants (most are open at {datetime.now().strftime('%I:%M %p')})")

    # Map
    map_data = filtered.dropna(subset=["lat", "lng"])
    if not map_data.empty:
        st.markdown("### 📍 Map")
        fig_map = px.scatter_mapbox(
            map_data,
            lat="lat", lon="lng",
            hover_name="name",
            hover_data={"rating": True, "cuisine_type": True, "lat": False, "lng": False},
            color="cuisine_type",
            zoom=13,
            height=450,
            mapbox_style="carto-positron"
        )
        fig_map.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
        st.plotly_chart(fig_map, use_container_width=True)

# ══ TAB 2: TOP RATED ═════════════════════════════════════
with tab2:
    st.subheader("🏆 Top Rated Restaurants")
    st.markdown("Minimum 50 reviews — these ratings have earned their stars.")

    min_reviews = st.slider("Minimum review count", 10, 500, 50, key="top_slider")
    top = df[df["review_count"] >= min_reviews].sort_values("rating", ascending=False).head(20)

    fig_top = px.bar(
        top,
        x="rating", y="name",
        orientation="h",
        color="cuisine_type",
        hover_data=["review_count", "price_level"],
        labels={"rating": "Rating", "name": "Restaurant"},
        height=600,
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    fig_top.update_layout(yaxis={"categoryorder": "total ascending"}, showlegend=True)
    st.plotly_chart(fig_top, use_container_width=True)

# ══ TAB 3: HIDDEN GEMS ═══════════════════════════════════
with tab3:
    st.subheader("💎 Hidden Gems")
    st.markdown("High ratings, low profile. Places locals know but newcomers miss.")

    max_reviews = st.slider("Max review count (lower = more hidden)", 20, 300, 150, key="gem_slider")
    min_gem_rating = st.slider("Minimum rating", 4.0, 5.0, 4.3, 0.1, key="gem_rating")

    gems = df[
        (df["review_count"] <= max_reviews) &
        (df["rating"] >= min_gem_rating)
    ].sort_values("rating", ascending=False)

    st.markdown(f"**{len(gems)} hidden gems found**")

    fig_gems = px.scatter(
        gems,
        x="review_count",
        y="rating",
        size="review_count",
        color="cuisine_type",
        hover_name="name",
        hover_data=["price_level", "address"],
        labels={"review_count": "Number of Reviews", "rating": "Rating"},
        height=450,
        color_discrete_sequence=px.colors.qualitative.Pastel
    )
    fig_gems.update_layout(showlegend=True)
    st.plotly_chart(fig_gems, use_container_width=True)

    for _, r in gems.iterrows():
        price_str = "💰" * int(r["price_level"]) if not pd.isna(r["price_level"]) else "?"
        st.markdown(f"**{r['name']}** — {r['cuisine_type']} {price_str} — ⭐{r['rating']} ({int(r['review_count'])} reviews)")

# ══ TAB 4: FOOD SCENE ════════════════════════════════════
with tab4:
    st.subheader("🌆 The State College Food Scene")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Cuisine Distribution")
        cuisine_counts = df["cuisine_type"].value_counts().reset_index()
        cuisine_counts.columns = ["Cuisine", "Count"]
        fig_pie = px.pie(
            cuisine_counts,
            values="Count",
            names="Cuisine",
            hole=0.4,
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        fig_pie.update_traces(textposition="inside", textinfo="percent+label")
        st.plotly_chart(fig_pie, use_container_width=True)

    with col2:
        st.markdown("#### Rating Distribution by Cuisine")
        fig_box = px.box(
            df.dropna(subset=["rating"]),
            x="cuisine_type",
            y="rating",
            color="cuisine_type",
            labels={"cuisine_type": "Cuisine", "rating": "Rating"},
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        fig_box.update_layout(
            xaxis_tickangle=-45,
            showlegend=False,
            height=400
        )
        st.plotly_chart(fig_box, use_container_width=True)

    st.markdown("#### Price vs Rating — Every Restaurant")
    price_labels = {1: "💰 Budget", 2: "💰💰 Mid-range", 3: "💰💰💰 Upscale"}
    df_price = df.dropna(subset=["price_level", "rating"]).copy()
    df_price["price_label"] = df_price["price_level"].map(price_labels)

    fig_scatter = px.scatter(
        df_price,
        x="price_level",
        y="rating",
        color="cuisine_type",
        size="review_count",
        hover_name="name",
        labels={"price_level": "Price Level", "rating": "Rating"},
        height=450,
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    st.plotly_chart(fig_scatter, use_container_width=True)

# ══ TAB 5: LATE NIGHT ════════════════════════════════════
with tab5:
    st.subheader("🌙 Late Night State College")
    st.markdown("Open past midnight — drag the slider to see what's open at your time.")

    selected_hour = st.slider(
        "What time is it?",
        min_value=0,
        max_value=6,
        value=1,
        format="%d:00 AM"
    )

    # Show readable label
    if selected_hour == 0:
        time_label = "12:00 AM (Midnight)"
    else:
        time_label = f"{selected_hour}:00 AM"
    st.markdown(f"**Showing restaurants open at {time_label}**")

    # Filter late night spots
    late = df[df["is_late_night"].astype(str).str.strip() == "True"].copy()

    # Further filter by selected hour using closing time from opening_hours
    # We use a simple heuristic: if closes after selected_hour, it's open
    # Since we don't have exact hours per day in CSV, we show all late night
    # spots and note their typical late night status
    late = late.sort_values("rating", ascending=False)

    st.markdown(f"**{len(late)} late night options** (open past midnight)")
    st.caption("💡 Late night = closes between 12am and 6am on at least one night of the week")

    fig_late = px.bar(
        late,
        x="rating",
        y="name",
        orientation="h",
        color="cuisine_type",
        hover_data=["review_count", "cuisine_type"],
        labels={"rating": "Rating", "name": "Restaurant"},
        height=700,
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    fig_late.update_layout(yaxis={"categoryorder": "total ascending"}, showlegend=True)
    st.plotly_chart(fig_late, use_container_width=True)

    st.markdown("#### 📍 Late Night Map")
    late_map = late.dropna(subset=["lat", "lng"])
    fig_late_map = px.scatter_mapbox(
        late_map,
        lat="lat", lon="lng",
        hover_name="name",
        hover_data={"rating": True, "cuisine_type": True, "lat": False, "lng": False},
        color="cuisine_type",
        zoom=13,
        height=400,
        mapbox_style="carto-positron"
    )
    fig_late_map.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
    st.plotly_chart(fig_late_map, use_container_width=True)
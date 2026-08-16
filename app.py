import streamlit as st
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt

# ---------------------------------------------------------
# 1. PAGE CONFIGURATION & MODERN FRONTEND CSS
# ---------------------------------------------------------
st.set_page_config(
    page_title="Audio Asset Management System",
    page_icon="🎧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom High-End Front-End Styling (Dark Glassmorphism Theme)
st.markdown("""
<style>
    /* Main App Background */
    .stApp {
        background: #0d1117;
        color: #e6edf3;
    }
    
    /* Header Typography */
    .main-title {
        background: linear-gradient(90deg, #38bdf8 0%, #818cf8 50%, #c084fc 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.8rem;
        font-weight: 800;
        margin-bottom: 0px;
    }
    .sub-title {
        color: #8b949e;
        font-size: 1.1rem;
        margin-bottom: 25px;
    }
    
    /* Frontend Cards */
    .card-box {
        background-color: #161b22;
        border: 1px solid #30363d;
        border-radius: 12px;
        padding: 22px;
        margin-bottom: 20px;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.2);
    }
    
    /* Visual Badges */
    .badge-item {
        background: #1f2937;
        color: #38bdf8;
        border: 1px solid #38bdf8;
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 0.9rem;
        font-weight: 600;
        display: inline-block;
        margin: 4px;
    }
    
    .badge-sound {
        background: #1e1b4b;
        color: #a78bfa;
        border: 1px solid #818cf8;
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 0.9rem;
        font-weight: 600;
        display: inline-block;
        margin: 4px;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. REAL HD AUDIO ASSET LIBRARY (Direct CDN Web Stream URLs)
# ---------------------------------------------------------
REAL_SOUND_LIBRARY = {
    "Ambulance Siren": "https://actions.google.com/sounds/v1/emergency/ambulance_siren.ogg",
    "Heart Monitor Beep": "https://actions.google.com/sounds/v1/science/digital_beep.ogg",
    "Hospital Ambience": "https://actions.google.com/sounds/v1/ambiences/hospital_lobby.ogg",
    
    "Ocean Waves": "https://actions.google.com/sounds/v1/weather/ocean_waves_sea_swell.ogg",
    "Seagull Calls": "https://actions.google.com/sounds/v1/animals/birds_forest.ogg",
    "Wind Noise": "https://actions.google.com/sounds/v1/weather/wind_in_trees.ogg",
    
    "Jet Engine Takeoff": "https://actions.google.com/sounds/v1/transportation/jet_flyby.ogg",
    "Airport Terminal Ambience": "https://actions.google.com/sounds/v1/transportation/airplane_cabin.ogg",
    
    "Train Horn Whistle": "https://actions.google.com/sounds/v1/transportation/train_horn.ogg",
    "Tracks Rumble": "https://actions.google.com/sounds/v1/transportation/train_pass_by.ogg",
    
    "Drill Machinery": "https://actions.google.com/sounds/v1/tools/power_drill.ogg",
    "Metal Clang": "https://actions.google.com/sounds/v1/foley/metal_bar_drop.ogg",
    
    "Espresso Steam Wand": "https://actions.google.com/sounds/v1/household/steam_hiss.ogg",
    "Cafe Chatter": "https://actions.google.com/sounds/v1/ambiences/coffee_shop.ogg",
    
    "Car Horn Honking": "https://actions.google.com/sounds/v1/transportation/city_traffic_ambience.ogg",
    "Crowd Cheering": "https://actions.google.com/sounds/v1/crowds/stadium_cheer.ogg",
    
    "Default Ambient Sound": "https://actions.google.com/sounds/v1/ambiences/outdoor_ambience.ogg"
}


# ---------------------------------------------------------
# 3. KNOWLEDGE BASE & ONTOLOGY MAPPING
# ---------------------------------------------------------
@st.cache_data
def load_knowledge_base():
    places_context = {
        "Hospital": {
            "category": "Healthcare Facility",
            "things": ["Ambulance", "Stretcher", "Heart Monitor", "Medicines", "Oxygen Cylinder", "Defibrillator"],
            "sounds": ["Ambulance Siren", "Heart Monitor Beep", "Hospital Ambience"]
        },
        "Beach": {
            "category": "Coastal Natural Area",
            "things": ["Surfboard", "Lifeguard Tower", "Palm Trees", "Sandcastle", "Seagulls"],
            "sounds": ["Ocean Waves", "Seagull Calls", "Wind Noise"]
        },
        "Airport": {
            "category": "Aviation Hub",
            "things": ["Commercial Airplane", "Baggage Conveyor", "Passport Desk", "Metal Detector", "Runway Lights"],
            "sounds": ["Jet Engine Takeoff", "Airport Terminal Ambience"]
        },
        "Railway Station": {
            "category": "Transit Station",
            "things": ["Express Train", "Railway Tracks", "Ticket Counter", "Platform Bench"],
            "sounds": ["Train Horn Whistle", "Tracks Rumble"]
        },
        "Construction Site": {
            "category": "Industrial Zone",
            "things": ["Jackhammer", "Excavator", "Scaffolding", "Safety Helmet", "Tower Crane"],
            "sounds": ["Drill Machinery", "Metal Clang"]
        },
        "Coffee Shop": {
            "category": "Commercial Venue",
            "things": ["Espresso Machine", "Coffee Beans", "Billing Counter", "Pastry Tray"],
            "sounds": ["Espresso Steam Wand", "Cafe Chatter"]
        },
        "City Traffic": {
            "category": "Urban Transportation",
            "things": ["Passenger Cars", "Traffic Signals", "City Bus", "Pedestrian Crossing"],
            "sounds": ["Car Horn Honking"]
        },
        "Sports Stadium": {
            "category": "Entertainment Arena",
            "things": ["Football Pitch", "Floodlights", "VIP Stands", "Digital Scoreboard"],
            "sounds": ["Crowd Cheering"]
        }
    }
    
    catalog_data = []
    asset_id = 101
    for place, details in places_context.items():
        for sound_name in details["sounds"]:
            catalog_data.append({
                "Asset ID": f"AUD-{asset_id}",
                "Title": sound_name,
                "Place": place,
                "Category": details["category"],
                "Format": "MP3 Audio",
                "Bitrate": "320 kbps (HD Quality)"
            })
            asset_id += 1
            
    return places_context, pd.DataFrame(catalog_data)


# ---------------------------------------------------------
# 4. FRONTEND DASHBOARD APP LOGIC
# ---------------------------------------------------------
def main():
    # Header Section
    st.markdown('<p class="main-title">🎵 Audio Asset Management & Cataloguing System</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-title">Context-Aware Entity Discovery & Real-World Audio Asset Retrieval Platform</p>', unsafe_allow_html=True)

    places_db, catalog_df = load_knowledge_base()

    # Sidebar Navigation
    st.sidebar.markdown("## 🧭 Control Panel")
    app_mode = st.sidebar.radio(
        "Navigate Modules:",
        ["🔍 Contextual Asset Search", "📦 Digital Asset Catalog", "🕸️ Knowledge Graph Visualizer"]
    )
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📌 Active System Stats")
    st.sidebar.write(f"• **Indexed Locations:** {len(places_db)}")
    st.sidebar.write(f"• **Audio Library:** HD Real-world Sounds")

    # -----------------------------------------------------
    # MODULE 1: CONTEXTUAL ASSET SEARCH
    # -----------------------------------------------------
    if app_mode == "🔍 Contextual Asset Search":
        st.markdown("### 📍 Location Context Discovery Engine")
        
        c_sel, c_inp = st.columns([2, 1])
        with c_sel:
            selected_place = st.selectbox("Choose Preset Location:", list(places_db.keys()))
        with c_inp:
            custom_place = st.text_input("Or Type Any Location Name:", placeholder="e.g. Airport, Beach, Gym...")

        active_place = custom_place.strip().title() if custom_place else selected_place

        # Resolve location context
        if active_place in places_db:
            category = places_db[active_place]["category"]
            things = places_db[active_place]["things"]
            sounds = places_db[active_place]["sounds"]
        else:
            category = "Custom Query Environment"
            things = [f"{active_place} Main Sector", f"{active_place} Hardware Equipment", f"{active_place} Control Desk"]
            sounds = ["Default Ambient Sound"]
            st.info(f"✨ Generating dynamic contextual fallback mapping for **'{active_place}'**")

        st.markdown(f"#### 🏷️ Active Location Context: **{active_place}** (`{category}`)")
        st.markdown("---")

        col_left, col_right = st.columns([1, 1])

        # Physical Entities Column
        with col_left:
            st.markdown('<div class="card-box">', unsafe_allow_html=True)
            st.markdown("### 🧰 Related Physical Entities & Things")
            st.write("Identified items from entity mapping ontology:")
            for item in things:
                st.markdown(f'<span class="badge-item">📦 {item}</span>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        # Real Sound Assets Column
        with col_right:
            st.markdown('<div class="card-box">', unsafe_allow_html=True)
            st.markdown("### 🔊 HD Real Sound Effects")
            st.write("Retrieved high-quality audio files:")
            
            for sound_name in sounds:
                st.markdown(f"**🔊 {sound_name}**")
                # Fetch Real HD Sound URL
                sound_url = REAL_SOUND_LIBRARY.get(sound_name, REAL_SOUND_LIBRARY["Default Ambient Sound"])
                st.audio(sound_url, format="audio/ogg")
            st.markdown('</div>', unsafe_allow_html=True)

    # -----------------------------------------------------
    # MODULE 2: DIGITAL ASSET CATALOG
    # -----------------------------------------------------
    elif app_mode == "📦 Digital Asset Catalog":
        st.markdown("### 📦 Centralized Digital Audio Asset Inventory")
        
        search_query = st.text_input("🔎 Search Catalog by Place, Category or Sound Title:", "")
        
        filtered_df = catalog_df.copy()
        if search_query:
            filtered_df = catalog_df[
                catalog_df["Title"].str.contains(search_query, case=False) |
                catalog_df["Place"].str.contains(search_query, case=False) |
                catalog_df["Category"].str.contains(search_query, case=False)
            ]
            
        st.dataframe(filtered_df, use_container_width=True)
        
        st.markdown("---")
        st.markdown("### 🎧 Instant Catalog Audio Player")
        
        c1, c2 = st.columns(2)
        with c1:
            selected_sound = st.selectbox("Select Asset to Play:", filtered_df["Title"].tolist())
        with c2:
            if selected_sound:
                sound_url = REAL_SOUND_LIBRARY.get(selected_sound, REAL_SOUND_LIBRARY["Default Ambient Sound"])
                st.write(f"Playing Asset: **{selected_sound}**")
                st.audio(sound_url, format="audio/ogg")

    # -----------------------------------------------------
    # MODULE 3: KNOWLEDGE GRAPH VISUALIZER
    # -----------------------------------------------------
    elif app_mode == "🕸️ Knowledge Graph Visualizer":
        st.markdown("### 🕸️ Semantic Knowledge Relationship Graph")
        st.write("Visualizing relationships: Location Node $\rightarrow$ Entity Node $\rightarrow$ Audio Asset Node.")

        G = nx.DiGraph()
        for place, details in places_db.items():
            G.add_node(place, node_type="place", color="#38bdf8")
            for thing in details["things"][:2]:
                G.add_node(thing, node_type="object", color="#34d399")
                G.add_edge(place, thing)
            for sound in details["sounds"][:2]:
                G.add_node(sound, node_type="sound", color="#c084fc")
                G.add_edge(place, sound)

        fig, ax = plt.subplots(figsize=(11, 5), facecolor='#0d1117')
        ax.set_facecolor('#0d1117')
        
        pos = nx.spring_layout(G, k=0.5, seed=42)
        colors = [nx.get_node_attributes(G, 'color').get(node, '#8b949e') for node in G.nodes()]
        
        nx.draw_networkx_nodes(G, pos, node_color=colors, node_size=1600, ax=ax)
        nx.draw_networkx_edges(G, pos, arrowstyle="->", arrowsize=12, edge_color="#30363d", ax=ax)
        nx.draw_networkx_labels(G, pos, font_size=7, font_color="black", font_weight="bold", ax=ax)
        
        plt.axis("off")
        st.pyplot(fig)


if __name__ == "__main__":
    main()

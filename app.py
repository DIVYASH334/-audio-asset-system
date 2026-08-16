import streamlit as st
import pandas as pd
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
import io
import hashlib
from scipy.io import wavfile

# ---------------------------------------------------------
# 1. PAGE CONFIGURATION & FRONT-END CSS STYLING
# ---------------------------------------------------------
st.set_page_config(
    page_title="Audio Asset Management System",
    page_icon="🎧",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .stApp { background: #0d1117; color: #e6edf3; }
    .main-title {
        background: linear-gradient(90deg, #38bdf8 0%, #818cf8 50%, #c084fc 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.8rem; font-weight: 800; margin-bottom: 0px;
    }
    .sub-title { color: #8b949e; font-size: 1.1rem; margin-bottom: 25px; }
    .card-box {
        background-color: #161b22; border: 1px solid #30363d; border-radius: 12px;
        padding: 22px; margin-bottom: 20px; box-shadow: 0 8px 24px rgba(0,0,0,0.2);
    }
    .badge-item {
        background: #1f2937; color: #38bdf8; border: 1px solid #38bdf8;
        padding: 6px 14px; border-radius: 20px; font-size: 0.9rem;
        font-weight: 600; display: inline-block; margin: 4px;
    }
</style>
""", unsafe_allow_html=True)


# ---------------------------------------------------------
# 2. AUDIO GENERATION ENGINE
# Generates a unique, topic-matched sound wave locally.
# No external URLs used -> audio always plays, no broken links.
# ---------------------------------------------------------
def generate_synthetic_audio(sound_type, duration=3.0, sample_rate=22050):
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    s = sound_type.lower()

    if "siren" in s or "ambulance" in s or "police" in s:
        freq = 600 + 350 * np.sin(2 * np.pi * 1.5 * t)
        audio = 0.5 * np.sin(2 * np.pi * freq * t)

    elif "monitor" in s or "beep" in s or "chime" in s:
        audio = np.zeros_like(t)
        beep_len = int(sample_rate * 0.15)
        beep = np.sin(2 * np.pi * 880 * t[:beep_len]) * np.exp(-4 * t[:beep_len])
        interval = int(sample_rate * 0.8)
        for i in range(0, len(t), interval):
            if i + beep_len < len(t):
                audio[i:i + beep_len] = beep

    elif "hospital" in s or "ambience" in s or "lobby" in s:
        noise = np.random.normal(0, 0.15, len(t))
        hum = 0.1 * np.sin(2 * np.pi * 60 * t)
        audio = noise + hum

    elif "wave" in s or "ocean" in s or "sea" in s:
        noise = np.random.normal(0, 0.4, len(t))
        envelope = 0.5 + 0.5 * np.sin(2 * np.pi * 0.3 * t)
        audio = noise * envelope

    elif "seagull" in s or "bird" in s:
        chirp_freq = 1500 + 1000 * np.sin(2 * np.pi * 4 * t)
        audio = 0.3 * np.sin(2 * np.pi * chirp_freq * t) * (np.sin(2 * np.pi * 2 * t) > 0.4)

    elif "wind" in s:
        audio = np.random.normal(0, 0.25, len(t))

    elif "jet" in s or "airplane" in s or "flight" in s or "engine" in s:
        noise = np.random.normal(0, 0.4, len(t))
        sweep = np.sin(2 * np.pi * (100 + 400 * (t / duration)) * t)
        audio = 0.5 * noise + 0.3 * sweep

    elif "train" in s or "whistle" in s or "horn" in s and "car" not in s:
        chord = np.sin(2 * np.pi * 311 * t) + np.sin(2 * np.pi * 370 * t) + np.sin(2 * np.pi * 466 * t)
        env = np.ones_like(t)
        env[:int(0.1 * sample_rate)] = np.linspace(0, 1, int(0.1 * sample_rate))
        env[-int(0.2 * sample_rate):] = np.linspace(1, 0, int(0.2 * sample_rate))
        audio = 0.3 * chord * env

    elif "rumble" in s or "track" in s:
        audio = 0.3 * np.random.normal(0, 0.3, len(t)) + 0.2 * np.sin(2 * np.pi * 40 * t)

    elif "drill" in s or "machinery" in s:
        audio = 0.4 * np.sin(2 * np.pi * 180 * t) + 0.2 * np.random.normal(0, 0.3, len(t))

    elif "clang" in s or "metal" in s or "hammer" in s:
        audio = np.zeros_like(t)
        hit_len = int(sample_rate * 0.5)
        ring_t = t[:hit_len]
        ring = (np.sin(2 * np.pi * 1200 * ring_t) + np.sin(2 * np.pi * 1800 * ring_t)) * np.exp(-7 * ring_t)
        audio[:hit_len] = 0.5 * ring

    elif "steam" in s or "hiss" in s:
        audio = 0.3 * np.random.normal(0, 0.3, len(t))

    elif "cafe" in s or "chatter" in s or "crowd" in s:
        noise = np.random.normal(0, 0.3, len(t))
        mod = 0.5 + 0.5 * np.sin(2 * np.pi * 1.2 * t) * np.cos(2 * np.pi * 0.7 * t)
        audio = noise * mod

    elif "car" in s or "traffic" in s:
        audio = 0.3 * np.sin(2 * np.pi * 250 * t) * (np.sin(2 * np.pi * 1.5 * t) > 0.6)

    elif "cheer" in s or "stadium" in s:
        noise = np.random.normal(0, 0.3, len(t))
        mod = 0.5 + 0.5 * np.sin(2 * np.pi * 0.8 * t)
        audio = noise * mod

    else:
        hash_val = int(hashlib.md5(sound_type.encode()).hexdigest(), 16)
        base_freq = (hash_val % 400) + 250
        mod_freq = (hash_val % 6) + 1
        freq = base_freq + 150 * np.sin(2 * np.pi * mod_freq * t)
        audio = 0.35 * np.sin(2 * np.pi * freq * t)

    audio_max = np.max(np.abs(audio))
    if audio_max > 0:
        audio = audio / audio_max
    audio_int16 = np.int16(audio * 32767)

    byte_io = io.BytesIO()
    wavfile.write(byte_io, sample_rate, audio_int16)
    return byte_io.getvalue()


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
                "Format": "WAV Audio",
                "Sample Rate": "22.05 kHz"
            })
            asset_id += 1

    return places_context, pd.DataFrame(catalog_data)


# ---------------------------------------------------------
# 4. FRONTEND DASHBOARD APP LOGIC
# ---------------------------------------------------------
def main():
    st.markdown('<p class="main-title">🎵 Audio Asset Management & Cataloguing System</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-title">Context-Aware Entity Discovery & Locally-Generated Audio Asset Platform</p>', unsafe_allow_html=True)

    places_db, catalog_df = load_knowledge_base()

    st.sidebar.markdown("## 🧭 Control Panel")
    app_mode = st.sidebar.radio(
        "Navigate Modules:",
        ["🔍 Contextual Asset Search", "📦 Digital Asset Catalog", "🕸️ Knowledge Graph Visualizer"]
    )
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📌 Active System Stats")
    st.sidebar.write(f"• **Indexed Locations:** {len(places_db)}")
    st.sidebar.write("• **Audio Engine:** Locally generated (offline-safe)")

    # MODULE 1: CONTEXTUAL ASSET SEARCH
    if app_mode == "🔍 Contextual Asset Search":
        st.markdown("### 📍 Location Context Discovery Engine")

        c_sel, c_inp = st.columns([2, 1])
        with c_sel:
            selected_place = st.selectbox("Choose Preset Location:", list(places_db.keys()))
        with c_inp:
            custom_place = st.text_input("Or Type Any Location Name:", placeholder="e.g. Airport, Beach, Gym...")

        active_place = custom_place.strip().title() if custom_place else selected_place

        if active_place in places_db:
            category = places_db[active_place]["category"]
            things = places_db[active_place]["things"]
            sounds = places_db[active_place]["sounds"]
        else:
            category = "Custom Query Environment"
            things = [f"{active_place} Main Sector", f"{active_place} Hardware Equipment", f"{active_place} Control Desk"]
            sounds = [f"{active_place} Ambient Sound"]
            st.info(f"✨ Generating dynamic contextual fallback mapping for **'{active_place}'**")

        st.markdown(f"#### 🏷️ Active Location Context: **{active_place}** (`{category}`)")
        st.markdown("---")

        col_left, col_right = st.columns([1, 1])

        with col_left:
            st.markdown('<div class="card-box">', unsafe_allow_html=True)
            st.markdown("### 🧰 Related Physical Entities & Things")
            st.write("Identified items from entity mapping ontology:")
            for item in things:
                st.markdown(f'<span class="badge-item">📦 {item}</span>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        with col_right:
            st.markdown('<div class="card-box">', unsafe_allow_html=True)
            st.markdown("### 🔊 Topic-Matched Sound Effects")
            st.write("Locally generated audio (plays instantly, no internet needed):")

            for sound_name in sounds:
                st.markdown(f"**🔊 {sound_name}**")
                audio_bytes = generate_synthetic_audio(sound_name)
                st.audio(audio_bytes, format="audio/wav")
            st.markdown('</div>', unsafe_allow_html=True)

    # MODULE 2: DIGITAL ASSET CATALOG
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
            options = filtered_df["Title"].tolist()
            selected_sound = st.selectbox("Select Asset to Play:", options) if options else None
        with c2:
            if selected_sound:
                st.write(f"Playing Asset: **{selected_sound}**")
                audio_bytes = generate_synthetic_audio(selected_sound)
                st.audio(audio_bytes, format="audio/wav")
                st.download_button(
                    label="📥 Download WAV Asset",
                    data=audio_bytes,
                    file_name=f"{selected_sound.replace(' ', '_')}.wav",
                    mime="audio/wav"
                )

    # MODULE 3: KNOWLEDGE GRAPH VISUALIZER
    elif app_mode == "🕸️ Knowledge Graph Visualizer":
        st.markdown("### 🕸️ Semantic Knowledge Relationship Graph")
        st.write("Visualizing relationships: Location Node -> Entity Node -> Audio Asset Node.")

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

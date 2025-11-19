import streamlit as st
import pandas as pd
import pickle
import os
import requests
import time
import random
from urllib.parse import quote_plus
from datetime import datetime

# -------------------- PAGE CONFIG --------------------
st.set_page_config(
    page_title='MRS Punjabi v4.0', 
    page_icon='🎵', 
    layout='wide',
    initial_sidebar_state="expanded"
)

# -------------------- SESSION STATE INITIALIZATION --------------------
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user_name' not in st.session_state:
    st.session_state.user_name = ""
if 'voice_text' not in st.session_state:
    st.session_state.voice_text = ""
if 'favorites' not in st.session_state:
    st.session_state.favorites = []
if 'play_history' not in st.session_state:
    st.session_state.play_history = []
if 'user_mood' not in st.session_state:
    st.session_state.user_mood = "Happy"
if 'now_playing' not in st.session_state:
    st.session_state.now_playing = None
if 'login_time' not in st.session_state:
    st.session_state.login_time = None

# Custom CSS with Enhanced Styling
st.markdown("""
<style>
    .main-title {
        font-size: 3rem;
        background: linear-gradient(45deg, #FF6B6B, #4ECDC4, #45B7D1, #FFD93D);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        font-weight: bold;
        margin-bottom: 1rem;
    }
    .song-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 15px;
        margin: 15px 0;
        color: white;
        border-left: 5px solid #4ECDC4;
        transition: transform 0.3s ease;
    }
    .song-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 25px rgba(0,0,0,0.2);
    }
    .feature-card {
        background: rgba(255,255,255,0.1);
        padding: 20px;
        border-radius: 15px;
        margin: 10px 0;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255,255,255,0.2);
    }
    .stats-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 15px;
        border-radius: 10px;
        color: white;
        text-align: center;
    }
    .mood-indicator {
        display: inline-block;
        padding: 5px 15px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: bold;
        margin: 2px;
    }
    .chill { background: #4ECDC4; color: black; }
    .party { background: #FFD93D; color: black; }
    .romantic { background: #FF97B7; color: white; }
    .hiphop { background: #6BFFB8; color: black; }
    .workout { background: #FF6B6B; color: white; }
    .youtube-btn {
        background: #FF0000 !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 8px 16px !important;
        font-weight: bold !important;
    }
</style>
""", unsafe_allow_html=True)

# -------------------- YOUTUBE INTEGRATION FUNCTIONS --------------------

def get_youtube_url(song_name, artist):
    """Generate YouTube search URL for the song"""
    search_query = quote_plus(f"{song_name} {artist} official audio")
    return f"https://www.youtube.com/results?search_query={search_query}"

def play_song_on_youtube(song_name, artist):
    """Open YouTube in a new tab with the song search"""
    youtube_url = get_youtube_url(song_name, artist)
    
    # Show success message with clickable link
    st.success(f"🎵 Opening YouTube for: **{song_name}** by **{artist}**")
    
    # Display clickable YouTube link
    st.markdown(f"""
    <div style="text-align: center; margin: 15px 0;">
        <a href="{youtube_url}" target="_blank" style="text-decoration: none;">
            <button style="
                background: linear-gradient(45deg, #FF0000, #CC0000);
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 16px;
                cursor: pointer;
                margin: 10px;">
                ▶️ Play "{song_name}" on YouTube
            </button>
        </a>
    </div>
    """, unsafe_allow_html=True)
    
    # Add to play history
    if song_name not in st.session_state.play_history:
        st.session_state.play_history.append(song_name)
    
    # Set now playing
    st.session_state.now_playing = song_name

# -------------------- HELPER FUNCTIONS --------------------

def display_song_card(row, show_favorite=True):
    """Display a song card with consistent formatting"""
    if new_df is None or new_df.empty:
        st.error("No data available")
        return
        
    song_col = new_df.columns[0]
    song_name = row[song_col]
    artist = row.get('Album/Movie', row.get('Singer/Artists', 'Unknown'))
    mood = row.get('Mood', 'Unknown')
    rating = row.get('User-Rating', 'N/A')
    genre = row.get('Genre', 'Unknown')
    
    youtube_url = get_youtube_url(song_name, artist)
    poster = fetch_poster(str(song_name), str(artist))
    
    col1, col2 = st.columns([1, 4])
    
    with col1:
        if poster and os.path.exists(poster):
            st.image(poster, use_container_width=True)
        else:
            st.markdown("<div style='text-align: center; font-size: 3rem;'>🎵</div>", unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class='song-card'>
            <h3>{song_name}</h3>
            <p><b>Artist:</b> {artist}</p>
            <p><b>Genre:</b> {genre} | <b>Mood:</b> {mood}</p>
            <p><b>Rating:</b> ⭐ {rating}/10</p>
            <a href='{youtube_url}' target='_blank' style='color: #4ECDC4; text-decoration: none; font-weight: bold;'>
                🎵 Listen on YouTube
            </a>
        </div>
        """, unsafe_allow_html=True)
    
    # Action buttons
    col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
    
    with col1:
        if st.button("▶️ Play", key=f"play_{song_name}"):
            play_song_on_youtube(song_name, artist)
    
    with col2:
        if show_favorite and st.button("❤️ Favorite", key=f"fav_{song_name}"):
            if song_name not in st.session_state.favorites:
                st.session_state.favorites.append(song_name)
                st.success(f"Added {song_name} to favorites!")
    
    with col3:
        if st.button("🔍 Similar", key=f"sim_{song_name}"):
            st.session_state.voice_text = song_name
            st.rerun()
    
    with col4:
        # Direct YouTube button
        st.markdown(f"""
        <a href="{youtube_url}" target="_blank">
            <button style="
                background: #FF0000; 
                color: white; 
                border: none; 
                padding: 8px 12px; 
                border-radius: 5px; 
                font-size: 12px;
                cursor: pointer;">
                YouTube
            </button>
        </a>
        """, unsafe_allow_html=True)

# -------------------- LOGIN --------------------
def login():
    st.markdown("<h1 class='main-title'>🔐 MRS Punjabi v4.0</h1>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.container():
            st.subheader("🎵 AI-Powered Music Discovery")
            username = st.text_input("👤 Username")
            password = st.text_input("🔒 Password", type="password")
            
            if st.button("🚀 Login to Music World", use_container_width=True):
                if username == "gursimran" and password == "12345":
                    st.session_state.logged_in = True
                    st.session_state.user_name = username
                    st.session_state.login_time = datetime.now()
                    st.success("🎉 Login successful! Welcome to your music universe!")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("❌ Invalid credentials!")
            
            st.info("**Demo Credentials:** 👤 Username: `gursimran` | 🔒 Password: `12345`")

# Check login status
if not st.session_state.logged_in:
    login()
    st.stop()

# -------------------- LOAD DATA --------------------
@st.cache_resource
def load_models():
    try:
        if not os.path.exists('models'):
            st.error("❌ Models folder not found. Run preprocess_data.py first.")
            st.stop()
        
        new_df = pickle.load(open('models/musicrec.pkl', 'rb'))
        similarity = pickle.load(open('models/similarities.pkl', 'rb'))
        return new_df, similarity
    except Exception as e:
        st.error(f"Error loading models: {e}")
        st.stop()

new_df, similarity = load_models()

# Create posters directory
os.makedirs('posters', exist_ok=True)

# -------------------- ENHANCED FUNCTIONS --------------------

def simulate_voice_search():
    """Enhanced voice search simulation"""
    punjabi_songs = [
        "Brown Munde", "Excuses", "295", "Lehanga", "Qismat", 
        "So High", "Sakhiyan", "Daang", "Lahore", "Prada",
        "Bambiha Bole", "Old Skool", "Diamond", "Viah", "Jatt da Muqabala"
    ]
    
    with st.spinner("🎤 Listening... Speak the song name clearly"):
        time.sleep(2)
    
    selected_song = random.choice(punjabi_songs)
    return selected_song

def fetch_poster(song, artist):
    """Enhanced poster fetching with caching"""
    filename = f"posters/{song}_{artist}.jpg".replace('/', '_').replace('\\', '_')[:100]
    if os.path.exists(filename):
        return filename
    try:
        query = quote_plus(f"{song} {artist} punjabi song")
        url = f"https://itunes.apple.com/search?term={query}&limit=1&media=music"
        r = requests.get(url, timeout=5)
        data = r.json()
        if data.get('results'):
            artwork = data['results'][0].get('artworkUrl100')
            if artwork:
                artwork = artwork.replace('100x100bb', '400x400bb')
                img_data = requests.get(artwork, timeout=5).content
                with open(filename, 'wb') as f:
                    f.write(img_data)
                return filename
    except Exception:
        return None
    return None

def recommend(song_title, topn=5):
    """Enhanced recommendation with mood-based filtering"""
    try:
        song_col = new_df.columns[0]
        idx = new_df[new_df[song_col] == song_title].index[0]
        distances = similarity[idx]
        
        rating_col = None
        for col in new_df.columns:
            if 'rating' in col.lower():
                rating_col = col
                break
        
        if rating_col:
            ratings = new_df[rating_col].fillna(0).astype(float).values
            hybrid_score = distances * 0.7 + (ratings / ratings.max()) * 0.3
        else:
            hybrid_score = distances
            
        recs = sorted(list(enumerate(hybrid_score)), reverse=True, key=lambda x: x[1])[1:topn + 1]
        results = []
        
        for i, score in recs:
            row = new_df.iloc[i]
            results.append({
                'title': row[song_col],
                'artist': row.get('Album/Movie', row.get('Singer/Artists', 'Unknown')),
                'genre': row.get('Genre', 'Unknown'),
                'rating': row.get('User-Rating', 'N/A'),
                'mood': row.get('Mood', 'Unknown'),
                'similarity': f"{score:.1%}",
                'score': score
            })
        return results
    except Exception as e:
        return []

def get_mood_recommendations(mood, topn=10):
    """Get songs based on specific mood"""
    mood_col = 'Mood'
    if mood_col in new_df.columns:
        mood_songs = new_df[new_df[mood_col].str.contains(mood, case=False, na=False)]
        if not mood_songs.empty:
            rating_col = None
            for col in new_df.columns:
                if 'rating' in col.lower():
                    rating_col = col
                    break
            
            if rating_col:
                mood_songs = mood_songs.nlargest(topn, rating_col)
            else:
                mood_songs = mood_songs.head(topn)
            
            return mood_songs
    return pd.DataFrame()

def generate_playlist_by_mood(mood, duration_minutes=60):
    """Generate a playlist for specific mood and duration"""
    mood_songs = get_mood_recommendations(mood, topn=20)
    if mood_songs.empty:
        return []
    
    playlist = []
    total_duration = 0
    target_duration = duration_minutes * 60  # Convert to seconds
    
    for _, song in mood_songs.iterrows():
        if total_duration >= target_duration:
            break
        
        # Simulate song duration (3-5 minutes)
        song_duration = random.randint(180, 300)
        playlist.append({
            'title': song[new_df.columns[0]],
            'artist': song.get('Album/Movie', 'Unknown'),
            'duration': f"{song_duration//60}:{song_duration%60:02d}",
            'mood': song.get('Mood', 'Unknown'),
            'youtube_url': get_youtube_url(song[new_df.columns[0]], song.get('Album/Movie', 'Unknown'))
        })
        total_duration += song_duration
    
    return playlist

def create_mood_chart_text():
    """Create text-based mood distribution"""
    if 'Mood' in new_df.columns:
        mood_counts = new_df['Mood'].value_counts()
        st.subheader("🎭 Music Mood Distribution")
        for mood, count in mood_counts.items():
            st.write(f"**{mood}**: {count} songs")
        return True
    return False

# -------------------- ENHANCED SIDEBAR --------------------
with st.sidebar:
    # Safe access to user_name with default value
    welcome_name = st.session_state.user_name if st.session_state.user_name else "Guest"
    st.markdown(f"### 👋 Welcome, {welcome_name}!")
    
    # Safe access to login_time
    if st.session_state.login_time:
        st.markdown(f"**Login Time:** {st.session_state.login_time.strftime('%Y-%m-%d %H:%M')}")
    
    st.markdown("---")
    
    # Now Playing Section
    if st.session_state.now_playing:
        st.markdown("### 🎵 Now Playing")
        st.success(f"**{st.session_state.now_playing}**")
        st.markdown("---")
    
    # User Mood Selector
    st.markdown("### 😊 How are you feeling?")
    mood_options = ["Happy", "Energetic", "Chill", "Romantic", "Nostalgic", "Focused"]
    user_mood = st.selectbox("Select your mood:", mood_options, 
                           index=mood_options.index(st.session_state.user_mood) if st.session_state.user_mood in mood_options else 0)
    st.session_state.user_mood = user_mood
    
    # Quick Mood Playlist
    if st.button(f"🎵 Generate {user_mood} Playlist"):
        st.session_state.generate_playlist = True
    
    st.markdown("---")
    
    # User Statistics
    st.markdown("### 📊 Your Stats")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Favorites", len(st.session_state.favorites))
    with col2:
        st.metric("Songs Played", len(st.session_state.play_history))
    
    # Recent Activity
    if st.session_state.play_history:
        st.markdown("#### 🕐 Recently Played")
        for song in st.session_state.play_history[-3:]:
            st.write(f"• {song}")
    
    st.markdown("---")
    
    # Quick Actions
    st.markdown("### ⚡ Quick Actions")
    if st.button("🔍 Discover New Songs"):
        st.session_state.discover_new = True
    if st.button("⭐ Random Favorite"):
        if st.session_state.favorites:
            st.session_state.voice_text = random.choice(st.session_state.favorites)
    
    st.markdown("---")
    st.markdown("**👨‍💻 Developed by Gursimran Singh**")
    st.markdown("**AUP Mohali**")
    
    if st.button("🚪 Logout"):
        # Clear all session state
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

# -------------------- MAIN APP WITH TABS --------------------
st.markdown("<h1 class='main-title'>🎧 MRS Punjabi v4.0 Pro</h1>", unsafe_allow_html=True)

# Create tabs for different features
tab1, tab2, tab3, tab4, tab5 = st.tabs(["🎵 Discover", "🔍 Search", "😊 Mood Magic", "⭐ Favorites", "📊 Analytics"])

with tab1:
    # Home/Dashboard
    st.subheader("🏠 Music Dashboard")
    
    # Statistics Cards
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""
        <div class='stats-card'>
            <h3>🎵</h3>
            <h4>{len(new_df)}</h4>
            <p>Total Songs</p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        unique_artists = new_df['Singer/Artists'].nunique() if 'Singer/Artists' in new_df.columns else 'N/A'
        st.markdown(f"""
        <div class='stats-card'>
            <h3>👤</h3>
            <h4>{unique_artists}</h4>
            <p>Artists</p>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        avg_rating = new_df['User-Rating'].mean() if 'User-Rating' in new_df.columns else 'N/A'
        st.markdown(f"""
        <div class='stats-card'>
            <h3>⭐</h3>
            <h4>{avg_rating if isinstance(avg_rating, str) else f'{avg_rating:.1f}'}</h4>
            <p>Avg Rating</p>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown(f"""
        <div class='stats-card'>
            <h3>😊</h3>
            <h4>{st.session_state.user_mood}</h4>
            <p>Your Mood</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Featured Songs
    st.subheader("🔥 Featured Punjabi Hits")
    featured_songs = new_df.sample(min(6, len(new_df)))
    
    cols = st.columns(3)
    for idx, (_, song) in enumerate(featured_songs.iterrows()):
        with cols[idx % 3]:
            song_name = song[new_df.columns[0]]
            artist = song.get('Album/Movie', 'Unknown')
            mood = song.get('Mood', 'Unknown')
            rating = song.get('User-Rating', 'N/A')
            
            poster = fetch_poster(song_name, artist)
            if poster and os.path.exists(poster):
                st.image(poster, use_container_width=True)
            
            youtube_url = get_youtube_url(song_name, artist)
            
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"**{song_name}**")
                st.write(f"*{artist}*")
            with col2:
                if st.button("❤️", key=f"fav_{idx}"):
                    if song_name not in st.session_state.favorites:
                        st.session_state.favorites.append(song_name)
                        st.success(f"Added {song_name} to favorites!")
            
            mood_class = mood.lower().replace(' ', '')
            st.markdown(f"<span class='mood-indicator {mood_class}'>{mood}</span>", unsafe_allow_html=True)
            st.write(f"⭐ {rating}")
            
            # Play button with YouTube integration
            if st.button("▶️ Play", key=f"play_{idx}"):
                play_song_on_youtube(song_name, artist)
                st.session_state.now_playing = song_name
            
            # Direct YouTube link
            st.markdown(f"""
            <a href="{youtube_url}" target="_blank">
                <button style="
                    background: #FF0000; 
                    color: white; 
                    border: none; 
                    padding: 8px 16px; 
                    border-radius: 5px; 
                    font-size: 12px;
                    cursor: pointer;
                    width: 100%;
                    margin-top: 5px;">
                    🎵 Open YouTube
                </button>
            </a>
            """, unsafe_allow_html=True)

with tab2:
    # Enhanced Search Tab
    st.subheader("🔍 Smart Search & Recommendations")
    
    # Voice Search
    col1, col2 = st.columns([3, 1])
    with col1:
        search_query = st.text_input(
            "Search for songs, artists, or moods:",
            value=st.session_state.voice_text,
            placeholder="Try 'romantic songs' or 'AP Dhillon'..."
        )
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🎤 Voice Search", use_container_width=True):
            recognized_text = simulate_voice_search()
            st.session_state.voice_text = recognized_text
            st.success(f"🎯 Voice recognized: **{recognized_text}**")
            st.rerun()
    
    if search_query:
        # Enhanced search across multiple columns
        song_col = new_df.columns[0]
        results = pd.DataFrame()
        
        # Search in song names
        song_results = new_df[new_df[song_col].astype(str).str.contains(search_query, case=False, na=False)]
        results = pd.concat([results, song_results])
        
        # Search in artists
        if 'Singer/Artists' in new_df.columns:
            artist_results = new_df[new_df['Singer/Artists'].astype(str).str.contains(search_query, case=False, na=False)]
            results = pd.concat([results, artist_results])
        
        # Search in moods
        if 'Mood' in new_df.columns:
            mood_results = new_df[new_df['Mood'].astype(str).str.contains(search_query, case=False, na=False)]
            results = pd.concat([results, mood_results])
        
        results = results.drop_duplicates()
        
        if not results.empty:
            st.subheader(f"🔍 Found {len(results)} results for '{search_query}'")
            for _, row in results.iterrows():
                display_song_card(row)
        else:
            st.warning("No results found. Try different keywords!")
    
    # Recommendations Section
    st.subheader("🎵 Get Personalized Recommendations")
    
    # Get available songs
    song_col = new_df.columns[0]
    options = new_df[song_col].astype(str).tolist()
    
    if options:
        selected_song = st.selectbox("Select a song you like:", options)
        
        if st.button("✨ Get Recommendations"):
            with st.spinner("🔍 Finding similar songs..."):
                recs = recommend(selected_song)
                
                if recs:
                    st.subheader(f"🎵 Songs similar to **{selected_song}**:")
                    for rec in recs:
                        col1, col2 = st.columns([1, 3])
                        
                        poster = fetch_poster(rec['title'], rec['artist'])
                        if poster and os.path.exists(poster):
                            col1.image(poster, use_container_width=True)
                        else:
                            col1.markdown("<div style='text-align: center; font-size: 2rem;'>🎵</div>", unsafe_allow_html=True)
                        
                        youtube_link = f"https://www.youtube.com/results?search_query={quote_plus(rec['title'] + ' ' + rec['artist'])}"
                        col2.markdown(f"""
                        <div class='song-card'>
                            <h3>{rec['title']} <small>({rec['similarity']} match)</small></h3>
                            <p><b>Artist:</b> {rec['artist']}</p>
                            <p><b>Genre:</b> {rec['genre']} | <b>Rating:</b> ⭐ {rec['rating']}</p>
                            <p><b>Mood:</b> {rec['mood']}</p>
                            <a href='{youtube_link}' target='_blank'>▶ Play on YouTube</a>
                        </div>
                        """, unsafe_allow_html=True)
                        st.markdown("---")
                else:
                    st.error("No recommendations found for this song")

with tab3:
    # Mood-based Features
    st.subheader("😊 Mood-Based Music Magic")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🎭 Mood Explorer")
        create_mood_chart_text()
        
        # Mood-based playlist generator
        st.markdown("### 🎵 Generate Playlist")
        mood_choice = st.selectbox("Select mood for playlist:", ["Party", "Chill", "Romantic", "Workout", "Happy", "Sad"])
        duration = st.slider("Playlist duration (minutes):", 10, 120, 30)
        
        if st.button("✨ Generate Smart Playlist"):
            playlist = generate_playlist_by_mood(mood_choice, duration)
            if playlist:
                st.success(f"🎵 Generated {len(playlist)} songs for {mood_choice} mood!")
                total_duration = sum([int(song['duration'].split(':')[0]) for song in playlist])
                st.write(f"**Total Duration:** ~{total_duration} minutes")
                
                for i, song in enumerate(playlist, 1):
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.write(f"**{i}. {song['title']}** - {song['artist']}")
                        st.write(f"⏱️ {song['duration']} | 🎭 {song['mood']}")
                    with col2:
                        if st.button("▶️ Play", key=f"mood_play_{i}"):
                            play_song_on_youtube(song['title'], song['artist'])
                st.markdown("---")
            else:
                st.error("No songs found for this mood!")
    
    with col2:
        st.markdown("### 🎯 Quick Mood Recommendations")
        quick_moods = ["Chill", "Party", "Romantic", "Workout", "Happy"]
        selected_quick_mood = st.selectbox("Quick mood picks:", quick_moods)
        
        if st.button(f"🎵 Get {selected_quick_mood} Songs"):
            mood_songs = get_mood_recommendations(selected_quick_mood, 5)
            if not mood_songs.empty:
                st.success(f"🎵 Top {selected_quick_mood} Songs:")
                for idx, (_, song) in enumerate(mood_songs.iterrows()):
                    song_name = song[new_df.columns[0]]
                    artist = song.get('Album/Movie', 'Unknown')
                    rating = song.get('User-Rating', 'N/A')
                    
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.write(f"**{idx+1}. {song_name}**")
                        st.write(f"👤 {artist} | ⭐ {rating}")
                    with col2:
                        if st.button("▶️ Play", key=f"quick_{idx}"):
                            play_song_on_youtube(song_name, artist)
                    st.markdown("---")
            else:
                st.warning(f"No {selected_quick_mood} songs found!")

with tab4:
    # Favorites Management
    st.subheader("⭐ Your Favorite Songs")
    
    if st.session_state.favorites:
        st.success(f"You have {len(st.session_state.favorites)} favorite songs!")
        
        for fav in st.session_state.favorites:
            # Find the favorite song in dataset
            song_col = new_df.columns[0]
            song_data = new_df[new_df[song_col] == fav]
            
            if not song_data.empty:
                row = song_data.iloc[0]
                display_song_card(row, show_favorite=False)
                
                col1, col2 = st.columns([1, 1])
                with col1:
                    if st.button(f"❌ Remove {fav}", key=f"remove_{fav}"):
                        st.session_state.favorites.remove(fav)
                        st.success(f"Removed {fav} from favorites!")
                        st.rerun()
                with col2:
                    if st.button(f"🔍 Similar to {fav}", key=f"sim_fav_{fav}"):
                        st.session_state.voice_text = fav
                        st.rerun()
            else:
                st.write(f"🎵 {fav} (Not in current dataset)")
                if st.button(f"❌ Remove {fav}", key=f"remove_{fav}"):
                    st.session_state.favorites.remove(fav)
                    st.rerun()
            st.markdown("---")
    else:
        st.info("You haven't added any favorites yet. Click the ❤️ button on songs to add them!")
        
        # Suggest some popular songs to add
        st.subheader("💡 Popular Songs to Start With:")
        popular_songs = new_df.nlargest(3, 'User-Rating') if 'User-Rating' in new_df.columns else new_df.head(3)
        for _, song in popular_songs.iterrows():
            song_name = song[new_df.columns[0]]
            artist = song.get('Album/Movie', 'Unknown')
            st.write(f"🎵 **{song_name}** - {artist}")
            if st.button(f"❤️ Add {song_name}", key=f"add_pop_{song_name}"):
                if song_name not in st.session_state.favorites:
                    st.session_state.favorites.append(song_name)
                    st.success(f"Added {song_name} to favorites!")
                    st.rerun()

with tab5:
    # Analytics Tab
    st.subheader("📊 Music Analytics")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🎵 Music Statistics")
        
        # Basic stats
        if 'Genre' in new_df.columns:
            genre_counts = new_df['Genre'].value_counts().head(8)
            st.subheader("🎼 Top Genres")
            for genre, count in genre_counts.items():
                st.write(f"**{genre}**: {count} songs")
        
        st.markdown("---")
        
        # Rating distribution
        if 'User-Rating' in new_df.columns:
            st.subheader("⭐ Rating Statistics")
            rating_stats = new_df['User-Rating'].describe()
            st.write(f"**Average Rating**: {rating_stats['mean']:.1f}/10")
            st.write(f"**Highest Rating**: {rating_stats['max']}/10")
            st.write(f"**Lowest Rating**: {rating_stats['min']}/10")
            st.write(f"**Total Rated Songs**: {len(new_df)}")
    
    with col2:
        st.markdown("### 👤 Your Music Profile")
        
        # User listening habits
        if st.session_state.play_history:
            st.write("**Your Recent Listening Pattern:**")
            # Simple analysis based on played songs
            recent_moods = []
            for song in st.session_state.play_history[-10:]:
                song_data = new_df[new_df[new_df.columns[0]] == song]
                if not song_data.empty and 'Mood' in song_data.columns:
                    recent_moods.append(song_data.iloc[0]['Mood'])
            
            if recent_moods:
                mood_counts = pd.Series(recent_moods).value_counts()
                st.subheader("🎭 Your Recent Mood Preferences")
                for mood, count in mood_counts.items():
                    st.write(f"**{mood}**: {count} songs")
            else:
                st.info("Play some songs to see your mood preferences!")
        else:
            st.info("No play history yet. Start listening to songs!")
        
        st.markdown("---")
        
        st.markdown("### 🏆 Your Top Genres")
        if st.session_state.favorites:
            favorite_genres = []
            for fav in st.session_state.favorites:
                song_data = new_df[new_df[new_df.columns[0]] == fav]
                if not song_data.empty and 'Genre' in song_data.columns:
                    favorite_genres.append(song_data.iloc[0]['Genre'])
            
            if favorite_genres:
                genre_counts = pd.Series(favorite_genres).value_counts().head(5)
                for genre, count in genre_counts.items():
                    st.write(f"**{genre}**: {count} songs")
            else:
                st.info("Add favorite songs to see your genre preferences!")
        else:
            st.info("No favorites yet. Add some songs to see your preferences!")

# Footer
st.markdown("---")
st.markdown("<center>🎵 **MRS Punjabi v4.0 Pro** | ✨ **AI-Powered Music Discovery** | 👨‍💻 **Developed by Gursimran Singh** | 🏫 **AUP Mohali**</center>", unsafe_allow_html=True)
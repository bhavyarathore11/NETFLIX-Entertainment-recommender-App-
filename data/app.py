import pickle
import streamlit as st
import requests
import pandas as pd

# Load the datasets
movies_data = pd.read_csv('top10K-TMDB-movies.csv')
tv_shows_data = pd.read_csv('tv_shows.csv') 

def fetch_movie_poster(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=29e2f3345677d97e093a706548e7a736&language=en-US"

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        poster_path = data.get('poster_path', '')
        if poster_path:
            full_path = f"https://image.tmdb.org/t/p/w500/{poster_path}"
        else:
            full_path = "https://via.placeholder.com/500x750?text=No+Image"
        homepage = data.get('homepage', '')
    except requests.exceptions.RequestException as e:
        print(f"Error fetching poster for movie ID {movie_id}: {e}")
        full_path = "https://via.placeholder.com/500x750?text=No+Image"
        homepage = ''
    return full_path, homepage

def fetch_tv_show_poster(tv_show_id):
    url = f"https://api.themoviedb.org/3/tv/{tv_show_id}?api_key=29e2f3345677d97e093a706548e7a736&language=en-US"

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        poster_path = data.get('poster_path', '')
        if poster_path:
            full_path = f"https://image.tmdb.org/t/p/w500/{poster_path}"
        else:
            full_path = "https://via.placeholder.com/500x750?text=No+Image"
        homepage = data.get('homepage', '')
    except requests.exceptions.RequestException as e:
        print(f"Error fetching poster for TV show ID {tv_show_id}: {e}")
        full_path = "https://via.placeholder.com/500x750?text=No+Image"
        homepage = ''
    return full_path, homepage

def recommend(content, content_type='movie'):
    if content_type == 'movie':
        index = movies_data[movies_data['title'] == content].index[0]
        distances = sorted(list(enumerate(movies_similarity[index])), reverse=True, key=lambda x: x[1])
        content_df = movies_data
        fetch_poster_func = fetch_movie_poster
    elif content_type == 'tv':
        index = tv_shows_data[tv_shows_data['title'] == content].index[0]
        distances = sorted(list(enumerate(tv_shows_similarity[index])), reverse=True, key=lambda x: x[1])
        content_df = tv_shows_data
        fetch_poster_func = fetch_tv_show_poster
    else:
        return [], [], []

    recommended_names = []
    recommended_posters = []
    recommended_links = []
    for i in distances[:5]:  # Recommend top 5 similar items
        content_id = content_df.iloc[i[0]].id
        poster, link = fetch_poster_func(content_id)
        recommended_posters.append(poster)
        recommended_names.append(content_df.iloc[i[0]].title)
        recommended_links.append(link)

    return recommended_names, recommended_posters, recommended_links

# Load the content and similarity matrices
movies_similarity = pickle.load(open(r'C:\Users\hp\OneDrive\Desktop\movie recomendation\similarity.pkl', 'rb'))
tv_shows_similarity = pickle.load(open(r'C:\Users\hp\OneDrive\Desktop\movie recomendation\tv_shows_similarity.pkl', 'rb'))

# Initialize session state
if 'page' not in st.session_state:
    st.session_state.page = 'welcome'

# Custom CSS with animations
if st.session_state.page == 'welcome':
    background_image = "https://files.tecnoblog.net/wp-content/uploads/2021/12/melhor-streaming-2021-netflix-1.jpg"
else:
    background_image = "https://wallpapers.com/images/hd/netflix-background-gs7hjuwvv2g0e9fj.jpg?size=1200:675"

st.markdown(f"""
    <style>
        @keyframes fadeIn {{
            from {{ opacity: 0; }}
            to {{ opacity: 1; }}
        }}
        @keyframes slideIn {{
            from {{ transform: translateY(-100%); }}
            to {{ transform: translateY(0); }}
        }}
        @keyframes backgroundFadeIn {{
            from {{ opacity: 0; }}
            to {{ opacity: 1; }}
        }}
        .stApp {{
            animation: backgroundFadeIn 2s ease-in-out;
            background: url("{background_image}");
            background-size: cover;
        }}
        .header {{
            animation: slideIn 1s ease-in-out;
            font-size: 3em;
            color: white;
            text-align: center;
            margin-top: 20px;
            font-family: 'Arial', sans-serif;
            font-weight: bold;
        }}
        .header .netflix {{
            color: red;
        }}
        .content-title {{
            animation: fadeIn 1s ease-in-out;
            color: white;
            text-align: center;
        }}
        .stButton>button {{
            display: block;
            margin: 0 auto;
            background-color: #E50914;
            color: white;
            border: none;
            padding: 10px 20px;
            font-size: 1.5em;
            cursor: pointer;
        }}
        .button-img {{
            width: 80px; /* Adjust as needed */
            height: auto; /* Maintain aspect ratio */
            cursor: pointer;
        }}
    </style>
""", unsafe_allow_html=True)


# Welcome page
if st.session_state.page == 'welcome':
    st.markdown('<div class="header">Welcome to <span class="netflix">NETFLIX</span> Entertainment Recommender</div>', unsafe_allow_html=True)
    if st.button('Enjoy Your Day'):
        st.session_state.page = 'main'
        st.experimental_rerun()

# Main app page
if st.session_state.page == 'main':
    st.markdown('<div class="header"><span class="netflix">NETFLIX</span> Entertainment Recommender</div>', unsafe_allow_html=True)

    if st.button('Back to Welcome'):
        st.session_state.page = 'welcome'
        st.experimental_rerun()

    # Dropdown menu for selecting content type
    content_type = st.selectbox(
        "Select content type",
        ['Movies', 'TV Shows']
    )

    # Dropdown menu for selecting content
    if content_type == 'Movies':
        content_list = movies_data['title'].values
        content_df = movies_data
        content_type_key = 'movie'
    else:
        content_list = tv_shows_data['title'].values
        content_df = tv_shows_data
        content_type_key = 'tv'

    selected_content = st.selectbox(
        f"Type or select a {content_type.lower()} from the dropdown",
        content_list
    )

    # Display recommendations when button is clicked
    if st.button('Show Recommendation'):
        try:
            recommended_names, recommended_posters, recommended_links = recommend(selected_content, content_type_key)
            col1, col2, col3, col4, col5 = st.columns(5)
            for i in range(len(recommended_names)):
                with globals()[f"col{i + 1}"]:
                    st.markdown(f'<div class="content-title">{recommended_names[i]}</div>', unsafe_allow_html=True)
                    st.markdown(f'<a href="{recommended_links[i]}" target="_blank"><img src="{recommended_posters[i]}" class="button-img"></a>', unsafe_allow_html=True)
        except Exception as e:
            st.error(f"An error occurred while fetching recommendations: {e}")

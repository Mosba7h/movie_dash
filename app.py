# Import necessary libraries
from flask import Flask
import dash
from dash import html, dcc, Output, Input, State
from bs4 import BeautifulSoup
import requests
import pandas as pd
import scipy.sparse as ssp
from sklearn.preprocessing import LabelEncoder

# Load your movies dataset and encoder
movies_df = pd.read_csv('movies.csv')  # Adjust the path as needed
links_df = pd.read_csv('links.csv')  # Load the links.csv file

movie_encoder = LabelEncoder()
movies_df['movieId_encoded'] = movie_encoder.fit_transform(movies_df['movieId'])

# Load the sparse similarity matrix
loaded_sparse_matrix = ssp.load_npz('sparse_similarity_matrix.npz')
similarity = pd.DataFrame.sparse.from_spmatrix(loaded_sparse_matrix)

def recommend_movies(movie_name, N=5)
    try
        movie_id = movies_df[movies_df['title'] == movie_name]['movieId'].values[0]
        movie_id_encoded = movie_encoder.transform([movie_id])[0]
        similarity_scores = similarity[movie_id_encoded]
        similar_movie_ids = similarity_scores.sort_values(ascending=False).index[1N+1]
        similar_movie_ids_original = movie_encoder.inverse_transform(similar_movie_ids)
        return similar_movie_ids_original.tolist()
    except IndexError
        return fMovie '{movie_name}' not found in the dataset.
    except Exception as e
        return str(e)

# Function to scrape movie details using tmdbId
def scrape_movie_details(tmdb_id)
    url = f'httpswww.themoviedb.orgmovie{tmdb_id}'
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    title_element = soup.find('h2', class_='title')
    title = title_element.text.strip() if title_element else NA
    release_date_element = soup.find('span', class_='release_date')
    release_date = release_date_element.text.strip() if release_date_element else NA
    overview_element = soup.find('div', class_='overview')
    overview = overview_element.text.strip() if overview_element else NA
    poster_element = soup.find('img', class_='poster')
    poster_path = poster_element['src'] if poster_element and 'src' in poster_element.attrs else NA
    return {'title' title, 'release_date' release_date, 'overview' overview, 'poster_path' poster_path}

# Initialize the Flask server
server = Flask(__name__)
# Initialize the Dash app
app = dash.Dash(__name__, server=server, suppress_callback_exceptions=True)

# Define the layout for the home page
home_layout = html.Div(
    style={'backgroundImage' 'url(assetshome_background.jpeg)', 'backgroundSize' 'cover', 'height' '100vh',
           'display' 'flex', 'flexDirection' 'column', 'justifyContent' 'center', 'alignItems' 'center'},
    children=[
        html.H1(Welcome to BEST_MOVIE app, style={'color' 'white', 'textAlign' 'center'}),
        html.Div([
            dcc.Link(html.Button(User Page), href='user'),
            dcc.Link(html.Button(Movie Page), href='movie')
        ], style={'marginTop' '20px'}),
    ]
)

# Define the layout for the user page
user_layout = html.Div(
    style={'backgroundImage' 'url(assetsuser_background.jpeg)', 'backgroundSize' 'cover', 'height' '100vh',
           'display' 'flex', 'flexDirection' 'column', 'justifyContent' 'center', 'alignItems' 'center'},
    children=[
        dcc.Input(id='user-id-input', type='text', placeholder='Enter your ID'),
        html.Button('Enter', id='user-id-button'),
        dcc.Link(html.Button('Back'), href='')
    ]
)

# Define the layout for the movie page
movie_layout = html.Div(
    style={'backgroundImage' 'url(assetsuser_background.jpeg)', 'backgroundSize' 'cover', 'height' '100vh',
           'display' 'flex', 'flexDirection' 'column', 'justifyContent' 'center', 'alignItems' 'center'},
    children=[
        dcc.Dropdown(id='movie-dropdown', options=[{'label' movie, 'value' movie} for movie in movies_df['title']],
                     placeholder='Select a movie', style={'width' '50%'}),
        html.Button('Get Recommendations', id='movie-name-button'),
        html.Div(id='recommendations-output', style={'marginTop' '20px', 'width' '80%'}),
        dcc.Link(html.Button('Back'), href='')
    ]
)

# Define the callback to handle movie recommendations
@app.callback(
    Output('recommendations-output', 'children'),
    [Input('movie-name-button', 'n_clicks')],
    [State('movie-dropdown', 'value')]
)
def display_recommendations(n_clicks, movie_name)
    if n_clicks is None or not movie_name
        return 
    
    recommended_movie_ids = recommend_movies(movie_name)
    if isinstance(recommended_movie_ids, str)
        return recommended_movie_ids  # Return the error message

    # Get the corresponding tmdbIds for the recommended movieIds
    tmdb_ids = links_df[links_df['movieId'].isin(recommended_movie_ids)]['tmdbId'].tolist()
    recommended_movie_details = [scrape_movie_details(tmdb_id) for tmdb_id in tmdb_ids]

    return html.Div([
        html.Div([
            html.Img(src=movie['poster_path'], style={'width' '150px', 'height' '225px', 'float' 'left', 'marginRight' '20px'}),
            html.Div([
                html.H2(movie['title'], style={'margin' '0'}),
                html.P(fRelease Date {movie['release_date']}, style={'margin' '5px 0'}),
                html.P(movie['overview'], style={'textAlign' 'justify'})
            ], style={'overflow' 'hidden'})
        ], style={'display' 'flex', 'marginBottom' '20px', 'padding' '10px', 'border' '1px solid #ddd', 'borderRadius' '5px', 'backgroundColor' '#f9f9f9'})
        for movie in recommended_movie_details
    ], style={'marginTop' '40px'})  # Added marginTop to create space

# Define the callback to handle page navigation
@app.callback(
    Output('page-content', 'children'),
    [Input('url', 'pathname')]
)
def display_page(pathname)
    if pathname == 'user'
        return user_layout
    elif pathname == 'movie'
        return movie_layout
    else
        return home_layout

# Define the layout with a URL router
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])

# Run the Dash app
if __name__ == '__main__'
    app.run_server(debug=True)

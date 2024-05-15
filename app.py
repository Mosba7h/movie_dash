# Import necessary libraries
from flask import Flask
import dash
from dash import html, dcc, callback_context, Output, Input, State, MATCH, ALL
from bs4 import BeautifulSoup
import requests

# Initialize the Flask server
server = Flask(__name__)

# Initialize the Dash app
app = dash.Dash(__name__, server=server, suppress_callback_exceptions=True)

# Function to scrape movie details
def scrape_movie_details(movie_id):
    url = f'https://www.themoviedb.org/movie/{movie_id}'
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    title_element = soup.find('h2', class_='title')
    title = title_element.text.strip() if title_element else "N/A"

    release_date_element = soup.find('span', class_='release_date')
    release_date = release_date_element.text.strip() if release_date_element else "N/A"

    overview_element = soup.find('div', class_='overview')
    overview = overview_element.text.strip() if overview_element else "N/A"

    poster_element = soup.find('img', class_='poster')
    poster_path = poster_element['src'] if poster_element and 'src' in poster_element.attrs else "N/A"

    return {'title': title, 'release_date': release_date, 'overview': overview, 'poster_path': poster_path}

# Example movie IDs
movie_ids = [550, 155, 13, 500, 272]

# Fetch movie details for all movie IDs
movie_data = [scrape_movie_details(movie_id) for movie_id in movie_ids]

# Define the layout for the home page
home_layout = html.Div(
    style={
        'backgroundImage': 'url("/assets/home_background.jpg")', # Path to home background image
        'backgroundSize': 'cover',
        'height': '100vh',
        'display': 'flex',
        'flexDirection': 'column',
        'justifyContent': 'center',
        'alignItems': 'center'
    },
    children=[
        html.H1("Welcome to BEST_MOVIE app", style={'color': 'white', 'textAlign': 'center'}),
        html.Div([
            dcc.Link(html.Button("User Page"), href='/user'),
            dcc.Link(html.Button("Movie Page"), href='/movie')
        ], style={'marginTop': '20px'}),
        html.Div(
            style={
                'display': 'flex',
                'overflowX': 'scroll',
                'marginTop': '50px',
                'width': '80%'
            },
            children=[
                html.Img(src=movie['poster_path'], style={'width': '200px', 'height': '300px', 'marginRight': '10px'})
                for movie in movie_data
            ]
        )
    ]
)

# Define the layout for the user page
user_layout = html.Div(
    style={
        'backgroundImage': 'url("/assets/user_background.jpg")', # Path to user background image
        'backgroundSize': 'cover',
        'height': '100vh',
        'display': 'flex',
        'flexDirection': 'column',
        'justifyContent': 'center',
        'alignItems': 'center'
    },
    children=[
        dcc.Input(id='user-id-input', type='text', placeholder='Enter your ID'),
        html.Button('Enter', id='user-id-button'),
        dcc.Link(html.Button('Back'), href='/')
    ]
)

# Define the layout for the movie page
movie_layout = html.Div(
    style={
        'backgroundImage': 'url("/assets/user_background.jpg")', # Path to movie background image (using the same as user page for now)
        'backgroundSize': 'cover',
        'height': '100vh',
        'display': 'flex',
        'flexDirection': 'column',
        'justifyContent': 'center',
        'alignItems': 'center'
    },
    children=[
        dcc.Input(id='movie-id-input', type='text', placeholder='Enter movie ID'),
        html.Button('Enter', id='movie-id-button'),
        dcc.Link(html.Button('Back'), href='/')
    ]
)

# Define the callback to handle page navigation
@app.callback(
    Output('page-content', 'children'),
    [Input('url', 'pathname')]
)
def display_page(pathname):
    if pathname == '/user':
        return user_layout
    elif pathname == '/movie':
        return movie_layout
    else:
        return home_layout

# Define the layout with a URL router
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])

# Run the Dash app on a different port
if __name__ == '__main__':
    app.run_server(debug=True)  # Change the port 


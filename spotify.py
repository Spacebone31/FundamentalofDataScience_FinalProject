import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import pandas as pd
import time

# Set up Spotify API credentials
client_id = '4f77263b936540a885653c4078c0dfa5'
client_secret = '6b6ad798c91d443c8d082b76de9dbe9e'
redirect_uri = 'spots.org'

# Authenticate with Spotify
client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

# Function to get audio features for all tracks in a playlist
def get_playlist_tracks(username, playlist_id):
    results = sp.user_playlist_tracks(username, playlist_id)
    tracks = results['items']

    # Continue fetching all tracks in case of a large playlist
    while results['next']:
        results = sp.next(results)
        tracks.extend(results['items'])

    return tracks

# Replace with your Spotify username and playlist ID
username = 'Ari Jaya Teguh'
playlist_id = '6UeSakyzhiEt4NB3UAd6NQ'

# Get all the song IDs from the playlist
tracks = get_playlist_tracks(username, playlist_id)
song_data = []
song_ids = []

for track in tracks:
    track_info = track['track']
    song_ids.append(track_info['id'])
    
    # Collect metadata: title, author, year, genre, and popularity
    title = track_info['name']
    author = track_info['artists'][0]['name']  # Assuming the first artist is the main one
    year = track_info['album']['release_date'][:4]  # Taking only the year part
    genre = sp.artist(track_info['artists'][0]['id']).get('genres', ['Unknown'])[0] if sp.artist(track_info['artists'][0]['id']).get('genres') else 'Unknown'
    popularity = track_info['popularity']  # Popularity score between 0 and 100
    
    song_data.append([title, author, year, genre, popularity])

# Retrieve audio features for each song
features_list = []
for i in range(0, len(song_ids), 50):  # Spotify limits 50 tracks per request
    batch_ids = song_ids[i:i + 50]
    audio_features = sp.audio_features(batch_ids)

    # Save the relevant audio features
    for idx, features in enumerate(audio_features):
        if features:  # Check if features are available
            track_info = song_data[i + idx]
            features_list.append([
                track_info[0], track_info[1], track_info[2], track_info[3], track_info[4],  # title, author, year, genre, popularity
                features['energy'], features['liveness'], features['tempo'], features['speechiness'],
                features['acousticness'], features['instrumentalness'], features['time_signature'],
                features['danceability'], features['key'], features['duration_ms'], features['loudness'],
                features['valence'], features['mode']
            ])

    time.sleep(1)  # Avoid hitting API rate limits

# Create a DataFrame with the features
df = pd.DataFrame(features_list, columns=['title', 'author', 'year', 'genre', 'popularity', 'energy', 'liveness', 'tempo',
                                          'speechiness', 'acousticness', 'instrumentalness', 'time_signature',
                                          'danceability', 'key', 'duration_ms', 'loudness', 'valence', 'mode'])

# Sort DataFrame by popularity and calculate rank
df = df.sort_values(by='popularity', ascending=False).reset_index(drop=True)
df['rank'] = df.index + 1  # Rank is index + 1 in sorted order

# Calculate Rank Score
max_rank = len(df)
df['rank_score'] = max_rank - df['rank'] + 1

# Save the DataFrame to a CSV file
df.to_csv('spotify_audio_features_with_metadata_and_rank_score.csv', index=False)

print("CSV file with metadata and rank score created successfully!")

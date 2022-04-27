# -*- coding: utf-8 -*-
"""
Created on Sat Apr 23 16:24:19 2022

@authors: Garrett Ramos, Max Leussler, Kevin Lee, and Dani Plaha
"""

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import streamlit as st
import pandas as pd

### Required credentials to access Spotify API 
cid = 'fd0fa7e9a82f4d36bc63245fc5f5defa'
secret = 'e8cdff10b25c452381194ca5bad8a85b'
client_credentials_manager = SpotifyClientCredentials(client_id=cid, client_secret=secret)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

st.title("Spotify - Streamlit Application")

### Sidebar setup
search_options = ['Artist', 'Album', 'Track']
search_choice = st.sidebar.selectbox("Search Choice", search_options)

### Search input + button
search_input = st.text_input(search_choice + " Search")
search_button = st.button("Search")

### Initializing empty list for search results to eventually append to
search_results = []

### Initializing these variables for eventual logic tests below
selected_album = None
selected_artist = None
selected_track = None


##### Sidebar Initial Program Flow
if len(str(search_input)) > 0:
    if search_choice == 'Album':
        ### Spotipy module function to initiate query search
        albums = sp.search(q='album:'+ search_input,type='album', limit=20)
        ### The above search returns a dict that we need to dive into
        albums_list = albums['albums']['items']
        if len(albums_list) > 0:
            ### For each album in the dict we want the name of the album as well as the artist
            ### We then want this information all in the same list to then portray as search results
            for album in albums_list:
                search_results.append(album['name'] + " - " + album['artists'][0]['name'])
        selected_album = st.selectbox("Select album: ", search_results)
        ### If the user selects an artist search, the process above will be initiated but based
        ### on the artist searched for
    elif search_choice == 'Artist':
        artists = sp.search(q='artist:'+ search_input,type='artist', limit=20)
        artists_list = artists['artists']['items']
        if len(artists_list) > 0:
            for artist in artists_list:
               search_results.append(artist['name'])
        selected_artist = st.selectbox("Select artist: ", search_results)
    ### If the user selects an track search, the process above will be initiated but based
    ### on the track searched for
    elif search_choice == 'Track':
        tracks = sp.search(q='track:'+ search_input,type='track', limit=20)
        tracks_list = tracks['tracks']['items']
        if len(tracks_list) > 0:
            for track in tracks_list:
                search_results.append(track['name'] + " - " + track['artists'][0]['name'])
        selected_track = st.selectbox("Select track: ", search_results)
 

##### Track Selection (From Sidebar)
if selected_track is not None:
    ### Initializing a couple variables for later in the program flow
    track_id = None
    track_preview = None
    tracks_list = tracks['tracks']['items']
    if len(tracks_list) > 0:
        ### We want to find the song that the user selected
        ### Above the user's selected_track was equal only to the name of the song and the artist
        ### But we also want to get additional data for the track
        for track in tracks_list:
            ### This for loop is used to test whether or not a track is the
            ### same as the track selected by the user
            test_selection = track['name'] + " - " + track['artists'][0]['name']
            if test_selection == selected_track:
                ### Once we confirm that the track selected by the user is the same as
                ### the track we just looped through to obtain
                ### We then want to grab the track id and preview url
                track_id = track['id']
                track_preview = track['preview_url']
    if track_id is not None:
        ### The user now has the option to look at recommended songs based on their selection
        ### Or they can observe the audio features collected and defined by Spotify
        track_options = st.selectbox("Options", ['Audio Features', 'Similar Songs'])
        if track_options == 'Audio Features':
            ### Audio Features are presented in a tabular form
            ### And a 30 second preview (if available) is made available for the user to listen to
            track_features = sp.audio_features(track_id)
            df = pd.DataFrame(track_features, index=[f"{track['name']}"])
            df_features = df.loc[: ,['acousticness', 'danceability', 'energy', 'instrumentalness', 'liveness', 'speechiness', 'valence']]
            st.dataframe(df_features)
            st.audio(track_preview, format="audio/mp3")
            ### Visualization plotted
            ax = df_features.plot.bar(rot=0)
            st.pyplot(fig=ax.figure)
        elif track_options == 'Similar Songs':
            ### User receieves recommeneded songs based on their initial selection
            rec_songs = sp.recommendations(seed_tracks=[track_id])
            for track in rec_songs['tracks'][:5]:
                st.write(f"{track['name']} - {track['artists'][0]['name']}")
                st.audio(track['preview_url'], format="audio/mp3")

##### Artist Selection (From Sidebar)
##### Above process is repeated for if a user selects an artist
if selected_artist is not None:
    artist_id = None
    artist_uri = None
    artists_list = artists['artists']['items']
    if len(artists_list) > 0:
       for artist in artists_list:
           test_selection = artist['name']
           if test_selection == selected_artist:
                artist_id = artist['id']
                artist_uri = artist['uri']
    if artist_id is not None:            
        artist_uri = 'spotify:artist:' + artist_id
        artist_albums = sp.artist_albums(artist_uri)
        top_albums = []
        for album in artist_albums['items']:
            top_albums.append(album['name'])
        top_album_selection = st.selectbox("Select album: ", top_albums)
    
    if top_album_selection is not None:
        for album in artist_albums['items']:
            if album['name'] == top_album_selection:
                album_id = album['id']
    
    if album_id is not None:
        tracks_album = []
        album_tracks = sp.album_tracks(album_id)
        for track in album_tracks['items']:
            tracks_album.append(track['name'])
        track_from_album = st.selectbox("Select track: ", tracks_album)
        
    if track_from_album is not None:
        for track in album_tracks['items']:
            if track['name'] == track_from_album:
                track_id = track['id']
                track_preview = track['preview_url']
        if track_id is not None:
            track_options = st.selectbox("Options", ['Audio Features', 'Similar Songs'])
            if track_options == 'Audio Features':
                track_features = sp.audio_features(track_id)
                df = pd.DataFrame(track_features, index=[f"{track['name']}"])
                df_features = df.loc[: ,['acousticness', 'danceability', 'energy', 'instrumentalness', 'liveness', 'speechiness', 'valence']]
                st.dataframe(df_features)
                st.audio(track_preview, format="audio/mp3")
                #### Visualization plotted
                ax = df_features.plot.bar(rot=0)
                st.pyplot(fig=ax.figure)
            elif track_options == 'Similar Songs':
                rec_songs = sp.recommendations(seed_tracks=[track_id])
                for track in rec_songs['tracks'][:5]:
                    st.write(f"{track['name']} - {track['artists'][0]['name']}")
                    st.audio(track['preview_url'], format="audio/mp3")
        

##### Album Selection (From Sidebar)
##### Above process is repeated for if a user selects an album
if selected_album is not None:
    album_id = None
    album_list = albums['albums']['items']
    if len(album_list) > 0:
        for album in album_list:
            test_selection = album['name'] + " - " + album['artists'][0]['name']
            if test_selection == selected_album:
                album_id = album['id']
    if album_id is not None:
        tracks_album = []
        album_tracks = sp.album_tracks(album_id)
        for track in album_tracks['items']:
            tracks_album.append(track['name'])
        track_from_album = st.selectbox("Select track: ", tracks_album)
    
    if track_from_album is not None:
        for track in album_tracks['items']:
            if track['name'] == track_from_album:
                track_id = track['id']
                track_preview = track['preview_url']
        if track_id is not None:
            track_options = st.selectbox("Options", ['Audio Features', 'Similar Songs'])
            if track_options == 'Audio Features':
                track_features = sp.audio_features(track_id)
                df = pd.DataFrame(track_features, index=[f"{track['name']}"])
                df_features = df.loc[: ,['acousticness', 'danceability', 'energy', 'instrumentalness', 'liveness', 'speechiness', 'valence']]
                st.dataframe(df_features)
                st.audio(track_preview, format="audio/mp3")
                ### Visualization plotted
                ax = df_features.plot.bar(rot=0)
                st.pyplot(fig=ax.figure)
            elif track_options == 'Similar Songs':
                rec_songs = sp.recommendations(seed_tracks=[track_id])
                for track in rec_songs['tracks'][:5]:
                    st.write(f"{track['name']} - {track['artists'][0]['name']}")
                    st.audio(track['preview_url'], format="audio/mp3")
        



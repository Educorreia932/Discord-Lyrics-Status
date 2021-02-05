import json
from os import getenv
from random import choice
import requests
import spotipy

from emoji import categories, category
from lyrics_extractor import SongLyrics, LyricScraperException
from spotipy.oauth2 import SpotifyOAuth


def get_tracks():
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
        client_id=getenv("SPOTIFY_CLIENT_ID"),
        client_secret=getenv("SPOTIFY_CLIENT_SECRET"),
        redirect_uri="http://127.0.0.1:8000/spotify/redirect",
        scope="user-library-read")
    )

    albums = sp.current_user_saved_albums()["items"]
    tracks = []

    for album in albums:
        album_tracks = album["album"]["tracks"]["items"]

        for track in album_tracks:
            track_name = track["name"]
            track_artist = track["artists"][0]["name"]

            tracks.append(f"{track_name} - {track_artist}")

    return tracks


def get_lyrics(track):
    extract_lyrics = SongLyrics(
        getenv("GCS_API_KEY"), getenv("GCS_ENGINE_ID"))

    try:
        data = extract_lyrics.get_lyrics(track)

    except LyricScraperException:
        return None

    return data["lyrics"]


def change_status(status_text, status_emoji):
    DISCORD_ENDPOINT = "https://discord.com/api/v8/users/@me/settings"

    payload = {
        "custom_status": {
            "text": status_text,
            "emoji_name": status_emoji
        }
    }

    payload = json.dumps(payload)

    headers = {
        "Content-Type": "application/json",
        "authorization": getenv("DISCORD_AUTH")
    }

    request = requests.patch(
        DISCORD_ENDPOINT,
        data=payload.encode('utf-8'),
        headers=headers
    )


def random_emoji():
    return choice(category(choice(categories)))


track = choice(get_tracks())

print(track)

lyrics = None

while lyrics is None:
    lyrics = get_lyrics(track)

lyrics = [x for x in lyrics.split("\n") if x != "" and x[0] != "["]

status_text = choice(lyrics)
status_emoji = random_emoji()

change_status(status_text, status_emoji)

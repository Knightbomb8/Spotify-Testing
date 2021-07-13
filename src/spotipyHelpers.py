import math
from spotipy.oauth2 import SpotifyOAuth
import json
import spotipy

features = ["danceability", "energy", "speechiness", "acousticness", "instrumentalness", "liveness",
                "valence"]

# the different spotify scopes needed
playback = spotipy.Spotify(auth_manager=SpotifyOAuth(scope="user-modify-playback-state"))
public_playlist = spotipy.Spotify(auth_manager=SpotifyOAuth(scope="playlist-modify-public"))
lib_reader = spotipy.Spotify(auth_manager=SpotifyOAuth(scope="user-library-read"))

class SpotipyHelpers:
    # container for the playlists (id : name)
    playlists = {}

    def __init__(self):
        """
        A container for the different needed spotify scopes
        """
        return

    # loads in all playlists and returns a list of names
    def load_playlists(self, playlist_count):
        # ensure the count is within a proper range
        playlist_count = max(0, min(playlist_count, 50))
        self.playlists.clear()
        results = lib_reader.current_user_playlists(playlist_count)
        names = []
        # go through every playlist and add to the dict and then return all the names
        for idx, item in enumerate(results['items']):
            name = item['name']
            playlist_id = item['id']
            self.playlists[name] = playlist_id
            names.append(name + " (" + str(item['tracks']['total']) + ")")
        return names

    # loads in all the songs for a specific playlist
    def load_songs_from_playlist(self, playlist_name):
        current_playlist_songs = []
        results = lib_reader.playlist_items(self.playlists.get(playlist_name))

        # iterate through all the songs and add to the current songs
        song_ids = []
        for idx, item in enumerate(results['items']):
            new_song = Song(item)
            current_playlist_songs.append(new_song)
            song_ids.append(new_song.id)
        while results['next']:
            results = lib_reader.next(results)
            for idx, item in enumerate(results['items']):
                new_song = Song(item)
                current_playlist_songs.append(new_song)
                song_ids.append(new_song.id)

        # get audio features for each song
        song_pages = math.ceil(len(song_ids) / 100)
        for i in range(song_pages):
            results = lib_reader.audio_features(song_ids[i * 100: min(len(song_ids), (i + 1) * 100)])
            for idx, item in enumerate(results):
                current_playlist_songs[(i * 100) + idx].get_audio_features(item)

        return current_playlist_songs

    def get_song_features(self):
        return features


# holds information regarding a song
class Song:
    def __init__(self, song_json):
        self.parse_song_info(song_json)
        self.feature_vals = {}

    # parses out the json for the wanted features
    def parse_song_info(self, song_json):
        track = song_json['track']
        self.name = track['name']
        self.id = track['id']
        self.length = track['duration_ms']

    # retrieves the songs audio features
    # TODO: incorporate values that are past the 0 - 1 range
    def get_audio_features(self, audio_json):
        for feature in features:
            self.feature_vals[feature] = audio_json[feature]

# object containing a fitlered playlist
class FilteredPlaylist:
    def __init__(self, unfiltered_playlist, feature_values):
        self.unfiltered_playlist = unfiltered_playlist.copy()
        self.songs_within_filter_range = unfiltered_playlist
        self.songs_outside_filter_range = []
        self.feature_values = {}
        # change features to an array as the default is an immutable tuple
        # TODO: Dont think this is necessary to copy this to new dict
        for feature in feature_values:
            slider = feature_values.get(feature)
            # check if the feature is enabled and if not  set the max range
            if slider.is_enabled:
                vals = slider.slider_values
                new_vals = [vals[0] / 100, vals[1]/100]
            else:
                new_vals = [0, 1]
            self.feature_values[feature] = new_vals

        # iterate over every feature and add the songs outside the filter to the outside array
        for feature in self.feature_values:
            # no need to filter if the slider is not enabled
            slider = feature_values.get(feature)
            if not slider.is_enabled:
                print("here")
                return
            min = self.feature_values.get(feature)[0]
            max = self.feature_values.get(feature)[1]
            for i, song in reversed(list(enumerate(self.songs_within_filter_range))):
                if song.feature_vals[feature] > max or song.feature_vals[feature] < min:
                    self.songs_within_filter_range.pop(i)
                    self.songs_outside_filter_range.append(song)

        # print("Songs in range: ")
        # for song in self.songs_within_filter_range:
        #     print(song.name)
        # print("\n\nSongs outside range: ")
        # for song in self.songs_outside_filter_range:
        #     print(song.name)

    # filters the playlist by features
    def update_feature(self, feature_name, min, max):
        # set the range from 0 -> 100 to 0 -> 1
        min = min/100
        max = max/100
        # retrieve old values and update the feature vals stored
        old_min = self.feature_values.get(feature_name)[0]
        old_max = self.feature_values.get(feature_name)[1]
        self.feature_values[feature_name] = [min, max]

        # check if the filter range grew wider
        extended_range = True if old_min > min or old_max < max else False

        song_moved = False

        # if we extended the range go through songs in the outside range
        if(extended_range):
            for i, song in reversed(list(enumerate(self.songs_outside_filter_range))):
                if max > song.feature_vals[feature_name] > min:
                    song_moved = True
                    self.songs_outside_filter_range.pop(i)
                    self.songs_within_filter_range.append(song)

        # otherwise check if any in range are no longer in range
        else:
            for i, song in reversed(list(enumerate(self.songs_within_filter_range))):
                if song.feature_vals[feature_name] > max or song.feature_vals[feature_name] < min:
                    song_moved = True
                    self.songs_within_filter_range.pop(i)
                    self.songs_outside_filter_range.append(song)

        return song_moved

    # get total playlist length
    def get_playlist_length(self):
        return len(self.unfiltered_playlist)

    # gets length of songs inside the current filters
    def get_songs_inside_filters_length(self):
        return len(self.songs_within_filter_range)

    # gets length of songs outside the current filters
    def get_songs_outside_filters_length(self):
        return len(self.songs_outside_filter_range)

    # gets all songs within filter range
    def get_filtered_songs(self):
        return self.songs_within_filter_range


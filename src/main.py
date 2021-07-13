from __future__ import print_function    # (at top of module)
from spotipyHelpers import SpotipyHelpers, FilteredPlaylist, Song
import sys
from PyQt5.QtCore import Qt
from superqt import *
from featureSlider import FeatureSlider
from PyQt5.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QCheckBox,
    QFormLayout,
    QLineEdit,
    QVBoxLayout,
    QWidget,
    QPushButton,
    QLabel,
    QMessageBox,
    QComboBox,
    QScrollArea
)

ORIENTATION = Qt.Horizontal

def main():
    screen = HomeScreen()

    # scopes = SpotifyScopes
    #
    # results = scopes.lib_reader.current_user_saved_tracks(5)
    # for idx, item in enumerate(results['items']):
    #     print(item)
    #     track = item['track']
    #     print(idx, track['artists'][0]['name'], " – ", track['name'])
    #
    # client_credentials_manager = SpotifyClientCredentials()
    # sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
    # sp.trace = True
    #
    # if len(sys.argv) > 1:
    #     tids = sys.argv[1]
    #     print(tids)
    #
    #     start = time.time()
    #     features = sp.audio_features(tids)
    #     delta = time.time() - start
    #     json_string = json.dumps(features, indent=4)
    #     json_file = open("data.json", "w")
    #     json_file.write(json_string)
    #     print("features retrieved in %.2f seconds" % (delta,))
    #
    # print(scopes.lib_reader.recommendation_genre_seeds())


class HomeScreen:
    def __init__(self):
        app = QApplication(sys.argv)
        self.window = Window()
        self.window.show()
        sys.exit(app.exec_())


class Window(QWidget):
    # reloads the playlist selector
    def reload_playlists_dropdown(self):
        self.combobox.clear()
        # get all the names then add to the dropdown
        playlist_names = self.spotipy_helpers.load_playlists(50)
        self.combobox.addItem("")
        for i in range(len(playlist_names)):
            self.combobox.addItem(playlist_names[i])

    # loads the songs in from spotify
    def load_playlist(self, text):
        # if we are loading in the default state do nothing
        # TODO: if default state loaded in clear all info?
        if text == "":
            return

        # load in the playlist from the helpers
        text = text[:text.rfind('(') - 1]
        songs = self.spotipy_helpers.load_songs_from_playlist(text)

        self.filtered_playlist = FilteredPlaylist(songs, self.feature_sliders)
        self.playlist_loaded = True
        self.update_filtered_songs_values()

        # add all songs to scrollable area in a vertical box layout
        widget = QWidget()
        self.song_scroll_area.setWidget(widget)
        vertical_box = QVBoxLayout()
        widget.setLayout(vertical_box)
        # add every song as a seperate label
        for i in songs:
            song_label = QLabel(i.name)
            vertical_box.addWidget(song_label)
        vertical_box.addStretch()
        self.update_filtered_songs_scroll_area()

    def generate_playlist(self):
        # TODO generate playlist here
        print("TODO: generate playlist here")

    # detects any time a slider value changes
    def slider_value_changed(self, name, values):
        self.feature_sliders[name].slider_values = values

        if self.playlist_loaded:
            song_moved = False
            if self.feature_sliders[name].is_enabled:
                song_moved = self.filtered_playlist.update_feature(name, values[0], values[1])
            else:
                song_moved = self.filtered_playlist.update_feature(name, 0, 100)
            self.update_filtered_songs_values()
            if song_moved:
                self.update_filtered_songs_scroll_area()

    # detects when a feature checkbox has changed
    def feature_checkbox_value_changed(self, name, state):
        # if the checkbox is enabled pass in the values to slider value_changed as is
        self.feature_sliders[name].is_enabled = state
        self.slider_value_changed(name, self.feature_sliders[name].slider_values)
        return

    # updates the labels with current songs in each category
    def update_filtered_songs_values(self):
        total = self.filtered_playlist.get_playlist_length()
        inside_filter = self.filtered_playlist.get_songs_inside_filters_length()
        outside_filter = self.filtered_playlist.get_songs_outside_filters_length()
        self.total_songs.setText("Total Songs: " + str(total))
        self.songs_within_feature_range.setText("Songs in Filter: " + str(inside_filter) +
                                                "(" + "{:.2f}".format(inside_filter/total * 100) + "%)")
        self.songs_outside_feature_range.setText("Songs outside Filter: " + str(outside_filter) +
                                                 "(" + "{:.2f}".format(outside_filter/total * 100) + "%)")

    # updates the songs shown in the filtered scroll area
    def update_filtered_songs_scroll_area(self):
        # grabs list of current filtered songs
        songs = self.filtered_playlist.get_filtered_songs()
        widget = QWidget()
        self.filtered_scroll_area.setWidget(widget)
        vertical_box = QVBoxLayout()
        widget.setLayout(vertical_box)

        # adds each song to the area
        for i in songs:
            song_label = QLabel(i.name)
            vertical_box.addWidget(song_label)
        vertical_box.addStretch()

    # creates a slider with name
    def create_slider(self, parent, name, min, max, is_feature_slider=False):
        # generates the slider label
        check_box = QCheckBox()
        check_box.setChecked(True)
        check_box.setText(name)
        check_box.stateChanged.connect(lambda state: self.feature_checkbox_value_changed(name, check_box.isChecked()))
        parent.addWidget(check_box)

        # generates the slider
        slider = QLabeledRangeSlider(ORIENTATION)
        slider.setRange(min, max)
        slider.setSingleStep(int((max - min) / 100))
        slider.setValue((10, 90))
        slider.valueChanged.connect(lambda e: self.slider_value_changed(name, e))

        # add the sliders to a list of feature sliders
        if(is_feature_slider):
            self.feature_sliders[name] = slider.value()

        parent.addWidget(slider)

    def __init__(self):
        # create a spotify helpers
        self.feature_sliders = {}
        self.spotipy_helpers = SpotipyHelpers()
        self.filtered_playlist = None
        self.playlist_loaded = False

        super().__init__()
        self.setWindowTitle("Spotify Playlist Creator")
        self.resize(1920, 1080)

        # create the layouts
        outer_layout = QHBoxLayout(self)

        column_one = QVBoxLayout(self)
        column_two = QVBoxLayout(self)
        column_three = QVBoxLayout(self)

        # setup for the column 1
        col1Layout = QFormLayout()
        col1Layout.setVerticalSpacing(30)

        self.song_count_label = QLabel()
        self.song_count_label.setText("Which Playlist would you like to load")

        self.combobox = QComboBox(self)
        # reload the playlists currently showing in the dropdown
        self.reload_playlists_dropdown()
        self.combobox.activated[str].connect(self.load_playlist)

        self.pb = QPushButton()
        self.pb.setObjectName("connect")
        self.pb.setText("Re-Load Playlists")
        self.pb.clicked.connect(self.reload_playlists_dropdown)

        self.song_scroll_area = QScrollArea()
        self.song_scroll_area.setWidgetResizable(True)
        self.song_scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)

        col1Layout.addWidget(self.song_count_label)
        col1Layout.addWidget(self.combobox)
        col1Layout.addWidget(self.pb)
        col1Layout.addWidget(self.song_scroll_area)

        column_one.addLayout(col1Layout)

        # load in the features to the center layout
        feature_layout = QHBoxLayout(self)
        first_feature_half = QFormLayout(self)
        first_feature_half.setVerticalSpacing(30)
        features = self.spotipy_helpers.get_song_features()
        # split the features in half
        for index, name in enumerate(features[:int(len(features)/2)]):
            new_feature_slider = FeatureSlider(first_feature_half, name, 0, 100, self.feature_checkbox_value_changed,
                                               self.slider_value_changed, True)
            self.feature_sliders[name] = new_feature_slider
        feature_layout.addLayout(first_feature_half)

        second_feature_half = QFormLayout(self)
        second_feature_half.setVerticalSpacing(30)
        for index, name in enumerate(features[int(len(features) / 2):]):
            new_feature_slider = FeatureSlider(second_feature_half, name, 0, 100, self.feature_checkbox_value_changed,
                                               self.slider_value_changed, True)
            self.feature_sliders[name] = new_feature_slider
        feature_layout.addLayout(second_feature_half)

        column_two.addLayout(feature_layout)

        # add text boxes to show total songs and filtered / unfiltered count
        form_layout = QFormLayout()
        self.total_songs = QLabel()
        self.total_songs.setText("Total Songs: -1")
        self.total_songs.setAlignment(Qt.AlignCenter)
        self.total_songs.setFixedHeight(100)
        form_layout.addWidget(self.total_songs)

        column_two.addLayout(form_layout)

        # TODO turn this into a progress bar look
        # add filter range label
        horz_layout = QHBoxLayout()
        self.songs_within_feature_range = QLabel()
        self.songs_within_feature_range.setText("Songs in Filter: -1")
        self.songs_within_feature_range.setAlignment(Qt.AlignCenter)

        # add outside filter range label
        self.songs_outside_feature_range = QLabel()
        self.songs_outside_feature_range.setText("Songs outside Filter: -1")
        self.songs_outside_feature_range.setAlignment(Qt.AlignCenter)

        horz_layout.addWidget(self.songs_within_feature_range)
        horz_layout.addWidget(self.songs_outside_feature_range)
        column_two.addLayout(horz_layout)
        column_two.addStretch()

        # third section
        self.col3Layout = QFormLayout()
        self.col3Layout.setVerticalSpacing(30)

        self.filtered_scroll_area_title = QLabel()
        self.filtered_scroll_area_title.setText("Filtered Songs")

        self.filtered_scroll_area = QScrollArea()
        self.filtered_scroll_area.setWidgetResizable(True)
        self.filtered_scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)

        self.generate_playlist_pb = QPushButton()
        self.generate_playlist_pb.setObjectName("connect")
        self.generate_playlist_pb.setText("Generate Playlist")
        self.generate_playlist_pb.clicked.connect(self.generate_playlist)

        self.col3Layout.addWidget(self.filtered_scroll_area_title)
        self.col3Layout.addWidget(self.filtered_scroll_area)
        self.col3Layout.addWidget(self.generate_playlist_pb)

        column_three.addLayout(self.col3Layout)

        outer_layout.addLayout(column_one)
        outer_layout.addSpacing(50)
        outer_layout.addLayout(column_two)
        outer_layout.addSpacing(50)
        outer_layout.addLayout(column_three)

        # Set the layout on the application's window
        self.setLayout(outer_layout)

if __name__ == '__main__':
    main()
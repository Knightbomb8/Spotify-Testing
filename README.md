# Spotify-Testing

### Installation and Setup Instructions
Clone the repo.

Go to https://developer.spotify.com/dashboard/applications and create an application. 
Inside the application you can see your client ID and client Secret. Then under edit 
settings in the top right. Here you want to set a redirect URL. It does not need to be
a reachable URL for ex: http://localhost:9090

Now inside the repo you will need to set some environment variables using the command line.
If using Windows use 'set' like below and 'export' if on Linux
```shell
set SPOTIPY_CLIENT_ID='your-spotify-client-id'
set SPOTIPY_CLIENT_SECRET='your-spotify-client-secret'
set SPOTIPY_REDIRECT_URI='your-app-redirect-url'
```

To execute the program run 'python main.py' in which main.py is located in the src folder.

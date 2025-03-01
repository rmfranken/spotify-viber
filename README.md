When listening to music on spotify, this tool makes it possible to display the album art along with some scrolling song information using the spotipy API.

It can be shown on a seperate monitor for increased vibes and aesthetic when listening to music, reminiscent of the old vinyl displays.
## Features

- Display album art and song + artist from Spotify
- Uses the Spotipy API for fetching data
- Can be shown on a separate monitor for enhanced visual experience


### Display Settings

You can customize the display settings and more by modifying the [config.yaml](config.yaml)

## Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/rmfranken/spotify-viber.git
    ```
2. Navigate to the project directory:
    ```bash
    cd spotify-viber
    ```
3. Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```

## Usage
1. Set up your Spotify API credentials. You will need to create a `config.py` file with your `SPOTIPY_CLIENT_ID`, `SPOTIPY_CLIENT_SECRET`, and `SPOTIPY_REDIRECT_URI`. These can be found in your [Spotify Web API Dashboard](https://developer.spotify.com/documentation/web-api).
    ```python
    SPOTIPY_CLIENT_ID = 'your_client_id'
    SPOTIPY_CLIENT_SECRET = 'your_client_secret'
    SPOTIPY_REDIRECT_URI = 'your_redirect_uri'
    ```
2. Run the main script:
    ```bash
    python main.py
    ```

## Configuration

You can customize the display settings by modifying the `config.py` file. Options include screen resolution, refresh rate, and more.

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request.

## License

This project is licensed under the DO WHAT THE FUCK YOU WANT TO PUBLIC LICENSE. See the [LICENSE](LICENSE) file for details.


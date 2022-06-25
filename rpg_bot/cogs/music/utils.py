"""
Utility methods for the Music cog.
"""

def format_duration(total) -> str:
    if total is None:
        return ""

    total = int(total)
    minutes = total//60
    seconds = total - 60*minutes

    return f"{minutes:0>2}:{seconds:0>2}"


def is_spotify_track(url):
    return "open.spotify.com" in url and "track" in url

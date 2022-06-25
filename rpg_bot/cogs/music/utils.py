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


def format_duration_w_hours(total) -> str:
    if total is None:
        return ""

    total = int(total)
    hours = total//3600
    minutes = (total - hours*3600)//60
    seconds = total - 60*minutes - hours*3600

    return f"{hours:0>2}:{minutes:0>2}:{seconds:0>2}"


def from_duration_to_seconds(value: str) -> int:
    splitted = value.split(':')

    if len(splitted) == 3:
        # Contains hours
        return int(splitted[0])*3600 + int(splitted[1])*60 + int(splitted[2])
    elif len(splitted) == 2:
        # Contains only minutes and seconds
        return int(splitted[0])*60 + int(splitted[1])
    else:
        return 0


def is_spotify_track(url):
    return "open.spotify.com" in url and "track" in url

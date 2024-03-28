# =============================================================================
# Minet YouTube Constants
# =============================================================================
#
# General constants used throughout the YouTube functions.
#

YOUTUBE_API_BASE_URL = "https://www.googleapis.com/youtube/v3"
YOUTUBE_API_MAX_VIDEOS_PER_CALL = 50
YOUTUBE_API_MAX_CHANNELS_PER_CALL = 50
YOUTUBE_API_MAX_COMMENTS_PER_CALL = 100

YOUTUBE_API_SEARCH_ORDERS = {
    "relevance",
    "date",
    "rating",
    "viewCount",
    "title",
    "videoCount",
}

YOUTUBE_API_DEFAULT_SEARCH_ORDER = "relevance"

# From: https://stackoverflow.com/questions/17698040/youtube-api-v3-where-can-i-find-a-list-of-each-videocategoryid
YOUTUBE_API_CATEGORIES = {
    "1": "Film & Animation ",
    "2": "Autos & Vehicles",
    "10": "Music",
    "15": "Pets & Animals",
    "17": "Sports",
    "18": "Short Movies",
    "19": "Travel & Events",
    "20": "Gaming",
    "21": "Videoblogging",
    "22": "People & Blogs",
    "23": "Comedy",
    "24": "Entertainment",
    "25": "News & Politics",
    "26": "Howto & Style",
    "27": "Education",
    "28": "Science & Technology",
    "29": "Nonprofits & Activism",
    "30": "Movies",
    "31": "Anime/Animation",
    "32": "Action/Adventure",
    "33": "Classics",
    "34": "Comedy",
    "35": "Documentary",
    "36": "Drama",
    "37": "Family",
    "38": "Foreign",
    "39": "Horror",
    "40": "Sci-Fi/Fantasy",
    "41": "Thriller",
    "42": "Shorts",
    "43": "Shows",
    "44": "Trailers",
}

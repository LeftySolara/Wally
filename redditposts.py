"""
redditposts.py : functions for fetching and filtering reddit posts
"""

import praw


def get_posts(config):
    """Fetch a list of links of wallaper posts"""
    reddit = praw.Reddit(
        user_agent=config['Reddit']['UserAgent'],
        client_id=config['Reddit']['RedditAppId'],
        client_secret=config['Reddit']['RedditSecret'])

    walls = reddit.multireddit(config['Reddit']['MultiredditOwner'],
                               config['Reddit']['MultiredditName'])
    top_posts = walls.top("week")
    posts = []

    for post in top_posts:
        if is_desired_post(post):
            posts.append(post)

    return posts


def is_desired_post(post):
    """Determine if a post is a request, self post, or link to an untested host.

    - Request posts usually have extra text, overlays, etc that need to be
      removed from the image, so we'll ignore those.

    - Fufilled requests require parsing the comments for all edited versions of
      the image, so we'll ignore these too.

    - Most wallpaper subs require walls to be in linked posts,
      so we'll skip self posts.

    - Any url that's a direct link to an image file is fine.
    """
    has_approved_host = False
    is_request = "[request]" in post.title.lower()
    file_types = ("jpg", "jpeg", "png")
    hosts = [
        "imgur.com",
        "iob.imgur.com",
        "i.imgur.com",
        "i.redd.it",
        "i.reddituploads.com",
        "cdn.awwni.me",
        "a.pomf.cat"
    ]

    if (
        any(host in post.url for host in hosts)
        or post.url.endswith(file_types)
    ):
        has_approved_host = True

    if post.link_flair_text:
        flair = post.link_flair_text.lower()
        is_request = ("request" in flair) or ("fulfilled" in flair)

    return (not (is_request or post.is_self)) and has_approved_host

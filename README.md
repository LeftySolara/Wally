# Wally - A Wallpaper Downloader for Reddit

Wally is a program for downloading albums and images from wallpaper multireddits using
[PRAW](https://praw.readthedocs.io/en/latest/) and the [Imgur API](http://api.imgur.com/).
It sorts a multireddit by top/week, downloads a user-defined number of albums and images,
and saves them in zip files in a user-defined directory.

This program is designed to sit on a server and be executed regularly by an automation program like cron.


## How to use

There are a few things you'll need to run Wally:

1. [PRAW](https://praw.readthedocs.io/en/latest/) and [imgurpython](https://github.com/Imgur/imgurpython).
Both can be installed using pip.
2. The name of the multireddit and the username of its owner.
3. A Reddit `client_id`, `client_secret`, and `user_agent`. You can obtain these
by following Reddit's [first steps guide](https://github.com/reddit/reddit/wiki/OAuth2-Quick-Start-Example#first-steps).
You'll need your own Reddit account for this.
4. An Imgur `client_id` and `client_secret`. Get these by following [Imgur's guide](http://api.imgur.com/#registerapp).

Once you have everything, copy the info into a config file called `wally.conf`
in the same directory as the python scripts. This repo contains a sample config file with
all available options. Also, **_remember to never share your API secrets with anyone_**.

Posts that only link to a single image are counted separately from albums with multiple images.
The script will create a subdirectory with a name matching the execution date, put each album into its own zip file,
and combine the standalone images into a separate zip file.
So, for example, if the specified directory is `~/pics/wallpapers/` and
the script is run on 12/11/2016 and 12/18/2016, the file tree will look like this:

```
.
+-- 2016-12-11
|   +-- albums
|       +-- album_name.zip
|       +-- album_name.zip
|   +-- images.zip
+-- 2016-12-18
|   +-- albums
|       +-- album_name.zip
|       +-- album_name.zip
|   +-- images.zip
```

And here is the file tree when compression is turned off:

```
.
+-- 2016-12-11
|   +-- albums
|       +-- album_name
|           +-- filename.png
|           +-- filename.png
|           +-- filename.png
|       +-- album_name
|           +-- filename.png
|           +-- filename.png
|           +-- filename.png
|   +-- images
|       +-- filename.png
|       +-- filename.png
|       +-- filename.png
+-- 2016-12-18
|   +-- albums
|       +-- album_name
|           +-- filename.png
|           +-- filename.png
|           +-- filename.png
|       +-- album_name
|           +-- filename.png
|           +-- filename.png
|           +-- filename.png
|   +-- images
|       +-- filename.png
|       +-- filename.png
|       +-- filename.png
```

The config file allows you to set the number of albums and images to download.
**Try not to set these too high, or you'll quickly hit Imgur's rate limit.**
The program checks the rate limit before checking Imgur URLs, but it's still possible
to hit the limit in the middle of downloading very large albums. You can read
about Imgur's rate limits [here](http://api.imgur.com/#limits).

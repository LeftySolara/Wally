# Reddit Wallpaper Downloader

A script for downloading albums and images from my wallpaper multireddit using
[PRAW](https://praw.readthedocs.io/en/latest/) and the [Imgur API](http://api.imgur.com/).
It sorts the multireddit by top/week, downloads a user-defined number of albums and images,
and saves them in zip files in the specified directory.

This script was designed to sit on a server and be executed each week by something like cron.


## How to use this script

There are a few things you'll need to run this script:

1. [PRAW](https://praw.readthedocs.io/en/latest/) and [imgurpython](https://github.com/Imgur/imgurpython).
Both can be installed using pip.
2. The name of the multireddit and the username of its owner.
3. A Reddit `client_id`, `client_secret`, and `user_agent`. You can get these
by following Reddit's [first steps guide](https://github.com/reddit/reddit/wiki/OAuth2-Quick-Start-Example#first-steps).
You'll need your own Reddit account for this.
4. An Imgur `client_id` and `client_secret`. Get these by following [Imgur's guide](http://api.imgur.com/#registerapp).

These are all stored in `creds.py`. **_Make sure to never share your API secrets with anyone_**.

Once those are set up, specify a directory for the albums and images to be saved to.
Posts that only link to a single image are counted separately from albums and are all combined into one directory.
You can specify the directory in the first line of `main()`. _Make sure to include a trailing slash_.
Under this directory, the script will create a subdirectory with a name matching the
execution date. It then puts each album into its own zip file, and combines the standalone images
into a zip file.
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

You can also tell it not to remove the uncompressed files, which results in a tree like this:

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

To tell the script not to delete the uncompressed files,
just switch `compress_directory(remove=True)` to `compress_directory(remove=False)`.

In `main()` you can also specify the number of albums and images to download.
**Try not to set these too high, or you'll quickly hit Imgur's rate limit.**
The script checks the rate limit before checking Imgur URLs, but it's still possible
to hit the limit in the middle of downloading ridiculously large albums. You can read
about Imgur's rate limits [here](http://api.imgur.com/#limits).

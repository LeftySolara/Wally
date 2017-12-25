from pathlib import Path
from datetime import date
from zipfile import ZipFile, ZIP_DEFLATED
import configparser
import time
import requests
import os

import redditposts
from imgurdownloader import ImgurDownloader
from imgurpython.helpers.error import ImgurClientError

CONFIG_PATH = "wally.conf"
STANDALONE_PATH = "/images/"
ALBUM_PATH = "/albums/"


def create_filename(url):
    """Create a filename for an image based on its host."""
    name = url[url.rfind("/"):] + ".jpg"
    file_types = (".jpg", ".jpeg", ".png")

    # The ImgurDownloader class names the imgur links itself, so we
    # don't need to worry about imgur links.
    if "i.redd.it" in url:
        name = url[url.rfind("/") + 1:url.rfind(
            ".")] + " - reddit" + url[url.rfind("."):]
    elif "i.reddituploads.com" in url:
        # these urls are super long and don't conatin the image's file extension
        name = url[url.find(".com/") + 5:url.find("?")] + " - reddit.png"
    elif "cdn.awwni.me" in url:
        name = url[url.rfind("/") + 1:url.rfind(
            ".")] + " - awwnime" + url[url.rfind("."):]
    elif "a.pomf.cat" in url:
        name = url[url.rfind("/") + 1:url.rfind(
            ".")] + " - apomfcat" + url[url.rfind("."):]
    elif url.endswith(file_types):
        name = url[url.rfind("/"):]

    return name


def compress_directory(directory, remove=False):
    """Compress the given directory into a zip file. If remove is True, then
    delete the original directory after compressing."""
    if directory.endswith("/"):
        directory = directory[:-1]

    zip_file = ZipFile(directory + ".zip", mode='w', compression=ZIP_DEFLATED)
    for root, dirs, files in os.walk(directory):
        rootname = os.path.relpath(root, directory).replace("/", "_")
        for d in dirs:
            pass
        for f in files:
            abspath = os.path.abspath(directory + "/" + rootname + "/" + f)
            relpath = os.path.relpath(abspath, directory)
            zip_file.write(abspath, relpath)
            if remove:
                os.remove(abspath)
        if remove:
            os.rmdir(root)
    zip_file.close()


def main():
    config = configparser.ConfigParser()
    with open("wally.conf") as f:
        config_file = f.readlines()
        config.read_file(config_file, CONFIG_PATH)

    # Parse the config file. IF any settings are undefined set sane defaults.
    download_dir = config['DEFAULT']["DownloadDir"]
    album_limit = config['DEFAULT']['AlbumLimit']
    standalone_limit = config['DEFAULT']['StandaloneLimit']

    if download_dir == "":
        download_dir = str(date.today())

    if not str.isdigit(album_limit):
        print("Invalid value for AlbumLimit. Exiting...")
        return

    if not str.isdigit(standalone_limit):
        print("Invalid value for StandaloneLimit. Exiting...")
        return

    album_limit = int(album_limit)
    standalone_limit = int(standalone_limit)

    # Create the target paths for downloaded images
    path = Path(download_dir + STANDALONE_PATH)
    path.mkdir(exist_ok=True, parents=True)
    path = Path(download_dir + ALBUM_PATH)
    path.mkdir(exist_ok=True, parents=True)


    album_count = 0
    standalone_count = 0
    posts = redditposts.get_posts(config)

    imgur = ImgurDownloader(config['Imgur']['ImgurAppId'],
                            config['Imgur']['ImgurSecret'])
    imgur.image_dir = download_dir + STANDALONE_PATH
    imgur.album_dir = download_dir + ALBUM_PATH
    imgur.minimum_credits = 50

    for post in posts:

        if album_count >= album_limit and standalone_count >= standalone_limit:
            break

        destination = ""
        if "imgur.com" in post.url:
            # check the api rate limit; resets every hour
            user_rate_remaining = int(imgur.user_credits())
            if user_rate_remaining < imgur.minimum_credits:
                print("Approaching rate limit. Sleeping until reset...")
                while user_rate_remaining < imgur.minimum_credits:
                    time.sleep(3600)

            # Imgur is the only host providing albums, so that's all we need to worry about
            if "imgur.com/a/" in post.url:
                is_album = imgur.is_album(post.url)
                if is_album and album_count >= album_limit:
                    continue
                if not is_album and standalone_count >= standalone_limit:
                    continue
            else:
                if standalone_count >= standalone_limit:
                    continue

            print("Downloading imgur post: {}".format(post.title))
            images_downloaded = imgur.download(post.url, post.title)
            if images_downloaded == 1:
                standalone_count += 1
                print("Downloaded image: {}".format(post.url))
            elif images_downloaded > 1:
                album_count += 1
                print("Downloaded album: {}".format(post.url))
        else:
            if standalone_count < standalone_limit:
                print("Downloading image: {}".format(post.title))
                filename = create_filename(post.url)
                destination = destination + download_dir + "/images/" + filename

                with open(destination, 'wb') as handle:
                    response = requests.get(post.url, stream=True)
                    if not response.ok:
                        print(response)

                    for block in response.iter_content(1024):
                        if not block:
                            break
                        handle.write(block)

                standalone_count += 1
                print("Downloaded image: {}".format(post.url))

    compress_directory(download_dir + "/images", True)
    for root, dirs, files in os.walk(download_dir + "/albums"):
        if os.path.basename(root) == "albums":
            continue
        compress_directory(root, True)

    print("Downloaded {} images and {} albums.".format(standalone_count,
                                                       album_count))

    # show rate limits
    print("\nRate Limits:")
    for key, value in imgur.client.credits.items():
        print("{}: {}".format(key, value))


if __name__ == '__main__':
    main()

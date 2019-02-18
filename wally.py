from pathlib import Path
from datetime import date
import configparser
import time
import requests
import os

import redditposts
import filehandler
from imgurdownloader import ImgurDownloader

CONFIG_PATH = "wally.conf"


def main():
    config = configparser.ConfigParser()
    with open("wally.conf") as f:
        config_file = f.readlines()
        config.read_file(config_file, CONFIG_PATH)

    # Parse the config file. IF any settings are undefined set sane defaults.
    download_dir = config['DEFAULT']["DownloadDir"]
    album_limit = config['DEFAULT']['AlbumLimit']
    standalone_limit = config['DEFAULT']['StandaloneLimit']

    if not download_dir.endswith("/"):
        download_dir += "/"
    download_dir += str(date.today())

    if not str.isdigit(album_limit):
        print("Invalid value for AlbumLimit. Exiting...")
        return

    if not str.isdigit(standalone_limit):
        print("Invalid value for StandaloneLimit. Exiting...")
        return

    album_limit = int(album_limit)
    standalone_limit = int(standalone_limit)

    # Create the target paths for downloaded images
    path = Path(download_dir + config['DEFAULT']['StandalonePath'])
    path.mkdir(exist_ok=True, parents=True)
    path = Path(download_dir + config['DEFAULT']['AlbumPath'])
    path.mkdir(exist_ok=True, parents=True)

    album_count = 0
    standalone_count = 0
    posts = redditposts.get_posts(config)

    imgur = ImgurDownloader(config['Imgur']['ImgurAppId'],
                            config['Imgur']['ImgurSecret'])
    imgur.image_dir = download_dir + config['DEFAULT']['StandalonePath']
    imgur.album_dir = download_dir + config['DEFAULT']['AlbumPath']
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

            # Imgur is the only host providing albums,
            # so that's all we need to worry about here
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
                filename = filehandler.create_filename(post.url)
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

    if config['DEFAULT']['Compress'] == "yes":
        remove = (config['DEFAULT']['RemoveAfterCompress'] == "yes")
        filehandler.compress_directory(download_dir + "/images", remove)

        for root, dirs, files in os.walk(download_dir + "/albums"):
            if os.path.basename(root) == "albums":
                continue
            filehandler.compress_directory(root, remove)

    print("Downloaded {} standalone images and {} albums.".format(
        standalone_count, album_count))

    # show rate limits
    print("\nRate Limits:")
    for key, value in imgur.client.credits.items():
        print("{}: {}".format(key, value))


if __name__ == '__main__':
    main()

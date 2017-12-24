from imgurpython import ImgurClient
from imgurpython.helpers.error import ImgurClientError
from pathlib import Path
import requests


class ImgurDownloader(object):
    """Class for downloading images using the official Imgur API"""

    def __init__(self, client_id, client_secret):
        self.client = ImgurClient(client_id, client_secret)
        self.image_dir = "./images/"
        self.album_dir = "./albums/"

    def download(self, url, dir_name):
        """Download content from an Imgur url. If the content is an album, save the
        images under the given directory. Returns number of items downloaded.
        """
        if dir_name.endswith("/"):
            dir_name = dir_name[:-1].replace("/", "_") + "/"
        else:
            dir_name = dir_name.replace("/", "_") + "/"

        imgur_id = self.get_imgur_id(url)
        images_downloaded = 0

        if imgur_id == "":
            return images_downloaded

        try:
            file_types = (".jpg", ".jpeg", ".png")
            if "imgur.com/a/" in url:
                album = self.client.get_album(imgur_id)
                images_downloaded = self.download_album(album, dir_name)
            elif "imgur.com/gallery/" in url:
                # I can't get galleries to work, so just skip them for now
                return 0
            else:
                image_id = self.get_imgur_id(url)
                image = self.client.get_image(image_id)
                self.download_image(image, self.image_dir)
                images_downloaded = 1
        except ImgurClientError as err:
            print("({}) - {}".format(err.status_code, err.error_message))

        return images_downloaded

    def download_album(self, album, dir_name):
        """Download all images from an album and save them to the given destination.
        Returns the number of images that were successfully downloaded.
        """
        if album.images_count == 1:
            self.download_image(album.images[0], self.image_dir)
        else:
            for image in album.images:
                self.download_image(image, self.album_dir + dir_name)
        return album.images_count

    def download_image(self, image, destination="./"):
        """Download image from url and save it to the given destination."""
        if not destination.endswith("/"):
            destination = destination + "/"

        # Image objects obtained from album.images are dicts instead of image objects
        if type(image) is dict:
            image_id = image["id"]
            image_type = image["type"]
            image_link = image["link"]
        else:
            image_id = image.id
            image_type = image.type
            image_link = image.link

        filename = destination + image_id + " - imgur." + image_type[6:]
        filename = filename.replace(".jpeg", ".jpg")

        # Create the destination path and parent directories if necessary.
        path = Path(destination)
        path.mkdir(exist_ok=True, parents=True)
        if not path.exists():
            print("Error: cannot create destination directory {}".format(
                destination))
            return

        with open(filename, 'wb') as handle:
            response = requests.get(image_link, stream=True)
            if not response.ok:
                print(response)

            for block in response.iter_content(1024):
                if not block:
                    break
                handle.write(block)

    def get_imgur_id(self, url):
        """Get Imgur id from image's or album's url."""
        if "imgur" not in url:
            return ""

        imgur_id = url[url.rfind("/") + 1:]

        # Remove any file extensions
        extension_index = imgur_id.find(".")
        if extension_index != -1:
            imgur_id = imgur_id[:extension_index]

        return imgur_id

    def user_credits(self):
        """Fetch the number of user credits remaining. Use for rate-limiting."""
        return self.client.credits["UserRemaining"]

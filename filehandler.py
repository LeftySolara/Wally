"""
filehandler.py : functions for file handling operations
"""

from zipfile import ZipFile, ZIP_DEFLATED
import os


def create_filename(url):
    """Create a filename for an image based on its web host."""
    filename = url[url.rfind("/"):] + ".jpg"
    file_types = (".jpg", ".jpeg", ".png")

    # The ImgurDownloader class names the imgur links itself, so we
    # don't need to worry about them.
    if "i.redd.it" in url:
        filename = url[url.rfind("/") + 1:url.rfind(
            ".")] + " - reddit" + url[url.rfind("."):]
    elif "i.reddituploads.com" in url:
        # these urls are very long and don't conatin the image's file extension
        filename = url[url.find(".com/") + 5:url.find("?")] + " - reddit.png"
    elif "cdn.awwni.me" in url:
        filename = url[url.rfind("/") + 1:url.rfind(
            ".")] + " - awwnime" + url[url.rfind("."):]
    elif "a.pomf.cat" in url:
        filename = url[url.rfind("/") + 1:url.rfind(
            ".")] + " - apomfcat" + url[url.rfind("."):]
    elif url.endswith(file_types):
        filename = url[url.rfind("/"):]

    return filename


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

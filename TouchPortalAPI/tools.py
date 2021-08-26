__copyright__ = """
    This file is part of the TouchPortal-API project.
    Copyright (C) 2021 DamienS

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

import requests
import os
import base64

class Tools():
    """
    A collection of utilities which may be useful for Touch Portal plugins at runtime.
    """

    @staticmethod
    def convertImage_to_base64(image, type="Auto", image_formats=["image/png", "image/jpeg", "image/jpg"]):
        """
        Returns a Base64-encoded representation of an image.

        Args:
            `image` can be a URL or file path.
            `type` can be "Auto", "Web" (for URL), or "Local" (for file path).
            `image_formats` is a list of one or more MIME types to accept, used only with URLs to confirm the response is valid.

        Raises:
            `TypeError`: If URL request returns an invalid MIME type.
            `ValueError`: In other cases such as invalid URL or file path.
        """
        data = None
        if type == "Auto" or type == "Web":
            try:
                r = requests.head(image)
                if r.headers['content-type'] in image_formats:
                    data = requests.get(image).content
                else:
                    raise TypeError(f"Returned image content type ({r.headers['content-type']}) is not one of: {image_formats}")
            except ValueError:  # raised by requests module for invalid URLs, less generic than requests.RequestException
                if type == "Auto":
                    pass
                else:
                    raise
        if not data and (type == "Auto" or type == "Local") and os.path.isfile(image):
            with open(image, "rb") as img_file:
                data = img_file.read()
        if data:
            return base64.b64encode(data).decode('ascii')
        raise ValueError(f"'{image}' is neither a valid URL nor an existing file.")

    @staticmethod
    def updateCheck(name, repository):
        """
        Returns the newest tag name from a GitHub repository.

        Args:
            `name`: the GitHub user name for the URL path.
            `repository`: the GitHub repository name for the URL path.

        Raises:
            `ValueError`: If the repository URL can't be reached, doesn't exist, or doesn't have any tags.
        """
        baselink = f'https://api.github.com/repos/{name}/{repository}/tags'
        if (r := requests.get(baselink)) and r.ok:
            if (js := r.json()):
                return js[0].get('name', "")
            raise ValueError(f'No tags found in repository: {baselink}')
        else:
            raise ValueError(f'Invalid repository URL or response: {baselink}')

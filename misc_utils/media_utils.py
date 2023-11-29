import cv2
import hashlib
import numpy as np
import os
from pathlib import Path
from PIL import ImageGrab, Image
from screeninfo import get_monitors
from typing import Tuple, Optional, Union, List

try:
    from .decorator_utils import export
except ImportError:
    from decorator_utils import export

monitor = [m for m in get_monitors() if m.is_primary][0]
screen_width, screen_height = monitor.width, monitor.height

# No exports here, as the functions aren't tested just yet


def capture_screenshot(
    filepath: Optional[Union[str, Path]] = None,
    x: int = 0,
    y: int = 0,
    width: int = screen_width,
    height: int = screen_height,
    format: str = "png",
    overwrite: bool = False,
) -> str:
    """
    Capture a screenshot given the coordinates (x, y, width, height).

    :param x: The top-left x-coordinate of the screen area to capture (default: 0).
    :param y: The top-left y-coordinate of the screen area to capture (default: 0).
    :param width: The width of the screen area to capture (default: primary monitor width).
    :param height: The height of the screen area to capture (default: primary monitor height).
    :return: The file name where the screenshot is saved.
    """

    image = ImageGrab.grab(bbox=(x, y, x + width, y + height))
    image_hash = hashlib.md5(image.tobytes()).hexdigest()  # default filename

    if filepath is None:
        filepath = Path.cwd() / f"{image_hash}.{format.lower()}"
    filepath = Path(filepath)

    if filepath.exists() is True and overwrite is False:
        raise FileExistsError(
            f"File {filepath} already exists and overwrite is set to False."
        )

    image.save(filepath, format=format.upper())


class ScreenRecorder:
    """
    Screen Recorder class to handle screen recording.
    """

    def __init__(self, x: int = 0, y: int = 0, width: int = None, height: int = None):
        self.x = x
        self.y = y
        if width is None or height is None:
            monitor = get_monitors()[0]
            self.width = monitor.width
            self.height = monitor.height
        else:
            self.width = width
            self.height = height

        self.is_recording = False
        self.out = None
        self.file_name = "temp_recording.avi"

    def start(self) -> None:
        """
        Start the screen recording.
        """
        fourcc = cv2.VideoWriter_fourcc(*"XVID")
        self.out = cv2.VideoWriter(
            self.file_name, fourcc, 20.0, (self.width, self.height)
        )
        self.is_recording = True

        while self.is_recording:
            screen = ImageGrab.grab(
                bbox=(self.x, self.y, self.x + self.width, self.y + self.height)
            )
            frame = np.array(screen)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            self.out.write(frame)

    def stop(self) -> str:
        """
        Stop the screen recording.

        :return: The file name where the recording is saved.
        """
        self.is_recording = False
        if self.out is not None:
            self.out.release()

        cv2.destroyAllWindows()
        md5_hash = generate_md5(self.file_name)
        new_file_name = f"{md5_hash}.avi"
        os.rename(self.file_name, new_file_name)
        return new_file_name

    def save(self, filepath: Union[str, Path]) -> None:
        """
        Save the screen recording to a file.

        :param filepath: The file path to save the recording to.
        """
        if self.out is not None:
            self.out.release()

        cv2.destroyAllWindows()
        os.rename(self.file_name, filepath)

    def screenshot(self, filepath: Union[str, Path]) -> None:
        """
        Take a screenshot of the screen.

        :param filepath: The file path to save the screenshot to.
        """
        image = ImageGrab.grab(
            bbox=(self.x, self.y, self.x + self.width, self.y + self.height)
        )
        image.save(filepath)


class ImageFile:
    def __init__(self, filepath: Union[str, Path]):
        self.filepath = Path(filepath)

        self.directory = self.filepath.parent
        self.filename = self.filepath.name

        self._image = Image.open(self.filepath)

        self.suffix = self.filepath.suffix
        self.format = self.filepath.suffix[1:].lower()
        self.name = self.filepath.stem

    @property
    def hash(self) -> str:
        return hashlib.md5(self._image.tobytes()).hexdigest()

    def move_to(self, dirpath: Union[str, Path]) -> None:
        dirpath = Path(dirpath)
        if not dirpath.is_dir():
            raise NotADirectoryError(f"{dirpath} is not a directory.")

        new_filepath = dirpath / self.filepath.name
        os.rename(self.filepath, new_filepath)
        self.filepath = new_filepath

    def rename_to_hash(self) -> None:
        new_filepath = self.filepath.parent / f"{self.hash}{self.suffix}"
        os.rename(self.filepath, new_filepath)
        self.filepath = new_filepath


class ImageDirectory:
    def __init__(
        self,
        dirpath: Union[str, Path],
        extensions: List[str] = ["jpg", "jpeg", "png", "gif"],
    ):
        self.dirpath = Path(dirpath)
        self.extensions = extensions

    def get_image_files(self) -> List[ImageFile]:
        files = self.dirpath.glob("*")
        image_files = [ImageFile(f) for f in files]
        return [
            f
            for f in image_files
            if f.format in self.extensions and f.filepath.is_file()
        ]

    def get_next_image_file(self) -> Optional[ImageFile]:
        image_files = self.get_image_files()

        try:
            return image_files[1]
        except IndexError:
            return None

    def __iter__(self):
        return iter(self.get_image_files())


if __name__ == "__main__":
    import shutil
    from collections import defaultdict
    from pprint import pprint

    hashes = defaultdict(list)
    image_count = 0

    path = Path("/home/nmischke/Downloads/Shadow-20231117T174601Z-001/Shadow")
    dst_dir = Path("/home/nmischke/Downloads/Shadow-20231117T174601Z-001/Shadow hashed")
    dst_dir.mkdir(exist_ok=True)

    image_dir = ImageDirectory(path)
    for image in image_dir:
        src = image.filepath
        dst = dst_dir / f"{image.image_hash}.{image.image_format}"
        shutil.copy(src, dst)

    #         image_count += 1
    #         hashes[image.image_hash].append(image.filepath)

    # for image_hash, image_files in hashes.items():
    #     if len(image_files) > 1:
    #         print()
    #         print(image_hash)
    #         print(", ".join(sorted([image.name for image in image_files])))

    #         # for image_file in image_files[1:]:
    #         #     image_file.unlink()

    # print(f"Total images: {image_count}, Total unique images: {len(hashes)}")

import os
import shutil
from pathlib import Path

import numpy as np
import pytest

from diffpy.srxplanar.loadimage import LoadImage

PROJECT_ROOT = Path(__file__).resolve().parents[1]

load_image_param = [
    # case 1: just filename of file in current directory.
    # expect function loads tiff file from cwd
    ("example.tiff", True),
    # case 2: absolute file path to file in another directory.
    # expect file is found and correctly read.
    ("home_dir/example.tiff", True),
    # case 3: relative file path to file in another directory.
    # expect file is found and correctly read
    ("./example.tiff", True),
    # case 4: non-existent file that incurred by mistype.
    ("nonexistent_file.tif", False),
]


@pytest.mark.parametrize("input_path, expected", load_image_param)
def test_load_image_cases(input_path, expected, user_filesystem):
    base_dir, home_dir, cwd_dir, test_dir = user_filesystem
    test_file_dir = Path(__file__).parent
    cwd_dir = test_file_dir / "cwd"
    home_dir = test_file_dir / "home"
    test_dir = test_file_dir / "test"
    src_image = test_file_dir.parent / "docs/examples/example.tiff"

    # Copy test image into all directories
    for dir in [cwd_dir, home_dir, test_dir]:
        dst = Path(dir) / "example.tiff"
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(src_image, dst)

    old_cwd = Path.cwd()
    os.chdir(home_dir)

    try:
        cfg = type(
            "Cfg", (), {"fliphorizontal": True, "flipvertical": False}
        )()
        loader = LoadImage(cfg)

        if expected:
            # Handle case 1-3 for absolute, cwd, and home directory.
            actual = loader.loadImage(input_path)
            assert isinstance(actual, np.ndarray)
        else:
            # Handle Case 4 for missing file.
            with pytest.raises(
                FileNotFoundError,
                match=r"file not found: .*"
                r"Please rerun specifying a valid filename\.",
            ):
                loader.loadImage(input_path)
    finally:
        os.chdir(old_cwd)

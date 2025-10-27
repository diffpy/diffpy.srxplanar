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
    home_dir = user_filesystem["home"]
    cwd_dir = user_filesystem["cwd"]
    os.chdir(cwd_dir)

    # locate source example file inside project docs
    source_file = PROJECT_ROOT / "docs" / "examples" / "example.tiff"
    shutil.copy(source_file, cwd_dir / "example.tiff")
    shutil.copy(source_file, home_dir / "example.tiff")

    old_cwd = Path.cwd()
    os.chdir(home_dir)

    try:
        cfg = type(
            "Cfg", (), {"fliphorizontal": True, "flipvertical": False}
        )()
        loader = LoadImage(cfg)
        actual = loader.loadImage(input_path)
        assert isinstance(actual, np.ndarray)
    except FileNotFoundError:
        pytest.raises(
            FileNotFoundError,
            match=r"file not found:"
            r" .*Please rerun specifying a valid filename\.",
        )
    finally:
        os.chdir(old_cwd)

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
    ("KFe2As2-00838.tif", True),
    # case 2: absolute file path to file in another directory.
    # expect file is found and correctly read.
    ("home_dir/KFe2As2-00838.tif", True),
    # case 3: relative file path to file in another directory.
    # expect file is found and correctly read
    ("./KFe2As2-00838.tif", True),
    # case 4: non-existent file that incurred by mistype.
    ("nonexistent_file.tif", FileNotFoundError),
]


@pytest.mark.parametrize("input_path, expected", load_image_param)
def test_load_image(input_path, expected, user_filesystem):
    home_dir = user_filesystem["home"]
    cwd_dir = user_filesystem["cwd"]
    os.chdir(cwd_dir)

    # locate source example file inside project docs
    source_file = PROJECT_ROOT / "docs" / "examples" / "KFe2As2-00838.tif"
    shutil.copy(source_file, cwd_dir / "KFe2As2-00838.tif")
    shutil.copy(source_file, home_dir / "KFe2As2-00838.tif")

    try:
        cfg = type(
            "Cfg", (), {"fliphorizontal": True, "flipvertical": False}
        )()
        loader = LoadImage(cfg)
        actual = loader.loadImage(input_path)
        expected = loader.loadImage(source_file)
        assert np.array_equal(actual, expected)
    except FileNotFoundError:
        pytest.raises(
            FileNotFoundError,
            match=r"file not found:"
            r" .*Please rerun specifying a valid filename\.",
        )

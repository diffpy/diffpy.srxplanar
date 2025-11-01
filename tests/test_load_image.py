import os
import shutil
from pathlib import Path
from unittest.mock import Mock

import pytest

from diffpy.srxplanar.loadimage import LoadImage

PROJECT_ROOT = Path(__file__).resolve().parents[1]

load_image_param = [
    # case 1: just filename of file in current directory.
    # expect function loads tiff file from cwd
    ("KFe2As2-00838.tif", Mock(fliphorizontal=False, flipvertical=False), 0),
    # case 2: absolute file path to file in another directory.
    # expect file is found and correctly read.
    (
        "home_dir/KFe2As2-00838.tif",
        Mock(fliphorizontal=True, flipvertical=False),
        102,
    ),
    # case 3: relative file path to file in another directory.
    # expect file is found and correctly read
    ("./KFe2As2-00838.tif", Mock(fliphorizontal=False, flipvertical=True), 39),
    # case 4: non-existent file that incurred by mistype.
    (
        "nonexistent_file.tif",
        Mock(fliphorizontal=False, flipvertical=False),
        FileNotFoundError,
    ),
]


@pytest.mark.parametrize(
    "file_name, config, expected_entry_value", load_image_param
)
def test_load_image(file_name, config, expected_entry_value, user_filesystem):
    home_dir = user_filesystem["home"]
    cwd_dir = user_filesystem["cwd"]
    os.chdir(cwd_dir)

    expected_mean = 2595.7087
    expected_shape = (2048, 2048)

    # locate source example file inside project docs
    source_file = (
        PROJECT_ROOT / "docs" / "examples" / "data" / "KFe2As2-00838.tif"
    )
    shutil.copy(source_file, cwd_dir / "KFe2As2-00838.tif")
    shutil.copy(source_file, home_dir / "KFe2As2-00838.tif")

    try:
        loader = LoadImage(config)
        actual = loader.load_image(file_name)
        assert actual.shape == expected_shape
        assert actual.mean() == expected_mean
        assert actual[1][0] == expected_entry_value
    except FileNotFoundError:
        pytest.raises(
            FileNotFoundError,
            match=r"file not found:"
            r" .*Please rerun specifying a valid filename\.",
        )

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
    "KFe2As2-00838.tif",
    # case 2: absolute file path to file in another directory.
    # expect file is found and correctly read.
    "home_dir/KFe2As2-00838.tif",
    # case 3: relative file path to file in another directory.
    # expect file is found and correctly read
    "./KFe2As2-00838.tif",
    # case 4: non-existent file that incurred by mistype.
    "nonexistent_file.tif",
]


@pytest.mark.parametrize("file_name", load_image_param)
def test_load_image(file_name, user_filesystem):
    home_dir = user_filesystem["home"]
    cwd_dir = user_filesystem["cwd"]
    os.chdir(cwd_dir)

    # These values were obtained from docs/examples/data/KFe2As2-00838.tif
    expected_mean = 2595.7087
    expected_shape = (2048, 2048)
    expected_first_point = 0
    expected_last_point = 0

    # locate source example file inside project docs
    source_file = (
        PROJECT_ROOT / "docs" / "examples" / "data" / "KFe2As2-00838.tif"
    )
    shutil.copy(source_file, cwd_dir / "KFe2As2-00838.tif")
    shutil.copy(source_file, home_dir / "KFe2As2-00838.tif")

    try:
        loader = LoadImage(Mock(fliphorizontal=False, flipvertical=False))
        actual = loader.load_image(file_name)
        assert actual.shape == expected_shape
        assert actual.mean() == expected_mean
        assert actual[0][0] == expected_first_point
        assert actual[-1][-1] == expected_last_point
    except FileNotFoundError:
        pytest.raises(
            FileNotFoundError,
            match=r"file not found:"
            r" .*Please rerun specifying a valid filename\.",
        )

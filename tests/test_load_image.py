import os
import shutil
from pathlib import Path
from types import SimpleNamespace

import pytest

from diffpy.srxplanar.loadimage import LoadImage

PROJECT_ROOT = Path(__file__).resolve().parents[1]

load_image_param = [
    # case 1: just filename of file in current directory.
    # expect function loads tiff file from cwd
    (["KFe2As2-00838.tif", False, False], [0, 26, 173]),
    # case 2: absolute file path to file in another directory.
    # expect file is found and correctly read.
    (
        ["home_dir/KFe2As2-00838.tif", True, False],
        [102, 57, 136],
    ),
    # case 3: relative file path to file in another directory.
    # expect file is found and correctly read
    (["./KFe2As2-00838.tif", False, True], [39, 7, 0]),
    # case 4: non-existent file that incurred by mistype.
    (
        ["nonexistent_file.tif", False, False],
        FileNotFoundError,
    ),
    # case 5: relative file path to file in another directory.
    # expect file to be flip both horizontally and vertically
    # and correctly read
    (["./KFe2As2-00838.tif", True, True], [0, 53, 21]),
]


@pytest.mark.parametrize("inputs, expected", load_image_param)
def test_load_image(inputs, expected, user_filesystem):
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
    config = SimpleNamespace(fliphorizontal=inputs[1], flipvertical=inputs[2])
    try:
        loader = LoadImage(config)
        actual = loader.load_image(inputs[0])
        assert actual.shape == expected_shape
        assert actual.mean() == expected_mean
        assert actual[1][0] == expected[0]
        assert actual[1][1] == expected[1]
        assert actual[2][5] == expected[2]
    except FileNotFoundError:
        pytest.raises(
            FileNotFoundError,
            match=r"file not found:"
            r" .*Please rerun specifying a valid filename\.",
        )

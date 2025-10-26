import os
from pathlib import Path
from unittest import mock

import numpy as np
import pytest

from diffpy.srxplanar.loadimage import LoadImage

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def reference_matrix():
    """Load reference matrix directly from the example TIFF."""
    tif_path = PROJECT_ROOT / "docs/examples/KFe2As2-00838.tif"
    cfg = type("Cfg", (), {"fliphorizontal": True, "flipvertical": False})()
    image_loader = LoadImage(cfg)
    return image_loader.loadImage(tif_path)


def build_loadimage_path(case_tag, home_dir):
    """Return the Path object for LoadImage test cases.

    case_tag: one of 'abs', 'rel', 'missing'
    """
    if case_tag == "abs":
        return home_dir / "diffpy.srxplanar/docs/examples/KFe2As2-00838.tif"
    elif case_tag == "rel":
        return Path("diffpy.srxplanar/docs/examples/KFe2As2-00838.tif")
    elif case_tag == "missing":
        return Path("nonexistent_file.tif")


load_image_param = load_image_params = [
    ("abs", PROJECT_ROOT / "docs/examples/KFe2As2-00838.tif"),
    ("rel", PROJECT_ROOT / "docs/examples/KFe2As2-00838.tif"),
    ("missing", PROJECT_ROOT / "docs/examples/KFe2As2-00838.tif"),
]


@pytest.mark.parametrize("case_tag,expected_path", load_image_params)
def test_load_image_cases(
    user_filesystem, monkeypatch, case_tag, expected_path
):
    home_dir = user_filesystem["home"]
    test_dir = user_filesystem["test"]

    cfg = type("Cfg", (), {"fliphorizontal": True, "flipvertical": False})()
    loader = LoadImage(cfg)

    with mock.patch.dict(os.environ, {"HOME": str(home_dir)}):
        expected = loader.loadImage(expected_path)

    expected = loader.loadImage(expected_path)

    abs_file = home_dir / "diffpy.srxplanar/docs/examples/KFe2As2-00838.tif"
    abs_file.parent.mkdir(parents=True, exist_ok=True)
    abs_file.write_bytes(expected_path.read_bytes())

    rel_dir = test_dir / "diffpy.srxplanar/docs/examples"
    rel_dir.mkdir(parents=True, exist_ok=True)
    rel_file = rel_dir / "KFe2As2-00838.tif"
    rel_file.write_bytes(expected_path.read_bytes())

    cwd = Path.cwd()
    os.chdir(test_dir)
    try:
        input_path = build_loadimage_path(case_tag, home_dir)
        result = loader.loadImage(input_path)

        if case_tag == "missing":
            assert result.shape == (100, 100)
            assert np.all(result == 0)
        else:
            assert np.array_equal(result, expected)
    finally:
        os.chdir(cwd)

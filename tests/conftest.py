import json
import os
from pathlib import Path

import numpy as np
import pytest

from diffpy.srxplanar.loadimage import LoadImage


# ----------------------------------------------------------------------
# Filesystem fixture following the structured format
# ----------------------------------------------------------------------
@pytest.fixture
def user_filesystem(tmp_path):
    base_dir = Path(tmp_path)
    input_dir = base_dir / "input_dir"
    home_dir = base_dir / "home_dir"
    test_dir = base_dir / "test_dir"
    for d in (input_dir, home_dir, test_dir):
        d.mkdir(parents=True, exist_ok=True)

    home_config_data = {
        "username": "home_username",
        "email": "home@email.com",
    }
    with open(home_dir / "diffpyconfig.json", "w") as f:
        json.dump(home_config_data, f)

    yield {
        "base": base_dir,
        "input": input_dir,
        "home": home_dir,
        "test": test_dir,
    }


# ----------------------------------------------------------------------
# LoadImage test setup
# ----------------------------------------------------------------------
@pytest.fixture(scope="module")
def example_tif():
    """Locate the example TIFF file relative to repo root."""
    tif_path = Path("../docs/examples/KFe2As2-00838.tif").resolve()
    if not tif_path.exists():
        pytest.skip(f"Example TIFF not found at {tif_path}")
    return tif_path


@pytest.fixture(scope="module")
def reference_matrix(example_tif):
    """Load reference matrix directly from the example TIFF once per
    session."""
    cfg = type("Cfg", (), {"fliphorizontal": True, "flipvertical": False})()
    loader = LoadImage(cfg)
    return loader.loadImage(example_tif)


@pytest.fixture
def loader():
    cfg = type("Cfg", (), {"fliphorizontal": True, "flipvertical": False})()
    return LoadImage(cfg)


# ----------------------------------------------------------------------
# Unified test
# ----------------------------------------------------------------------


def test_load_image_all_cases(
    loader, example_tif, user_filesystem, monkeypatch
):
    home_dir = user_filesystem["home"]
    test_dir = user_filesystem["test"]
    monkeypatch.setenv("HOME", str(home_dir))

    # Load once as ground truth
    expected = loader.loadImage(example_tif)

    # ---- Case 1: absolute path ----
    abs_tif = home_dir / "diffpy.srxplanar/docs/examples/KFe2As2-00838.tif"
    abs_tif.parent.mkdir(parents=True, exist_ok=True)
    abs_tif.write_bytes(example_tif.read_bytes())
    result_abs = loader.loadImage(abs_tif)
    assert np.array_equal(result_abs, expected)

    # ---- Case 2 & 3: CWD and relative ----
    cwd_tif = test_dir / example_tif.name
    cwd_tif.write_bytes(example_tif.read_bytes())

    rel_dir = test_dir / "diffpy.srxplanar/docs/examples"
    rel_dir.mkdir(parents=True, exist_ok=True)
    rel_tif = rel_dir / example_tif.name
    rel_tif.write_bytes(example_tif.read_bytes())

    cwd = Path.cwd()
    os.chdir(test_dir)
    try:
        result_cwd = loader.loadImage(example_tif.name)
        assert np.array_equal(result_cwd, expected)

        relative_path = (
            Path("diffpy.srxplanar/docs/examples") / example_tif.name
        )
        result_rel = loader.loadImage(relative_path)
        assert np.array_equal(result_rel, expected)

        # ---- Case 4: missing file ----
        result_missing = loader.loadImage("nonexistent_file.tif")
        assert result_missing.shape == (100, 100)
        assert np.all(result_missing == 0)

    finally:
        os.chdir(cwd)

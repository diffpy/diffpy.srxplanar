import json
from pathlib import Path

import pytest


@pytest.fixture
def user_filesystem(tmp_path):
    base_dir = Path(tmp_path)
    input_dir = base_dir / "input_dir"
    home_dir = base_dir / "home_dir"
    test_dir = base_dir / "test_dir"
    for dir in (input_dir, home_dir, test_dir):
        dir.mkdir(parents=True, exist_ok=True)

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

import logging
from pathlib import Path

from dotenv import load_dotenv

project_root = Path(__file__).parent.parent
env_test_path = project_root / ".env.test"

if env_test_path.exists():
    load_dotenv(env_test_path, override=True)
    logging.info("Loaded optional test environment from %s", env_test_path)
else:
    logging.info("No .env.test found at %s; local/mock tests will run and remote tests skip by env.", env_test_path)


def pytest_configure(config):
    logger = logging.getLogger("autobyteus")
    logger.setLevel(logging.DEBUG)

    if any(getattr(handler, "_image_audio_test_handler", False) for handler in logger.handlers):
        return

    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    ch._image_audio_test_handler = True

    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    ch.setFormatter(formatter)

    logger.addHandler(ch)

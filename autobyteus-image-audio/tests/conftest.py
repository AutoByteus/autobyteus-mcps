import logging
from pathlib import Path

from dotenv import load_dotenv

# Eagerly load test environment on import
project_root = Path(__file__).parent.parent
env_test_path = project_root / ".env.test"

if not env_test_path.exists():
    raise FileNotFoundError(
        f"CRITICAL: Test environment file not found at '{env_test_path}'. Tests cannot proceed."
    )

load_dotenv(env_test_path, override=True)
logging.info(f"Successfully loaded test environment from {env_test_path}")


def pytest_configure(config):
    logger = logging.getLogger("autobyteus")
    logger.setLevel(logging.DEBUG)

    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)

    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    ch.setFormatter(formatter)

    logger.addHandler(ch)

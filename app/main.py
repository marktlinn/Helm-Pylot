import subprocess
import sys

from .logger import logger


def run_cmd(cmd_list: list[str]) -> None:
    cmd_str = " ".join(cmd_list)
    logger.info(f"\n---> Executing command: {cmd_str}")

    try:
        result = subprocess.run(
            cmd_list, check=True, text=True, capture_output=True, encoding="utf-8"
        )
        logger.info("Stdout:\n", result.stdout.strip())
        if result.stderr:
            logger.error("Stderr:\n", result.stderr.strip())

    except subprocess.CalledProcessError as e:
        logger.error(f"\nCommand failed with code {e.returncode}: {cmd_str}")
        logger.error("--- Stderr ---\n", e.stderr)
        logger.error("--- Stdout ---\n", e.stdout)
        sys.exit(1)
    except FileNotFoundError:
        logger.error(
            f"\nCommand not found. Are all required CLI tools installed and in PATH? {cmd_str}"
        )
        sys.exit(1)

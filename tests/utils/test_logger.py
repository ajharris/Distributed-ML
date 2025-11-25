import logging
from src.utils.logger import get_logger


def test_get_logger_basic():
    logger = get_logger("test_logger", json_logs=False)
    assert isinstance(logger, logging.Logger)
    assert logger.level == logging.INFO


def test_logger_json_format(tmp_path):
    log_file = tmp_path / "test.json"
    logger = get_logger("json_logger", log_file=str(log_file), json_logs=True)
    logger.info("hello")

    contents = log_file.read_text()
    assert "hello" in contents
    assert contents.strip().startswith("{")  # looks like JSON

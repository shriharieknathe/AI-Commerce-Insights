import logging
from config import config


class AppLogger:
    def __init__(self, log_file_name):
        self.__logger = logging.getLogger(__name__)
        self.__set_log_handlers(log_file_name)

    def __set_log_handlers(self, log_file_name):
        self.__handlers = []
        self.__handlers.append(logging.FileHandler(log_file_name))

        if config["logger"]["handlers"]["streamhandler"]:
            self.__handlers.append(logging.StreamHandler())

        # Configure the logger
        self.__logger.setLevel(config["logger"]["level"])
        formatter = logging.Formatter(config["logger"]["format"])
        for handler in self.__handlers:
            handler.setFormatter(formatter)
            self.__logger.addHandler(handler)

        # Disable propagation to prevent logs from being passed to the root logger
        self.__logger.propagate = False

    def log(self, level, message, **kwargs):
        methodname = kwargs.get("methodname", "")
        classname = kwargs.get("classname", "")
        username = kwargs.get("username", "")
        self.__logger.log(level, message, extra={"methodname": methodname, "classname": classname, "username": username})

    def debug(self, message, **kwargs):
        self.log(logging.DEBUG, message, **kwargs)

    def info(self, message, **kwargs):
        self.log(logging.INFO, message, **kwargs)

    def warning(self, message, **kwargs):
        self.log(logging.WARNING, message, **kwargs)

    def error(self, message, **kwargs):
        self.log(logging.ERROR, message, **kwargs)

    def critical(self, message, **kwargs):
        self.log(logging.CRITICAL, message, **kwargs)

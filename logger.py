import logging


class Logger():
    @staticmethod
    def get_logger(name, ):
        new_logger = logging.getLogger(name)

        new_handler = logging.FileHandler(f"log/{name}.log", mode='w')
        new_formatter = logging.Formatter("%(name)s %(asctime)s %(levelname)s %(message)s")

        new_handler.setFormatter(new_formatter)
        new_logger.addHandler(new_handler)

        return new_logger
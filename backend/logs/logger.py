import logging
import os
from pathlib import Path


class Logger:
    def __init__(self, name=__name__, level=logging.INFO):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)

        # Создаем директорию для логов, если она не существует
        log_directory = Path(__file__).parent / 'logs'
        log_directory.mkdir(exist_ok=True)

        # Настраиваем FileHandler для записи в файл в папке logs
        log_file = log_directory / f"{name}.log"
        file_handler = logging.FileHandler(log_file)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s\n%(message)s\n')
        file_handler.setFormatter(formatter)

        # Добавляем FileHandler к нашему logger'у
        self.logger.addHandler(file_handler)

    def get_logger(self):
        return self.logger
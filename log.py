import logging
import colorama

from datetime import datetime

colors = {
    'BOLD_RED': '\x1b[31;1m',
    'WHITE': '\x1b[38;21m',
    'YELLOW': '\033[93m',
    'GREEN': '\033[92m',
    'RESET': '\x1b[0m',
    'CYAN': '\033[96m',
    'RED': '\033[91m'
}

formats = {
    logging.DEBUG: colors['GREEN'],
    logging.INFO: colors['WHITE'],
    logging.WARNING: colors['YELLOW'],
    logging.ERROR: colors['RED'],
    logging.CRITICAL: colors['BOLD_RED']
}

class ColoredFormatter(logging.Formatter):
    def format(self, record):
        date_fmt = color('[%(asctime)s]', colors['CYAN'])
        module_fmt = color('[%(module)s]', colors['YELLOW'])
        msg_fmt = color('(%(levelname)s) %(message)s', formats[record.levelno])

        formatter = logging.Formatter(
            fmt=f'{date_fmt} {module_fmt} {msg_fmt}', 
            datefmt='%H:%M:%S'
        )
        
        return formatter.format(record)


def color(text, color):
    return color + text + colors['RESET']


def setup_logger():
    colorama.init()

    logger = logging.getLogger('IFTMBot')
    logger.setLevel(logging.DEBUG)

    f_handler = logging.FileHandler(
        f'./logs/{datetime.now().strftime("%Y-%m-%d")}.log'
    )

    f_handler.setFormatter(
        logging.Formatter(
            fmt='[%(asctime)s] [%(module)s] (%(levelname)s) %(message)s',
            datefmt='%H:%M:%S'
        )
    )

    f_handler.setLevel(logging.DEBUG)
    logger.addHandler(f_handler)

    s_handler = logging.StreamHandler()
    s_handler.setFormatter(ColoredFormatter())
    
    logger.addHandler(s_handler)

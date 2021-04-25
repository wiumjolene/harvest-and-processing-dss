import logging
from src.data.make_dataset import vakansie


if __name__ == '__main__':
    log_fmt = '%(asctime)s - %(levelname)s - %(name)s - %(message)s'
    logging.basicConfig(level=logging.INFO, format=log_fmt)

    v = vakansie()
    v.lekker()
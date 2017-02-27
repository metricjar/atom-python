import logging
import logging.handlers


def get_logger(name="AtomLogger", debug=False, file_name="atom-raw.json"):
    """
    Atom Logger factory: If AtomRawLogger == name then it will return a rotating-file logger, else just logs to stdout.
    :param name: logger name
    :param debug: Disable/enable debug printing
    :return:
    """
    logger = logging.getLogger(name)
    new_level = logging.DEBUG if debug else logging.INFO

    if name == "AtomRawLogger":
        logger.setLevel(logging.INFO)
        ch = logging.handlers.RotatingFileHandler(file_name,
                                                  encoding="utf8",
                                                  maxBytes=10 * 1024 * 1024,
                                                  backupCount=100)
        ch.setLevel(logging.INFO)
        logger.addHandler(ch)
        logger.propagate = 0
        return logger

    if logger.level == logging.NOTSET or logger.level != new_level:
        logger.setLevel(new_level)

        # Create console handler and set level to debug
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)

        # Create formatter
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        # add formatter to ch
        ch.setFormatter(formatter)

        # add ch to logger
        if len(logger.handlers) == 0:
            logger.addHandler(ch)
        else:
            # case we already have a stdout handler and we want to change its level
            logger.handlers[0].level = new_level

        logger.propagate = 0
        logger.info('Starting Logger: {}, debug: {}'.format(name, debug))
    return logger

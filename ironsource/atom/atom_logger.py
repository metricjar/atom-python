import logging


def get_logger(name="AtomLogger", debug=False):

        logger = logging.getLogger(name)
        new_level = logging.DEBUG if debug else logging.INFO

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

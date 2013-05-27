def _init_log():
    import logging
    from logging.handlers import SysLogHandler

    logger = logging.getLogger(request.application)
    logger.setLevel(logging.DEBUG)
    handler = logging.FileHandler("/home/www-data/web2py/applications/hello/helloweb2py.log")
    handler.setFormatter(logging.Formatter('%s' % request.application + '[%(process)d]: %(levelname)s:%(filename)s at line %(lineno)d: %(message)s'))
    handler.setLevel(logging.DEBUG) 
    logger.addHandler(handler) 
    return logger
logging=cache.ram('once',lambda:_init_log(),time_expire=99999999)

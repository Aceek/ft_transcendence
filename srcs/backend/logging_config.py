from pythonjsonlogger import jsonlogger

log_config = {
    "version": 1,
    "formatters": {
        "json": {
            "()": jsonlogger.JsonFormatter,
            "fmt": "%(levelname)s %(name)s %(message)s %(asctime)s",
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "json",
        }
    },
    "loggers": {
        "uvicorn": {
            "handlers": ["console"],
            "level": "INFO",
        },
        "uvicorn.error": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
        "uvicorn.access": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
    },
}

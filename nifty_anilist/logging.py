import structlog


anilist_logger = structlog.wrap_logger(
    structlog.get_logger(),
    processors=[
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.dev.ConsoleRenderer(colors=True)
    ],
    wrapper_class=structlog.stdlib.BoundLogger,
)

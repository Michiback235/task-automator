from __future__ import annotations

import logging


def setup_logging(verbose: bool = False, quiet: bool = False) -> None:
    level = logging.INFO
    if verbose:
        level = logging.DEBUG
    if quiet:
        level = logging.WARNING
    logging.basicConfig(
        level=level,
        format="%(levelname)s %(asctime)s %(name)s - %(message)s",
        datefmt="%H:%M:%S",
    )
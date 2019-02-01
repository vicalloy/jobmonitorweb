try:
    from .local import *  # NOQA
except ImportError as e:
    from .dev import *  # NOQA
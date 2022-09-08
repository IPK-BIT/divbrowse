from ._version import _version
__version__ = _version

import sys
import logging
logging.basicConfig(stream=sys.stderr, level=logging.INFO)
log = logging.getLogger(__name__)
from ._version import _version
__version__ = _version

import sys
import logging


logging.basicConfig(stream=sys.stderr, level=logging.INFO)
log = logging.getLogger(__name__)


logging.getLogger('numexpr').setLevel(logging.WARNING)
logging.getLogger('numba').setLevel(logging.WARNING)
logging.getLogger('h5py').setLevel(logging.WARNING)
logging.getLogger('matplotlib').setLevel(logging.WARNING)
logging.getLogger('matplotlib.font_manager').setLevel(logging.WARNING)
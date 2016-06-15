# Enable other layers to have extensions in the same named directory.
from pkgutil import extend_path
__path__ = extend_path(__path__, __name__)

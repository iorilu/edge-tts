"""edge-tts allows you to use Microsoft Edge's online text-to-speech service without
needing Windows or the Edge browser."""

from . import exceptions
from .communicate import Communicate
from .submaker import SubMaker
from .version import __version__, __version_info__
from .voices import VoicesManager, list_voices

__all__ = [
    "Communicate",
    "SubMaker",
    "exceptions",
    "__version__",
    "__version_info__",
    "VoicesManager",
    "list_voices",
]

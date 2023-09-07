# Components
from .components import *  # noqa
from .components.authentication import *  # noqa
from .components.base import *  # noqa
from .components.crispy import *  # noqa
from .components.databases import *  # noqa
from .components.email import *  # noqa
from .components.installed_apps import *  # noqa
from .components.logging import *  # noqa
from .components.middlewares import *  # noqa
from .components.notifications import *  # noqa
from .components.rest_framework import *  # noqa
from .components.rq import *  # noqa
from .components.static import *  # noqa
from .components.templates import *  # noqa

# Envs
settings_env = env.get_value("ENVIRONMENT", default="local")  # noqa

if settings_env == "local":
    from .environments.local import *  # noqa
elif settings_env == "production":
    from .environments.production import *  # noqa

# Override settings:
try:
    from .environments.override import *  # noqa
except ImportError:
    pass

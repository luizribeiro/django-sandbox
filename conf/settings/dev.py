from conf.settings.common import *

# @threaded_async (or the asyncio loop) is giving trouble in debug mode :/
DEBUG = False

TEST_RUNNER = "green.djangorunner.DjangoRunner"


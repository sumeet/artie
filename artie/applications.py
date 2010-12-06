import os
import re
import sys

from . import settings

triggers = set()
timers = set()

class BadApplicationError(Exception): pass

def trigger(expression):
    def decorator(func):
        triggers.add((re.compile(expression), func))
    return decorator

def timer(time):
    def decorator(func):
        timers.add((time, func))
    return decorator

sys.path.insert(0, settings.APPLICATION_PATH)

for filename in os.listdir(settings.APPLICATION_PATH):
    if filename != '__init__.py' and filename.endswith('.py'):
        if filename == 'triggers.py':
            raise BadApplicationError(
                "Application file can't be called triggers.py"
            )
        module = filename[:-3]
        if module in sys.modules:
            reload(sys.modules[module])
        else:
            __import__(module, locals(), globals())

import os
import sys
import yaml

DEFAULT_SETTINGS_FILENAME = 'settings.yaml'

if sys.argv[0] == 'artie-run.py':
    try:
        settings_file = sys.argv[1]
    except IndexError:
        settings_file = DEFAULT_SETTINGS_FILENAME
else:
    settings_file = DEFAULT_SETTINGS_FILENAME

try:
    settings = yaml.load(open(os.path.abspath(settings_file)))
except IOError:
    print "Error: Settings file '%s' doesn't exist." % settings_file
    sys.exit(1)

for setting, value in settings.iteritems():
    setattr(sys.modules[__name__], setting, value)

if not settings.get('APPLICATION_PATH'):
    settings_directory = os.path.dirname(os.path.abspath(settings_file))
    APPLICATION_PATH = os.path.join(settings_directory, 'applications')
else:
    APPLICATION_PATH = os.path.dirname(APPLICATION_PATH)

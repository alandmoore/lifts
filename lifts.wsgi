import sys
import os.path

path = os.path.realpath(os.path.dirname(__file__))
virtualenv_path = os.path.join(path, "env")

# activate virtualenv if it exists
activate_this = os.path.join(virtualenv_path, "bin/activate_this.py")
if os.path.exists(activate_this):
    print("Using virtualenv at {}.".format(virtualenv_path))
    with open(activate_this) as f:
        code = compile(f.read(), activate_this, 'exec')
        exec(code, dict(__file__=activate_this))
else:
    print("{} not found, using system python.".format(virtualenv_path))
sys.path.insert(0, path)

from lifts import app

if app.config.get("DEBUG"):
    from werkzeug.debug import DebuggedApplication
    application = DebuggedApplication(app, True)
else:
    application = app

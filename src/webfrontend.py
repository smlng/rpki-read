import os
import sys

sys.path.append(os.path.dirname(__name__))

from app import app
from settings import *

app.run(host=webfrontend['host'], webfrontend['port'], debug=True)

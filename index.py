import os
import sys

# Add the current directory to Python path
current_dir = os.path.dirname(__file__)
sys.path.insert(0, current_dir)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')

from myproject.wsgi import application
from vercel_wsgi import make_app

app = make_app(application)
import os
import sys
import django
from django.core.wsgi import get_wsgi_application

# Add the current directory and parent directory to Python path
current_dir = os.path.dirname(__file__)
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, current_dir)
sys.path.insert(0, parent_dir)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')

django.setup()

app = get_wsgi_application()
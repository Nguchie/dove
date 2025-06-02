import sys
import os

# Add your local packages path
sys.path.insert(0, os.path.expanduser('~/python_packages'))

# Point to your project
sys.path.insert(0, os.path.dirname(__file__))

# Set Django settings module
os.environ['DJANGO_SETTINGS_MODULE'] = 'kitchen.settings'

# Import and serve
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

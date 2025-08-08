import sys
import os

# Add the backend directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from main import app as fastapi_app

# Vercel needs `app` variable here
app = fastapi_app

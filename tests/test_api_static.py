import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def test_style_css_route_exists_in_api():
    """The /style.css route must be registered in api.py."""
    with open(os.path.join(os.path.dirname(__file__), '..', 'src', 'api.py')) as f:
        source = f.read()
    assert '@app.get("/style.css")' in source, "Missing /style.css route in api.py"

def test_style_css_uses_correct_content_type():
    """The route must specify content_type='text/css'."""
    with open(os.path.join(os.path.dirname(__file__), '..', 'src', 'api.py')) as f:
        source = f.read()
    assert 'content_type="text/css"' in source, "Missing content_type='text/css' in style.css route"

def test_style_css_file_exists():
    """The actual CSS file must exist at the expected static path."""
    css_path = os.path.join(os.path.dirname(__file__), '..', 'src', 'static', 'style.css')
    assert os.path.exists(css_path), f"style.css not found at {css_path}"

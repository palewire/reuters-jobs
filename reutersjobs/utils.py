from html.parser import HTMLParser
from io import StringIO


class MLStripper(HTMLParser):
    """Strip HTML."""

    def __init__(self):
        """Create."""
        super().__init__()
        self.reset()
        self.strict = False
        self.convert_charrefs = True
        self.text = StringIO()

    def handle_data(self, d):
        """Handle the provided data."""
        self.text.write(d)

    def get_data(self):
        """Get a value."""
        return self.text.getvalue()


def strip_tags(html):
    """Strip HTML from the provided string."""
    s = MLStripper()
    s.feed(html)
    return s.get_data()

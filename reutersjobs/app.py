from bs4 import BeautifulSoup
from dateutil.parser import parse as dateparse
from flask import Flask, render_template, request
from markdown import markdown

from . import utils

app = Flask(__name__)


@app.route("/")
def job_list():
    """List all of the jobs in the latest clean file."""
    return render_template("job_list.html", obj_list=utils.get_latest_list())


@app.route("/job/")
def job_detail():
    """Serve a detail page that we'll save as an image."""
    id_ = request.args.get("id")
    obj_list = utils.get_latest_list()
    obj = next(o for o in obj_list if o["id"] == id_)
    obj["html"] = _prep_html(obj["description"])
    obj["open_date"] = dateparse(obj["open_date"])
    return render_template("job_detail.html", obj=obj)


def _prep_html(s):
    html = markdown(s)
    soup = BeautifulSoup(html, "html5lib")
    for each in soup.findChildren():
        if _cut(each.text):
            each.clear()
    return str(soup)


def _cut(s):
    s = s.lower().strip()
    if s in ["accessibility"]:
        return True
    starts_list = [
        "as a global business, we rely on diversity of culture",
        "We also make reasonable accommodations",
        "Protect yourself from fraudulent job postings",
        "More information about Thomson Reuters can be found",
        "We are powered by the talents of",
        "Do you want to be part of a team helping re-invent the way knowledge professionals work?",
    ]
    for t in starts_list:
        if s.startswith(t.lower()):
            return True
    return False


if __name__ == "__main__":
    app.run(debug=True)

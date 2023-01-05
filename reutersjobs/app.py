from flask import Flask, render_template, request
from markupsafe import escape

from . import utils

app = Flask(__name__)


@app.route("/")
def job_list():
    """List all of the jobs in the latest clean file."""
    return render_template("job_list.html", obj_list=utils.get_latest_list())


@app.route("/jobs/")
def job_detail():
    """Serve a detail page that we'll save as an image."""
    name = request.args.get("name", "World")
    return f"Hello, {escape(name)}!"


if __name__ == "__main__":
    app.run(debug=True)

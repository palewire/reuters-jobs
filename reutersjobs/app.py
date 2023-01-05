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
    obj["html"] = markdown(obj["description"])
    return render_template("job_detail.html", obj=obj)


if __name__ == "__main__":
    app.run(debug=True)

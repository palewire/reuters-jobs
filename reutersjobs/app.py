from flask import Flask, request
from flask import render_template
from markupsafe import escape

from . import utils

app = Flask(__name__)


@app.route('/')
def job_list():
    return render_template('job_list.html', obj_list=utils.get_latest_list())


@app.route("/jobs/")
def job_detail():
    name = request.args.get("name", "World")
    return f'Hello, {escape(name)}!'


if __name__ == "__main__":
    app.run(debug=True)
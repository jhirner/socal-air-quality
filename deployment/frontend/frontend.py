# A Flask-based web frontend for boiling point predictions.

# Import the necessary modules and instantiate the app
from flask import Flask, render_template
import dataset
import json
from datetime import datetime

app = Flask(__name__)


# Load user-defined variables.
with open('../config.json', "r") as f:
    config = json.load(f)

# Prepare to query database for up-to-date air quality data.
query = """SELECT DateTime, O3, T, WS, WD
            FROM aq
            ORDER BY DateTime DESC
            LIMIT 1"""

# Define routes
@app.route("/")
def display_forecast():

    # Query db for latest air quality data
    with dataset.connect("sqlite:///" + config["db_path"]) as db:
        aq_dict = list(db.query(query))[0]
        dt_updated = datetime.strptime(aq_dict["DateTime"].split(".")[0], "%Y-%m-%d %H:%M:%S")

    display = render_template("forecast.html",
        current_time = dt_updated.strftime("%d %b %Y, %I:00 %p"),
        current_temp = validate_nums(aq_dict["T"]),
        current_O3 = validate_nums(aq_dict["O3"]),
        current_windspeed = validate_nums(aq_dict["WS"]),
        current_winddir = validate_nums(aq_dict["WD"]),
        )
    return display

@app.route("/<unspecified_str>")
def handle_unknown(unspecified_str):
    message = """Sorry, but there is nothing at that path."""

    display = render_template("error.html", error_msg = message)
    return display

@app.route("/about")
def about_model():
    display = render_template("learn_more.html")
    return display

# For live  updates of weather & air quality data at /,
# ensure that numeric data is correctly read from the database.
def validate_nums(numeric_string):
    if numeric_string:
        try:
            return int(numeric_string)
        except TypeError:
            return ("unknown")
    else:
        return "Not retrievable from SQAQMD."

# Run the app
if __name__ == "__main__":
    app.run(debug = False)

# Run the app if called indirectly (i.e.: via gunicorn)
if __name__ != '__main__':
    gunicorn_logger = logging.getLogger('gunicorn.error')
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)

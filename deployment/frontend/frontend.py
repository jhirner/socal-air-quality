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
        current_temp = int(aq_dict["T"]),
        current_O3 = int(aq_dict["O3"]),
        current_windspeed = int(aq_dict["WS"]),
        current_winddir = int(aq_dict["WD"]),
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

# Run the app
if __name__ == "__main__":
    app.run(debug = False)

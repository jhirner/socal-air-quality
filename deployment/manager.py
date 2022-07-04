from aq_updater import AQUpdater
from aq_predictor import AQPredictor
import numpy as np
import pandas as pd

if __name__ == "__main__":
    # Instantiate the AQUpdater and AQPredictor classes.
    updater = AQUpdater("config.json")
    predictor = AQPredictor("config.json")

    # Print status updates to a log
    print("=====> Initializing at ", predictor.now.strftime("%d. %B %Y %H:%M"))

    # Scrape the newest air quality data via updater, then generate a new
    # new air quality forecast. Save & plot the predictions.
    updater.update()
    print("     Updated database.")
    predictor.predict()
    print("     Generated forecast.")
    predictor.write_db()
    predictor.plot_forecast()
    print("     Wrote forecast.")

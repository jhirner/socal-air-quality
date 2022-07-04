# Import required modules
import json
import pandas as pd
from sqlalchemy import create_engine
import dataset
from dill import load
from tensorflow.keras.models import load_model
import numpy as np
import datetime
from matplotlib import dates as mpdates

class AQPredictor:
    def __init__(self, config_path):

        # Load user-defined variables.
        with open(config_path, "r") as f:
            self.config = json.load(f)

        # Load the data preprocessor & the trained model.
        with open(self.config["preprocessor_path"], "rb") as f:
            self.preprocessor = load(f)
        self.model = load_model(self.config["model_path"])

        # Load the data & prepare it for prediction.
        self.load_db()

    def load_db(self):
        """Read the past 48 hours of air quality data into df, which
        is ordered in chronological order."""
        db_engine = create_engine("sqlite:///" + self.config["db_path"])
        with db_engine.connect() as con:
            query = """SELECT DateTime, O3, T, WS, WD
                     FROM aq
                     ORDER BY DateTime DESC
                     LIMIT 48"""
            self.df = pd.read_sql(query, con)[::-1]

        # Convert the date/time data from string to datetime-type.
        # Extract the latest date/time entry as "now".
        self.df["DateTime"] = pd.to_datetime(self.df["DateTime"])
        self.now = self.df[-1:]["DateTime"].values.astype('datetime64[s]').tolist()[0]


    def preprocess_data(self):
        """Serves two primary purposes:
           1) Slice the input df to the most recent 24 hours
           2) Transform & scale the data."""

        # Ensure the data are continous and hourly. If not, fill data forward.
        self.df.drop_duplicates(subset = "DateTime", inplace = True)
        self.df = self.df.set_index("DateTime").resample("1H").ffill().reset_index()

        # First, slice the df to the most recent 25 hours, dropping predicted values.
        # Ensure any missing values are imputed.
        df_subset = self.df[["DateTime", "O3", "T", "WS", "WD"]][-25:]
        df_subset = df_subset.fillna(method = "ffill").fillna(method = "bfill")

        # Next, Scale & transform using the already-fitted preprocessing pipeline.
        transformed = self.preprocessor.transform(df_subset)
        transformed = transformed.reset_index(drop = True)

        # Features must be forced to numpy array with float32 type.
        # Required because the data tends to be converted to strings otherwise.
        x = transformed.drop(columns = ["O3-untrans", "DateTime"],
                             inplace = False)
        x = np.asarray(x).astype("float32").reshape(-1, 25, 4)

        # Return the datetime, y, and reverse-order x data (in that order).
        return (transformed.loc[0, "DateTime"],
                transformed.loc[0, "O3-untrans"],
                x)


    def predict(self):
        """Generate an hourly forecast extending 24 hours into the future,
        an array with shape (1, 24)"""
        dt, y, x = self.preprocess_data()
        self.pred = self.model.predict(x,
                                       verbose = 0)
        return


    def write_db(self):
        """Write the complete forecast to the database, including the time
        the forecast was made."""

        self.forecast = {"DateTime" : self.now}
        for hour in range(0, self.pred.shape[1]):
            self.forecast["t+" + str(hour + 1) + "h"] = float(self.pred[0, hour])
            # The predicted value must be cast as float, as writing its
            # original type (numpy.float32) results in failure.

        with dataset.connect("sqlite:///" + self.config["db_path"]) as db:
            db["predictions"].insert(self.forecast)

        return


    def plot_forecast(self):

        # First, append the predictions to the df.
        pred_df = pd.DataFrame(self.pred.reshape(24,1))
        pred_df.columns = ["PredO3"]

        # Merge the predicted values to the dataframe containing measured values. Reindex to fill-forward the datetime stamp.
        self.df = self.df.set_index("DateTime")
        self.df = pd.concat([self.df, pred_df], axis = "rows")
        self.df.index = pd.date_range(self.df.index[0],
                                            periods = len(self.df),
                                            freq = "1H")



        fig = self.df.plot(y = ["O3", "PredO3"],
                           kind = "line",
                           title = "Surface-Level Ozone in Downtown Los Angeles",
                           xlabel = "Date / Time",
                           ylabel = "Surface-Level Ozone, ppb",
                           label = ["Historical Data", "Forecast"],
                           figsize = (8, 3))
        fig.get_figure().savefig(self.config["plot_path"], bbox_inches = "tight", pad_inches = 0.5)

        return


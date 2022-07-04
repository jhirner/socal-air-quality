# Import required modules
import json
import requests
from io import StringIO
from csv import DictReader
from datetime import datetime
import dataset

class AQUpdater:

    def __init__(self, config_path):
        # Load user-defined variables
        with open(config_path, "r") as f:
            self.config = json.load(f)
        return

    def query(self):
        # Assemble query & fetch data
        try:
            response = requests.post(self.config["query_url"],
                                     params = {"toExcel" : self.config["query_toExcel"],
                                               "keepSiteCode" : self.config["query_keepSiteCode"],
                                               "keepMaxHr" : datetime.now().strftime("%m/%d/%Y")})
        except:
            pass

        if response.status_code == 200:
            reader = DictReader(StringIO(response.text))

            # Store the retrieved air quality data to a dict.
            # Also include the date and time (to the nearest hour).
            self.aq = {}
            self.aq["DateTime"] = datetime.now().replace(minute = 0,
                                                         second = 0,
                                                         microsecond = 0)

            for entry in reader:
                try:
                    self.aq[entry["Abbreviation "].replace(".", "")] = float(entry["Current Value"])
                except ValueError:
                    pass

    def write_db(self):
        with dataset.connect("sqlite:///" +self.config["db_path"]) as db:
            db["aq"].insert(self.aq)

    def update(self):
        self.query()
        self.write_db()
        return

# Scrapes air quality data from the South Coast Air Quality Management
# district website, https://aqmd.gov

# Import required modules
from bs4 import BeautifulSoup
import dataset
from time import sleep
from datetime import datetime, timedelta
import requests
from tqdm import tqdm


class AqiScraper:
    def __init__(self, scraping_start, scraping_end, db_path):

        # Available options for scraping
        self.station_opts = {
            "70087": "Central Los Angeles",
            "30176": "Anaheim",
            "70060": "Azusa",
            "33164": "Banning",
            "36181": "Central San Bernardino Mountains,",
            "70112": "Compton",
            "36197": "Fontana",
            "70591": "Glendora",
            "33157": "Indio",
            "30177": "Habra",
            "33158": "Lake Elsinore",
            "70111": "LAX Hastings",
            "33033": "Mecca",
            "33165": "Mira Loma",
            "30002": "Mission Viejo",
            "70200": "North Hollywood",
            "33137": "Palm Springs",
            "70088": "Pasadena",
            "33149": "Perris",
            "70185": "Pico Rivera",
            "70075": "Pomona",
            "36204": "Redlands",
            "70074": "Reseda",
            "33144": "Rubidoux Riverside",
            "36203": "San Bernardino",
            "70090": "Santa Clarita",
            "36039": "Signal Hill",
            "33031": "Temecula",
            "36175": "Upland",
            "70091": "West Los Angeles"""
        }

        self.aq_metric_opts = {
            "036": "Ozone",
            "065": "PM2.5",
            "064": "PM10",
            "038": "NO2",
            "015": "CO",
            "024": "SO2",
            "074": "Temperature",
            "086": "Wind Direction",
            "084": "Wind Speed",
        }

        # Convert the user-defined query range strings into struct_time
        try:
            self.scr_start_date = datetime.strptime(scraping_start, "%m/%d/%Y")
            self.scr_end_date = datetime.strptime(scraping_end, "%m/%d/%Y")
        except ValueError:
            print("Input dates could not be interpreted. The format MM/DD/YYYY is required.")

        # Scraped data will be stored to a SQLite database at the user-specified path.
        self.db_path = db_path

        return

    def calc_query_end(self, start):
        # Calculate the end date for an individual web query.
        # This is necessary because the AQMD website only returns up to
        # 183 days of data per query. Longer queries are rejected.

        if start + timedelta(days=183) < self.scr_end_date:
            end = start + timedelta(days=183)
        else:
            end = self.scr_end_date

        return end

    def calc_query_start(self, end):
        # Calculate the start date for an individual web query
        # by adding 1 day to the prior query's end date.

        return end + timedelta(days=1)

    def access_webdata(self,
                       query_start_struct=None,
                       query_end_struct=None,
                       station_code=None,
                       aq_param_code=None):
        # Construct & execute a query for the AQMD website. Return it as HTML.
        query_payload = {"AQIVar": aq_param_code,
                         "stationDropDownList": station_code,
                         "fdate": datetime.strftime(query_start_struct, "%m/%d/%Y"),
                         "tdate": datetime.strftime(query_end_struct, "%m/%d/%Y"),
                         "searchVariButn": "",  # requests fail if this variable is omitted
                         }

        # An offline complete copy of SCAQMD's SSL certificate is included via
        # _verify_ because the requests module does not support externally
        # downloaded certificates.
        html_results = requests.post("https://xappp.aqmd.gov/aqdetail/AirQuality/HistoricalData",
                                     data=query_payload,
                                     verify="scaqmd-fullchain.pem").text

        return html_results

    def parse_webdata(self, html_results):
        # Parse HTML from the AQMD website. Add values to the collected_data
        # list, which will become a list of dicts. Each dict is one scrape data row.
        collected_data = []
        soup = BeautifulSoup(html_results, "html.parser")

        # First scrape the station name & the air quality metric for these results.
        station_metric = soup.find_all(class_="pb20")
        for tag in station_metric:
            if len(tag.find_all(class_="text-blue")) != 0:
                name_of_station = tag.find(class_="text-blue").get_text()
                air_quality_param = tag.find(class_="text-blue").find_next().get_text()

        # Now scrape the tabulated data to the list of tuples.
        try:
            data_table_list = soup.find(id="gridtable").find_all(class_="listrow")
            for data_row in data_table_list:
                collected_data.append(dict(
                    StationName=name_of_station,
                    DateTime=data_row.find_all(class_="mtext")[0].get_text().strip(),       # date & time of measurement
                    Metric=air_quality_param,                                               # metric of interest
                    MeasuredValue=data_row.find_all(class_="mtext")[1].get_text().strip(),  # measured value
                    MeasuredUnits=data_row.find_all(class_="mtext")[3].get_text().strip(),  # units for measurement
                    MeasuredPeriod=data_row.find_all(class_="mtext")[2].get_text().strip(), # averaging period for measurement
                ))

            return collected_data

        except AttributeError:
            # AttibuteError is raised when BeautufulSoup fails to find either
            # of the tags listed in find() or find_all functions.
            return []



    def update_database(self, data_rows):
        # Write the air quality data to a SQLite database.

        try:
            with dataset.connect("sqlite:///" + self.db_path) as db:
                db["scaqmd-data"].insert_many(data_rows)
        except RuntimeWarning:
            # A RuntimeWarning is raised if the db schema is altered inside the loop.
            # Which, of course, it is altered when the new scaqmd-data table is created.
            pass

        return

    def scrape(self, stations_list):
        # Scrape the data by iterating over all stations and air quality metrics.
        for station in tqdm(stations_list):
            for metric in tqdm(self.aq_metric_opts.keys()):

                # Begin the first query at the user-specified start date
                query_start = self.scr_start_date

                while query_start <= self.scr_end_date:

                    # Calculate the end date for this query
                    query_end = self.calc_query_end(query_start)

                    # print("Searching station {} for {} through {}.".format(station, metric, query_end), end="\r")

                    html = self.access_webdata(query_start_struct=query_start,
                                               query_end_struct=query_end,
                                               station_code=station,
                                               aq_param_code=metric)
                    new_data = self.parse_webdata(html)
                    self.update_database(new_data)

                    # Calculate a new query start date for the next iteration
                    query_start = self.calc_query_start(query_end)

                    # Pause 1 second to avoid triggering server-side throttling.
                    sleep(1)


if __name__ == '__main__':
    # Ask for user's scraping parameters.
    scraping_start_str = input("Start date for data scraping? (MM/DD/YYYY): ")
    scraping_end_str = input("End date for data scraping? (MM/DD/YYYY): ")
    db_path = input("Relative path to database? ")
    scraper = AqiScraper(scraping_start_str, scraping_end_str, db_path)

    print("Available air monitoring stations are: ")
    for station_code in scraper.station_opts.keys():
        print(station_code, scraper.station_opts[station_code])

    stations_str = input("Station codes to scrape? (List, separated by spaces): ")
    stations = stations_str.split()
    scraper.scrape(stations)

    print("All done.")

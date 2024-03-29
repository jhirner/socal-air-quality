# socal-air-quality
A machine learning project to predict ozone pollution in central Los Angeles.

## Contents
From a high level, this repository includes:
* **Historical air quality and weather data for central Los Angeles.** Data were scraped from the [South Coast Air Quality Management District](http://www.aqmd.gov/) page for a monitoring station in [Central Los Angeles](http://www.aqmd.gov/docs/default-source/clean-air-plans/air-quality-monitoring-network-plan/aaqmnp-losangeles.pdf). The monitoring station is located at [1630 North Main Street
Los Angeles, CA 90012](https://duckduckgo.com/?q=1630+North+Main+Street+Los+Angeles%2C+CA+90012&t=h_&ia=web&iaxm=maps). The raw data set is `la_aq.csv`. The Python script used in scraping this dataset (`data_scraping.py`) is also included.
* **A series of Jupyter notebooks** studying the ozone pollution within the larger data set. The notebooks include exploratory analysis, data preprocessing, and training of a long short-term memory (LSTM) neural network for generating a 24-hour ozone pollution forecast.
* **A deployed forecast web app.** The Flask-based app resides within the `deployment` directory and is deployed at [aq.withjosh.net](https://aq.withjosh.net).

## Requirements
No installation is required to browse the analysis show in the Jupyter notebooks or to use the web app.

Reproducing & extending the analysis requires the following Python 3 libraries or compatible versions:
* dill 0.3
* numpy 1.22
* pandas 1.4
* scikeras 0.4
* scikit-learn 1.1
* tensorflow 2.8

## How is the raw data  structured?
The raw data set (`la_aq.csv`) includes *185912* rows, with each row representing one hour between 1 January 2000 and 31 December 2021. Although some individual timepoints are missing select measurements, included features are:
* CO: carbon monoxide, in ppm (parts per million)
* NO2: nitrogen dioxide, in ppb (parts per billion)
* O3: ozone, in ppb (parts per billion)
* PM10: <10-micron particulate matter, in µg/m<sup>3</sup>
* PM2.5: <2.5-micron particulate matter, in µg/m<sup>3</sup>
* SO2: sulfur dioxide, in ppb (parts per billion),
* T: air temperature, in degrees Fahrenheit
* WD: wind direction, in [degrees](http://snowfence.umn.edu/Components/winddirectionanddegrees.htm)
* WS: wind speed, in mph (miles per hour), average hourly

## Sources & License
These data were recorded by [South Coast Air Quality Management District](http://www.aqmd.gov/) and made public via their [web interface](https://xappp.aqmd.gov/aqdetail/). Data were aggregated and tabulated by this author's repository.

You are welcome to use this data for any and all purposes. Please cite both the SCAQMD and this repository.

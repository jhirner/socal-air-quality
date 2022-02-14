# socal-air-quality
Air quality data from Southern California monitoring stations

## What is included?
This repository features historical air quality data for Southern California and associated weather data. The data set currently features data from only a single [South Coast Air Quality Management District(http://www.aqmd.gov/) monitoring station in [Central Los Angeles](http://www.aqmd.gov/docs/default-source/clean-air-plans/air-quality-monitoring-network-plan/aaqmnp-losangeles.pdf) located at [1630 North Main Street
Los Angeles, CA 90012](https://duckduckgo.com/?q=1630+North+Main+Street+Los+Angeles%2C+CA+90012&t=h_&ia=web&iaxm=maps). The data set is **la_aq.csv**.

## How is the data structured?
The set includes *185912* rows, with each row representing one hour between 1 January 2000 and 31 December 2021. Although some individual timepoints are missing select measurements, included features are:
* CO: carbon monoxide, in ppm (parts per million)
* NO2: nitrogen dioxide, in ppb (parts per billion)
* O3: ozone, in ppb (parts per billion)
* PM10: <10-micron particulate matter, in µg/m^3^
* PM2.5: <2.5-micron particulate matter, in µg/m^3^
* SO2: sulfur dioxide, in ppb (parts per billion),
* T: air temperature, in degrees Fahrenheit
* WD: wind direction, in [degrees](http://snowfence.umn.edu/Components/winddirectionanddegrees.htm)
* WS: wind speed, in mph (miles per hour), average hourly

## Sources & License
These data were recorded by [South Coast Air Quality Management District(http://www.aqmd.gov/) and made public via their [web interface](https://xappp.aqmd.gov/aqdetail/). Data were aggregated and tabulated by this author's repository.

You are welcome to use this data for any and all purposes. Please cite both the SCAQMD and this repository.

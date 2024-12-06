# Project: Satellite-Based Air Quality Forecasting in Thailand

## Problem Statement:
Leveraging Satellite-Based Data for Daily Air Quality Forecasting in Major Thai Cities

## Excusive Summary:
This project aims to develop a robust and accurate air quality forecasting model for major cities in Thailand. By harnessing the power of satellite-derived data from 2024 data, we seek to improve the accuracy of air quality predictions. This will enable authorities and individuals to make informed decisions and take proactive measures to mitigate the adverse impacts of air pollution.

## Project Goal:
To develop a robust and accurate air quality forecasting model leveraging satellite-derived hotspot data, meteorological parameters, and ground-level air quality measurements.

## Data Requirements:

### Satellite Fire Hotspot Data:
* MODIS (Moderate Resolution Imaging Spectroradiometer)
* VIIRS (Visible Infrared Imaging Radiometer Suite)

    Source: [The Fire Information for Resource Management System (FIRMS)](https://firms.modaps.eosdis.nasa.gov/)

### Meteorological Data:
* Temperature
* Wind speed, and direction
* Atmospheric pressure

    Source: [Open-Meteo](https://open-meteo.com/)
----

* Ground-Level Air Quality Measurements
    * PM2.5 concentrations from air quality monitoring stations

    Source: [The World Air Quality Index Project](https://aqicn.org/historical/#thailand!city:bangkok)
----

### Methodology:
#### Data Preprocessing and Cleaning:
* Handle missing values and outliers
* Convert data to a consistent format and time zone
* Perform spatial and temporal interpolation for missing data

#### Feature Engineering:
* Extract relevant features from satellite hotspot data
  * Hotspot intensity
  * Frequency
  * Spatial distribution

#### Model Development and Training:
* Train and compare Gradient Boosting (XGBoost) model and Long Short-Term Memory (LSTM) Neural Network model.
* Train models on historical data to predict future air quality levels

#### Model Evaluation:
* Assess model performance using metrics is Root Mean Square Error (RMSE)
* Conduct cross-validation to ensure model generalizability

#### Forecasting and Visualization:
* Generate short-term and long-term air quality forecasts
* Visualize forecasts using maps, time series plots, and other appropriate techniques

### Expected Outcomes:
* A reliable and accurate air quality forecasting model that can predict future air quality levels
* Improved understanding of the impact of satellite-derived hotspot data on air quality
* Development of early warning systems to alert authorities and the public about potential air pollution

### Target Audience
* Government Agency
* Media Outlet

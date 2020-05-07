import datetime as dt
import numpy as np
import pandas as pd
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify

engine = create_engine("sqlite:///hawaii.sqlite")

# reflect an existing database

NewBase = automap_base()
NewBase.prepare(engine, reflect=True)

# Save references to each table

Measurement = NewBase.classes.measurement
Station = NewBase.classes.station

# Create our session (link) from Python to the DB

oursession = Session(engine)
app = Flask(__name__)

@app.route("/")

def aloha():

    return (

        f"Aloha to the Hawaii Climate Analysis<br/>"

        f"Available Routes<br/>"

        f"/api/v1.0/precipitation<br/>"

        f"/api/v1.0/stations<br/>"

        f"/api/v1.0/tobs<br/>"

        f"/api/v1.0/temp/start/end"

    )

@app.route("/api/v1.0/precipitation")

def precipitation():

    # Calculate the date 1 year ago from last date in database

    cubsworldseries = dt.date(2016, 8, 31) - dt.timedelta(days=365)

    # Query for the date and precipitation for the last year

    precipitation = oursession.query(Measurement.date, Measurement.prcp)

    filter(Measurement.date >= cubsworldseries)

    # Dict with date as the key and prcp as the value

    sortprecip = {date: prcp for date, prcp in precipitation}

    return jsonify(sortprecip)


@app.route("/api/v1.0/stations")

def stations():

    results = oursession.query(Station.station).all()

    # Unravel results into a 1D array and convert to a list

    stations = list(np.ravel(results))

    return jsonify(stations)


@app.route("/api/v1.0/tobs")

def temp_monthly():

    cubsworldseries = dt.date(2016, 8, 31) - dt.timedelta(days=365)
    results = oursession.query(Measurement.tobs).\
        filter(Measurement.station == 'USC00519281').\
        filter(Measurement.date >= cubsworldseries).all()

    # Unravel results into a 1D array and convert to a list

    temps = list(np.ravel(results))

    # Return the results

    return jsonify(temps)

@app.route("/api/v1.0/temp/<start>")

@app.route("/api/v1.0/temp/<start>/<end>")

def stats(start=None, end=None):

    # Select statement & calculate TMIN, TAVG, TMAX for dates greater than start

    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]

    if not end:

        results = oursession.query(*sel)

        filter(Measurement.date >= start)

        temps = list(np.ravel(results))

        return jsonify(temps)


    results = oursession.query(*sel)

    filter(Measurement.date >= start)

    filter(Measurement.date <= end)

    temps = list(np.ravel(results))

    return jsonify(temps)


if __name__ == '__main__':

    app.run()
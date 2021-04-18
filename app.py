#####imports#####
import numpy as np
import pandas as pd
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect
################


#####flask setup#####
from flask import Flask, jsonify
app = Flask(__name__)
####################



#####sqlalchemy setup#####
engine = create_engine("sqlite:///hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect = True)
inspector = inspect(engine)

measurement = Base.classes.measurement
Station = Base.classes.station

session = Session(engine)
#########################




@app.route("/")
def home():
    print("server received request for 'home' page.")
    return(
        "Available routes are:<br/>"
        "/api/v1.0/precipitation<br/>"
        "/api/v1.0/stations<br/>"
        "/api/v1.0/tobs<br/>"
        "/api/v1.0/&lt;start&gt;  returns results from &lt;start&gt to most recent<br/>"
        "/api/v1.0/&lt;start&gt;/&lt;end&gt;  &lt;start&gt; being oldest,  &lt;end&gt; being most recent"
    )
    

@app.route("/api/v1.0/precipitation")
def precipitation():
    print("Server received reqeust for 'precipitation' page")

    session = Session(engine)

    results = session.query(measurement.date, measurement.prcp).all()


    session.close()

    values_dict = dict()
    for date, prcp in results:
        values_dict.setdefault(date, prcp)

    return jsonify(values_dict)

@app.route("/api/v1.0/stations")
def stations():
    print("Server received request for 'stations' page")

    session = Session(engine)

    results = session.query(Station.station, Station.name).all()

    session.close()

    values_dict = dict()
    for station, name in results:
        values_dict.setdefault(station, name)

    return jsonify(values_dict)

@app.route("/api/v1.0/tobs")
def tobs():
    print("Server received request for 'tobs' page")

    session = Session(engine)

    most_active_station = session.query(measurement.station, Station.name, func.count(measurement.id)).\
        filter(measurement.station == Station.station).\
        group_by(measurement.station).\
        order_by(func.count(measurement.id).desc()).first()[0]

    results = session.query(measurement.date, measurement.tobs).\
        filter(measurement.station == most_active_station).\
        filter(measurement.date >= '2016-08-23').\
        order_by(measurement.date.desc()).all()

    session.close()

    values_dict = dict()
    for date, temp in results:
        values_dict.setdefault(date, temp)

    return jsonify(values_dict)

@app.route("/api/v1.0/<start>")
def info_from_start(start):
    session = Session(engine)

    start_date = start

    results = session.query(func.min(measurement.tobs), func.max(measurement.tobs), func.avg(measurement.tobs)).\
        filter(measurement.date >= start_date).first()
    
    session.close()

    values_dict = {
        "Start date":start_date,
        "Max temp":results[1],
        "Min temp":results[0],
        "Avg temp":results[2]
    }

    return jsonify(values_dict)


@app.route("/api/v1.0/<start>/<end>")
def start_end_temp(start, end):

    session = Session(engine)

    start_date = start
    end_date = end

    results = session.query(func.min(measurement.tobs), func.max(measurement.tobs), func.avg(measurement.tobs)).\
        filter(measurement.date >= start_date).\
        filter(measurement.date <= end_date).first()
    
    session.close()

    values_dict = {
        "Start date":start_date,
        "End date":end_date,
        "Max temp":results[1],
        "Min temp":results[0],
        "Avg temp":results[2]
    }

    return jsonify(values_dict)


if __name__ == "__main__":
    app.run(debug = True)

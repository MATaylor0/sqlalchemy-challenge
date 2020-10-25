# Importing dependencies
import numpy as np
import sqlalchemy
import datetime as dt

from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify

engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Setting the max date and query date
max_date = dt.date(2017, 4, 8)
query_date = max_date - dt.timedelta(days = 365.24)

# Flask setup
app = Flask(__name__)

# Flask routes
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start_date<br/>"
        f"/api/v1.0/start_date/end_date"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)

    results = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date > query_date).\
        order_by(Measurement.date).all()

    session.close()

    return jsonify(dict(results))

@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)

    results = session.query(Station.station).\
    group_by(Station.station).all()

    session.close()

    all_stations = list(np.ravel(results))

    return jsonify(all_stations)

@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)

    results = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.date > query_date).\
        filter(Measurement.station == "USC00519281").\
        order_by(Measurement.date).all()

    session.close()

    return jsonify(dict(results))

@app.route("/api/v1.0/<start_date>")
def start(start_date):
    session = Session(engine)

    try:
        startdate = dt.datetime.strptime(start_date, "%d-%m-%Y").date()
        sel = [func.min(Measurement.tobs),
            func.max(Measurement.tobs),
            func.avg(Measurement.tobs)]
        
        results = session.query(*sel).\
            filter(Measurement.date >= startdate).all()
    except:
        session.close()
        return "Invalid start date entered", 404

    session.close()

    return jsonify(results)

@app.route("/api/v1.0/<start_date>/<end_date>")
def start_end(start_date, end_date):
    session = Session(engine)

    try:
        startdate = dt.datetime.strptime(start_date, "%d-%m-%Y").date()
        enddate = dt.datetime.strptime(end_date, "%d-%m-%Y").date()
        sel = [func.min(Measurement.tobs),
            func.max(Measurement.tobs),
            func.avg(Measurement.tobs)]
        
        results = session.query(*sel).\
            filter(Measurement.date >= startdate).\
            filter(Measurement.date <= enddate).all()
    except:
        session.close()
        return "Invalid start or end date entered", 404

    session.close()

    return jsonify(results)


if __name__ == "__main__":
    app.run(debug=True)
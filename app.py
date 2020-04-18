import numpy as np
import sqlalchemy
import datetime as dt
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify

# Database Setup
engine = create_engine("sqlite:///hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
measurement= Base.classes.measurement
station=Base.classes.station

# Create our session (link) from Python to the DB
session=Session(engine)

# Flask Setup
app = Flask(__name__)

# Define what to do when a user hits the index route
@app.route("/")
def welcome():
   return (
        # print out all available routes and information about each route
        f"Available Routes:<br/>"
        f"<br>"
        f"/api/v1.0/precipitation<br/>"
        f"- List of precipitation information from previous year of all stations<br/>"
        f"<br>"
        f"/api/v1.0/stations<br/>"
        f"- List of Information of all stations<br/>"
        f"<br>"
        f"/api/v1.0/tobs<br/>"
        f"- List of temperature information from previous year of the most active station<br/>"
        f"<br>"
        f"/api/v1.0/start<br/>"
        f"- Temperature information from start date of all stations <br/>"
        f"- Enter date information as Y-M-D<br/>"
        f"<br>"
        f"/api/v1.0/start/end<br/>"
        f"- Temperature information from start date to end date of all stations<br/>"
        f"- Enter date information as Y-M-D<br/>"
    )

# Define what to do when a user hits the /api/v1.0/precipitation route
@app.route("/api/v1.0/precipitation")
def precipitation():
    #calculate of date one year before the last day 
    lastyear=dt.date(2017,8,23)-dt.timedelta(days=365)

    #query the date and precipitation information in the previous year
    scores=session.query(measurement.date,measurement.prcp).filter(measurement.date>=lastyear).all()
    
    #store information in a list 
    rain=[]
    for score in scores:
        rain_dict = {}
        rain_dict["Date"] = score[0]
        rain_dict["Prcp"] = score[1]
        rain.append(rain_dict)
   
    return jsonify(rain)

# Define what to do when a user hits the /api/v1.0/stations route
@app.route("/api/v1.0/stations")
def Station():
    #get station information
    stations=session.query(measurement.station,station.name,station.latitude,station.longitude,station.elevation).\
        filter(measurement.station==station.station).group_by(measurement.station).all()
    return jsonify(stations)

# Define what to do when a user hits the /api/v1.0/tobs route
@app.route("/api/v1.0/tobs")
def tobs():
    #calculate of date one year before the last day 
    lastyear=dt.date(2017,8,23)-dt.timedelta(days=365)

    #find the most active station
    station_active=session.query(measurement.station,func.count(measurement.tobs)).group_by(measurement.station).order_by(func.count(measurement.tobs).desc()).all()
    
    #get temperature information from previous year
    temp=session.query(measurement.date,measurement.tobs).filter(measurement.station==station_active[0][0]).filter(measurement.date>=lastyear).all()
    
    #store information in a list
    tep=[]
    for t in temp:
        row2 = {}
        row2["Date"] = t[0]
        row2["Temp"] = t[1]
        tep.append(row2)
    
    return jsonify(tep)

# Define what to do when a user hits the /api/v1.0/<start> route
@app.route("/api/v1.0/<start>")
def date(start):  
    #find information of min, avg and max temp after the start date
    temp_data = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).\
        filter(measurement.date >= start).all()        
        
    return jsonify(temp_data)    

# Define what to do when a user hits the /api/v1.0/<start>/<end> route
@app.route("/api/v1.0/<start>/<end>")
def date2(start,end):  
    #find information of min, avg and max temp within the start and end date   
    temp_data2 = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).\
        filter(measurement.date >= start).filter(measurement.date<=end).all()        
        
    return jsonify(temp_data2) 

#run the app
if __name__ == "__main__":
    app.run(debug=True)




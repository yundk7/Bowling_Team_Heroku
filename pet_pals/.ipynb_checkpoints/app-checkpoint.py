# import necessary libraries
import os
from flask import (
    Flask,
    render_template,
    jsonify,
    request,
    redirect)
import pandas as pd

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Database Setup
#################################################

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', '') or "sqlite:///db.sqlite"
# app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', '')
# db = SQLAlchemy(app)

# from .models import Pet


# create route that renders index.html template
@app.route("/")
def home():
    df = pd.DataFrame()
    df["Title"] = ["Welcome"]
    df["Contents"] = ["Gunbowl member management"]
    return (df.to_html())

@app.route("/initialize")
def initialize():
    df = pd.DataFrame()
    con = create_engine("sqlite:///data.sqlite")
    df.to_sql("members", con, if_exists="replace")
    
    df = pd.DataFrame()
    con = create_engine("sqlite:///data.sqlite")
    df.to_sql("scores", con, if_exists="replace")
    
    df = pd.DataFrame()
    con = create_engine("sqlite:///data.sqlite")
    df.to_sql("attendance", con, if_exists="replace")
    
    df = pd.DataFrame()
    con = create_engine("sqlite:///data.sqlite")
    df.to_sql("inactive", con, if_exists="replace")
    return ("Success")

# Query the database and send the jsonified results
@app.route("/addmember", methods=["GET", "POST"])
def addmember():
    if request.method == "POST":
        doe = request.form["doe"]
        namedob = request.form["namedob"]
        namedob = namedob.replace(" ,",",").replace(", ",",").split(",")
        
        con = create_engine("sqlite:///data.sqlite")
        members = pd.read_sql("members",con)
        inactive = pd.read_sql("inactive",con)
        
        
        names = []
        dobs = []
        does = []
        names_left = []
        dobs_left = []
        does_left = []
        print(len(namedob))
        if doe.lower() == "import":
            for i in range(0,len(namedob),3):
                names.append(namedob[i])
            for i in range(1,len(namedob)+1,3):
                dobs.append(namedob[i])
            for i in range(2,len(namedob)+2,3):
                does.append(namedob[i])
        else:   
            for i in range(0,len(namedob),2):
                names.append(namedob[i])
            for i in range(1,len(namedob)+1,2):
                dobs.append(namedob[i])
                does.append(doe)
            
        df = pd.DataFrame()
        df["name"] = names
        df["DoB"] = dobs
        df["DoE"] = does
        df["DoB"] = pd.to_datetime(df["DoB"])
        df["DoE"] = pd.to_datetime(df["DoE"])
        df.index = df.index+1
        return(df.to_html())
#         return redirect("/", code=302)

    return render_template("form.html")


@app.route("/members")
def pals():
    results = db.session.query(Pet.name, Pet.lat, Pet.lon).all()

    hover_text = [result[0] for result in results]
    lat = [result[1] for result in results]
    lon = [result[2] for result in results]

    pet_data = [{
        "type": "scattergeo",
        "locationmode": "USA-states",
        "lat": lat,
        "lon": lon,
        "text": hover_text,
        "hoverinfo": "text",
        "marker": {
            "size": 50,
            "line": {
                "color": "rgb(8,8,8)",
                "width": 1
            },
        }
    }]

    return jsonify(pet_data)


if __name__ == "__main__":
    app.run()

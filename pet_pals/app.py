import os
from flask import (
    Flask,
    render_template,
    jsonify,
    request,
    redirect)
import pandas as pd
import numpy as np

app = Flask(__name__)


from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
# from sqlalchemy import ARRAY, Integer
@app.route("/")
def home():
    df = pd.DataFrame()
    df["Title"] = ["Welcome"]
    df["Contents"] = ["Gun-Bowl Member Management"]
    return (df.to_html())

@app.route("/formatdb")
def formatdb():
    con = create_engine("postgres://qcumacnfmicopw:c700fed529373aa3b54a62168e0914d2a0d1d5b458aa965d4aea319662c6ed97@ec2-174-129-27-158.compute-1.amazonaws.com:5432/d5koeu8hgsrr65")
    
    df = pd.DataFrame({"name":[],"DoB":[],"DoE":[]})
    df = df.astype({"name":"object"})
    df["DoB"]=pd.to_datetime(df["DoB"])
    df["DoE"]=pd.to_datetime(df["DoE"])
#     con = create_engine("sqlite:///data.sqlite")
    df.to_sql("members", con, if_exists="replace",index=False)
    
    df = pd.DataFrame({"name":[],"date":[],"scores":[]})
    df = df.astype({"name":"object","scores":"object"})
    df["date"]=pd.to_datetime(df["date"])
#     con = create_engine("sqlite:///data.sqlite")
    df.to_sql("scores", con, if_exists="replace",index=False)
    
    df = pd.DataFrame()
#     con = create_engine("sqlite:///data.sqlite")
    df.to_sql("attendance", con, if_exists="replace")
    
    df = pd.DataFrame()
    df = pd.DataFrame({"name":[],"DoB":[],"DoE":[]})
    df = df.astype({"name":"object"})
    df["DoB"]=pd.to_datetime(df["DoB"])
    df["DoE"]=pd.to_datetime(df["DoE"])
#     con = create_engine("sqlite:///data.sqlite")
    df.to_sql("inactive", con, if_exists="replace",index=False)
    return ("Success")

@app.route("/addmember", methods=["GET", "POST"])
def addmember():
    if request.method == "POST":
        doe = request.form["doe"].replace(" ","")
        namedob = request.form["namedob"].replace(" ","")
        
        if namedob[-1] == ",":
            namedob = namedob[:-1]
            
        namedob = namedob.replace(" ,",",").replace(", ",",").split(",")

        names = []
        dobs = []
        does = []
        names_left = []
        dobs_left = []
        does_left = []
        
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
        
#         con = create_engine("sqlite:///data.sqlite")
        con = create_engine("postgres://qcumacnfmicopw:c700fed529373aa3b54a62168e0914d2a0d1d5b458aa965d4aea319662c6ed97@ec2-174-129-27-158.compute-1.amazonaws.com:5432/d5koeu8hgsrr65")
        members = pd.read_sql("members",con)
        inactive = pd.read_sql("inactive",con)
        left_df= pd.DataFrame()
        
        for i in df["name"]:
            if i in list(members["name"]):
                left = pd.DataFrame({"name":[i],"DoB":"in MEMBERS already"})
                left.index = ["FAIL"]
                left_df = left_df.append(left)
            if i in list(inactive["name"]):
                left = pd.DataFrame({"name":[i],"DoB":"in INACTIVE already"})
                left.index = ["FAIL"]
                left_df = left_df.append(left)
        
        if len(left_df)>0:
            return(left_df.to_html())
        
        df = df[~df["name"].isin(list(members["name"]))]
        
        df.to_sql("members", con, if_exists="append",index=False)
        df = df.append(left_df)
        return(df.to_html())
#         return redirect("/", code=302)

    return render_template("addmember.html")


@app.route("/members")
def members():
#     con = create_engine("sqlite:///data.sqlite")
    con = create_engine("postgres://qcumacnfmicopw:c700fed529373aa3b54a62168e0914d2a0d1d5b458aa965d4aea319662c6ed97@ec2-174-129-27-158.compute-1.amazonaws.com:5432/d5koeu8hgsrr65")
    members = pd.read_sql("members",con)
    members.sort_values("name",inplace = True)
    members.reset_index(drop=True,inplace=True)
    members.index=members.index+1
    

    return (members.to_html())

@app.route("/birthday")
def birthday():
#     con = create_engine("sqlite:///data.sqlite")
    con = create_engine("postgres://qcumacnfmicopw:c700fed529373aa3b54a62168e0914d2a0d1d5b458aa965d4aea319662c6ed97@ec2-174-129-27-158.compute-1.amazonaws.com:5432/d5koeu8hgsrr65")
    members = pd.read_sql("members",con)
    members["month"] = pd.DatetimeIndex(members['DoB']).month
    df = members.pivot(values="name",columns="month").apply(lambda x: pd.Series(x.dropna().values))
    

    return (df.to_html())

@app.route("/passed")
def passed():
#     con = create_engine("sqlite:///data.sqlite")
    con = create_engine("postgres://qcumacnfmicopw:c700fed529373aa3b54a62168e0914d2a0d1d5b458aa965d4aea319662c6ed97@ec2-174-129-27-158.compute-1.amazonaws.com:5432/d5koeu8hgsrr65")
    members = pd.read_sql("members",con)
    today = pd.to_datetime("today")
    members["passed"] = today - members["DoE"]
    members = members.sort_values("passed",ascending=False)
    

    return (members.to_html())

@app.route("/inactivate", methods=["GET", "POST"])
def inactivate():
    if request.method == "POST":
#         con = create_engine("sqlite:///data.sqlite")
        con = create_engine("postgres://qcumacnfmicopw:c700fed529373aa3b54a62168e0914d2a0d1d5b458aa965d4aea319662c6ed97@ec2-174-129-27-158.compute-1.amazonaws.com:5432/d5koeu8hgsrr65")
        members = pd.read_sql("members",con)
        inactive = pd.read_sql("inactive",con)
        name = request.form["name"].replace(" ","")
        
        df = members[members["name"]==name]
        if len(df)==0:
            return("not found in MEMBERS")
        df.to_sql("inactive", con, if_exists="append",index=False)
        
        members = members[~members["name"].isin([name])]
        members.to_sql("members", con, if_exists="replace",index=False)
    

        return (f'{[name]} inactivated')
    return render_template("inactivate.html")

@app.route("/reactivate", methods=["GET", "POST"])
def reactivate():
    if request.method == "POST":
#         con = create_engine("sqlite:///data.sqlite")
        con = create_engine("postgres://qcumacnfmicopw:c700fed529373aa3b54a62168e0914d2a0d1d5b458aa965d4aea319662c6ed97@ec2-174-129-27-158.compute-1.amazonaws.com:5432/d5koeu8hgsrr65")
        members = pd.read_sql("members",con)
        inactive = pd.read_sql("inactive",con)
        name = request.form["name"].replace(" ","")
        
        df = inactive[inactive["name"]==name]
        if len(df)==0:
            return("not found in INACTIVE")
        df.to_sql("members", con, if_exists="append",index=False)
        
        inactive = inactive[~inactive["name"].isin([name])]
        inactive.to_sql("inactive", con, if_exists="replace",index=False)
    

        return (f'{[name]} reactivated')
    return render_template("reactivate.html")

@app.route("/inactive")
def inactive():
#     con = create_engine("sqlite:///data.sqlite")
    con = create_engine("postgres://qcumacnfmicopw:c700fed529373aa3b54a62168e0914d2a0d1d5b458aa965d4aea319662c6ed97@ec2-174-129-27-158.compute-1.amazonaws.com:5432/d5koeu8hgsrr65")
    inactive = pd.read_sql("inactive",con)
    inactive.index=inactive.index+1
    

    return (inactive.to_html())


@app.route("/permanent", methods=["GET", "POST"])
def permanent():
    if request.method == "POST":
        name = request.form["name"].replace(" ","")
#         con = create_engine("sqlite:///data.sqlite")
        con = create_engine("postgres://qcumacnfmicopw:c700fed529373aa3b54a62168e0914d2a0d1d5b458aa965d4aea319662c6ed97@ec2-174-129-27-158.compute-1.amazonaws.com:5432/d5koeu8hgsrr65")
        inactive = pd.read_sql("inactive",con)
        scores = pd.read_sql("scores",con)
        scores = scores[~scores["name"].isin([name])]
        inactive = inactive[~inactive["name"].isin([name])]
        scores.to_sql("scores", con, if_exists="replace",index=False)
        inactive.to_sql("inactive", con, if_exists="replace",index=False)
        return(f"{name} removed permanently")
    return render_template("permanent.html")
@app.route("/addscore", methods=["GET", "POST"])
def addscore():
    if request.method == "POST":
        pd.set_option('display.max_colwidth', -1)
        date = request.form["date"]
        scores = request.form["scores"].replace(" ","")
        if scores[-1]==",":
            scores = scores[:-1]
        
        scores = scores.split(",")
        while ("" in scores):
            scores.remove("")
        
        df=pd.DataFrame()
        first = 1
        go = 0
        count = 0
        for i in scores:
            count+=1            
            
            if i.isdigit()==True:
#                 indv_scores.append(int(i))
                indv_scores = indv_scores + str(i) + ","
    
            if i.isdigit()==False and first ==1:
                name = i
#                 indv_scores=[]
                indv_scores=""
                first=0
    
            elif i.isdigit()==False or count == len(scores):
                apnd = pd.DataFrame({"name":[name],"date":[date],"scores":[indv_scores]})
                df = df.append(apnd)
                name = i
#                 indv_scores=[]
                indv_scores = ""
            
        df["date"] = pd.to_datetime(df["date"])
        
#         con = create_engine("sqlite:///data.sqlite")
        con = create_engine("postgres://qcumacnfmicopw:c700fed529373aa3b54a62168e0914d2a0d1d5b458aa965d4aea319662c6ed97@ec2-174-129-27-158.compute-1.amazonaws.com:5432/d5koeu8hgsrr65")
        members = pd.read_sql("members",con)
        notfound = []
        for n in df["name"]:
            if n not in list(members["name"]):
                notfound.append(n)
        if len(notfound)>0:
            return(f'could not find {notfound} in active members')
        
        scores = pd.read_sql("scores",con)
        scores["temp_idx"] = scores["name"] + scores["date"].astype(str)
        
        df["temp_idx"] = df["name"] + df["date"].astype(str)
        
        scores = scores[~scores["temp_idx"].isin(list(df["temp_idx"]))]
        scores.drop(columns=["temp_idx"],inplace=True)
        df.drop(columns=["temp_idx"],inplace=True)
        
        scores.to_sql("scores", con, if_exists="replace",index=False)
        
        df.to_sql("scores", con, if_exists="append",index=False)
        
        return(df.to_html())
    
    return render_template("addscore.html")

@app.route("/scores")
def scores():
    pd.set_option('display.max_colwidth', -1)
#     con = create_engine("sqlite:///data.sqlite")
    con = create_engine("postgres://qcumacnfmicopw:c700fed529373aa3b54a62168e0914d2a0d1d5b458aa965d4aea319662c6ed97@ec2-174-129-27-158.compute-1.amazonaws.com:5432/d5koeu8hgsrr65")
    scores = pd.read_sql("scores",con)
    scores["date"] = scores["date"].astype(str)
    df = scores.pivot(index="name",columns ="date",values="scores").sort_values("name").sort_index(axis=1,ascending=False)
    return(df.to_html())

@app.route("/removescore", methods=["GET", "POST"])
def removescore():
    if request.method == "POST":
        date = request.form["date"]
        names = request.form["names"].lower().replace(" ","")
        
#         con = create_engine("sqlite:///data.sqlite")
        con = create_engine("postgres://qcumacnfmicopw:c700fed529373aa3b54a62168e0914d2a0d1d5b458aa965d4aea319662c6ed97@ec2-174-129-27-158.compute-1.amazonaws.com:5432/d5koeu8hgsrr65")
        scores = pd.read_sql("scores",con)
        
        if names == "all":
            date = pd.to_datetime([date])
            scores = scores[~scores["date"].isin(date)]
            scores.to_sql("scores", con, if_exists="replace",index=False)
            return("done")
        
        names = names.split(",")
        df = pd.DataFrame({"name":names,"date":[date]})
        df["date"] = pd.to_datetime(df["date"])
        
        scores["temp_idx"] = scores["name"] + scores["date"].astype(str)
        
        df["temp_idx"] = df["name"] + df["date"].astype(str)
        
        scores = scores[~scores["temp_idx"].isin(list(df["temp_idx"]))]
        scores.drop(columns=["temp_idx"],inplace=True)
        df.drop(columns=["temp_idx"],inplace=True)
        scores.to_sql("scores", con, if_exists="replace",index=False)
        
        return(df.to_html())
    return render_template("removescore.html")

@app.route("/recentavg", methods=["GET", "POST"])
def recentavg():
    if request.method == "POST":
        pd.set_option('display.max_colwidth', -1)
        num = request.form["num"]
#         con = create_engine("sqlite:///data.sqlite")
        con = create_engine("postgres://qcumacnfmicopw:c700fed529373aa3b54a62168e0914d2a0d1d5b458aa965d4aea319662c6ed97@ec2-174-129-27-158.compute-1.amazonaws.com:5432/d5koeu8hgsrr65")
        inactive = pd.read_sql("inactive",con)
        df = pd.read_sql("scores",con)
        df = df[~df["name"].isin(list(inactive["name"]))]
        
        
        df["date"] = df["date"].astype(str)
        df.sort_values("date",ascending=True,inplace=True)
        # df["scores"] = df.apply(lambda col: df["scores"].str[:-1])

        df = df.groupby("name")["scores"].sum()
        df = pd.DataFrame(df)
        df["scores"] = df.apply(lambda col: df["scores"].str[:-1])
        df["scores"] = df["scores"].str.split(",")

        df = pd.DataFrame(df["scores"].str[::-1].str[:int(num)])
        df["scores"] = df.apply(lambda x: [int(i) for i in x["scores"]],axis=1)
        df["games"] = df.apply(lambda x: len(x["scores"]),axis=1)
        df["avg"] = (df.apply(lambda x: sum(x["scores"]),axis=1)/df["games"]).round(1)
        df["stdev"] = df.apply(lambda x: np.std(x["scores"]),axis=1).round(1)
        df = df[["avg","stdev","games","scores"]].sort_values("avg",ascending=False)
        
        return(df.to_html())
    return render_template("recentavg.html")

if __name__ == "__main__":
    app.run()

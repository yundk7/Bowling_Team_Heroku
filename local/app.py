#gunbowl20
#건볼최고
import os
from flask import (
    Flask,
    render_template,
    jsonify,
    request,
    redirect)
import pandas as pd
pd.set_option('display.max_colwidth', -1)
pd.option_context('display.float_format', '{:0.2f}'.format)
import numpy as np
from statistics import mean,stdev
import random
import datetime
from datetime import timedelta
app = Flask(__name__)


from flask_sqlalchemy import *#SQLAlchemy
from sqlalchemy import create_engine
# from sqlalchemy import ARRAY, Integer
@app.route("/")
def home():
    pd.set_option('display.max_colwidth', -1)
    df = pd.DataFrame()
    df["Title"] = ["Welcome",
                  "/members",
                   "/scores",
                  "/birthday",
                  "/passed",
                  "/inactive",
                  "/recent",
                  "/random"]
    df["Title"]=df["Title"].apply(lambda x: '<a href="{0}">{0}</a>'.format(x))
    df["Contents"] = ["Gun-Bowl Member Management",
                     "insert/edit members:활동회원 리스트",
                      "insert/edit scores: 점수 입력 및 수정",
                     "birthdays by month:회원 달별 생일",
                     "days passed after entry:가입후 경과 일자",
                     "list of INACTIVE members: 비활동회원 리스트",
                     "Recent average of scores: 점수 데이터",
                     "Random team up: 랜덤으로 팀짜기"]
    return (df.to_html(escape=False))


@app.route("/members")
def members():
#     df = pd.DataFrame({"GOOD":["View Members List"]})
#     df["GOOD"] = df["GOOD"].apply(lambda x: '<a href="https://docs.google.com/spreadsheets/d/1EqfynT9042BNYMrtraM4R8CsMR3rL7qZbp_kWsw32nI/edit#gid=0">{0}</a>'.format(x))
#     return(df.to_html(escape=False))
    return redirect("https://docs.google.com/spreadsheets/d/1EqfynT9042BNYMrtraM4R8CsMR3rL7qZbp_kWsw32nI/edit#gid=0", code=302)
#         return redirect("/", code=302)

@app.route("/scores")
def scores():
    return redirect("https://docs.google.com/spreadsheets/d/1TNjv8ANZEE58FjX3_cZXgkFHp8NT2Z54rarJbHSzTdM/edit#gid=1797500471", code = 302)

@app.route("/birthday")
def birthday():
#     con = create_engine("sqlite:///data.sqlite")
    members = pd.read_csv("https://docs.google.com/spreadsheets/d/1EqfynT9042BNYMrtraM4R8CsMR3rL7qZbp_kWsw32nI/export?format=csv&gid=0")
    members["birthday"] = pd.to_datetime(members["birthday"])
    members["day"] = pd.DatetimeIndex(members["birthday"]).day
    members["name"] = members["name"] + "/" + members["day"].astype(str)
    members["month"] = pd.DatetimeIndex(members['birthday']).month
    members.sort_values("day",inplace = True)
    members.reset_index(drop = True,inplace = True)
    df = members.pivot(values="name",columns="month").apply(lambda x: pd.Series(x.dropna().values))
    df = df.replace(np.nan, '', regex=True)

    return (df.to_html())

@app.route("/passed")
def passed():
#     con = create_engine("sqlite:///data.sqlite")
    members = pd.read_csv("https://docs.google.com/spreadsheets/d/1EqfynT9042BNYMrtraM4R8CsMR3rL7qZbp_kWsw32nI/export?format=csv&gid=0")
    members["entry"] = pd.to_datetime(members["entry"])
    today = pd.to_datetime("today")
    members["passed"] = today - members["entry"]
    members = members.sort_values("passed",ascending=False)
    members.reset_index(drop = True, inplace = True)
    members.index+=1

    return (members.to_html())

@app.route("/inactive")
def inactive():
#     con = create_engine("sqlite:///data.sqlite")
    con = create_engine("postgres://qcumacnfmicopw:c700fed529373aa3b54a62168e0914d2a0d1d5b458aa965d4aea319662c6ed97@ec2-174-129-27-158.compute-1.amazonaws.com:5432/d5koeu8hgsrr65")
    inactive = pd.read_sql("inactive",con)
    inactive.index=inactive.index+1
    

    return (inactive.to_html())



@app.route("/recent",methods=["GET","POST"])
def recent():
    if request.method == "POST":
        num = request.form["num"]
        if num == "":
            num = 0
        num = int(num)
        scores = pd.ExcelFile("https://docs.google.com/spreadsheets/u/0/d/1TNjv8ANZEE58FjX3_cZXgkFHp8NT2Z54rarJbHSzTdM/export?format=xlsx&id=1TNjv8ANZEE58FjX3_cZXgkFHp8NT2Z54rarJbHSzTdM")
        sheets = scores.sheet_names
        s = pd.DataFrame()
        for i in sheets:
            df = scores.parse(i)
            df.set_index(df.columns[0],inplace=True)

            for c in range(0,len(df.columns)):
                df.iloc[:,c] = pd.to_numeric(df.iloc[:,c],errors="coerce",downcast="integer")

            df[i] = df.apply(lambda x: x.dropna().values.tolist(),axis=1)
            df = pd.DataFrame(df[i])
            s = pd.merge(s,df,left_index=True,right_index=True,how="outer")

            
        s1 = s.sort_index(axis=0).sort_index(axis=1)
        
        if num == 0:
            return(s1.to_html())
        
        s["concat"] = s.apply(lambda x: x.dropna().values.tolist(),axis=1)
        #flip == [::-1]
        #recent 10 games
        s["concat"] = s["concat"].apply(lambda x: [item for sublist in x for item in sublist][-num:])
        s["games"] = s["concat"].apply(lambda x: len(x))
        s = s[s["games"]>1]
        s["stdev"] = s["concat"].apply(lambda x: stdev(x))
        s["avg"] = s["concat"].apply(lambda x: mean(x))
        s = s[["avg","games","stdev","concat"]].sort_values("avg",ascending=False)
        
        #highlighting according to average and gender
        s.reset_index(inplace=True)
        s.rename(columns={"index":"name"},inplace=True)
        members = pd.read_csv("https://docs.google.com/spreadsheets/d/1EqfynT9042BNYMrtraM4R8CsMR3rL7qZbp_kWsw32nI/export?format=csv&gid=0")
        members = members[["name","gender"]]
        members.set_index("name",inplace=True)
        s = pd.merge(s,members,on="name",how="inner")
        
        def highlight(x):
            c0 = 'border-color: black'
            c1 = 'background-color: pink'
            c2 = 'background-color: lightblue'
            c3 = 'background-color: lightgreen'
            c4 = 'background-color: yellow'
            c5 = 'background-color: orange'
            c6 = 'background-color: red'
            g1 = 'background-color: lightblue'
            g2 = 'background-color: pink'
            #if want set no default colors 
            #c2 = ''  
            m1 = x["avg"] > 0
            m2 = x["avg"] >= 100
            m3 = x["avg"] >= 140
            m4 = x["avg"] >= 160
            m5 = x["avg"] >= 180
            m6 = x["avg"] >= 200
            mg1 = x["gender"] == 1
            mg2 = x["gender"] == 2

            df1 = pd.DataFrame(c0,index=x.index, columns=x.columns)

            df1.loc[m1, 'avg'] = c1
            df1.loc[m2, 'avg'] = c2
            df1.loc[m3, 'avg'] = c3
            df1.loc[m4, 'avg'] = c4
            df1.loc[m5, 'avg'] = c5
            df1.loc[m6, 'avg'] = c6
            df1.loc[mg1, 'name'] = g1
            df1.loc[mg2, 'name'] = g2
            return df1
        s.index+=1
        s = s.style.hide_columns(["gender"]).apply(highlight, axis=None)
#         return(df.render())
        
        return(
            s.render()+render_template("n.html")+
            s1.to_html()
              )
    return render_template("recent.html")

@app.route("/random", methods=["GET", "POST"])
def random():
    if request.method == "POST":
        num = request.form["num"]
        if num == "":
            num = 30
        num = int(num)
        names = request.form["players"]
        names = names.replace(" ","").split(",")
        
        if num == "":
            num = 0
        num = int(num)
        scores = pd.ExcelFile("https://docs.google.com/spreadsheets/u/0/d/1TNjv8ANZEE58FjX3_cZXgkFHp8NT2Z54rarJbHSzTdM/export?format=xlsx&id=1TNjv8ANZEE58FjX3_cZXgkFHp8NT2Z54rarJbHSzTdM")
        sheets = scores.sheet_names
        s = pd.DataFrame()
        for i in sheets:
            df = scores.parse(i)
            df.set_index(df.columns[0],inplace=True)

            for c in range(0,len(df.columns)):
                df.iloc[:,c] = pd.to_numeric(df.iloc[:,c],errors="coerce",downcast="integer")

            df[i] = df.apply(lambda x: x.dropna().values.tolist(),axis=1)
            df = pd.DataFrame(df[i])
            s = pd.merge(s,df,left_index=True,right_index=True,how="outer")
            
        non = pd.DataFrame({"name":names})
        non = df[i] = non[non["name"].isin(list(s.index))==False]
        if  len(non) > 0:
            non = ",".join(non["name"])
            return(f"{non} not found")
        
        s = s[s.index.isin(names)]
        
        s["concat"] = s.apply(lambda x: x.dropna().values.tolist(),axis=1)
        #flip == [::-1]
        #recent n games
        s["concat"] = s["concat"].apply(lambda x: [item for sublist in x for item in sublist][-num:])
#         s["games"] = s["concat"].apply(lambda x: len(x))
#         s["stdev"] = s["concat"].apply(lambda x: stdev(x))
        s["avg"] = s["concat"].apply(lambda x: mean(x))
        
        s = s[["avg"]].reset_index()
        s.columns = ["name","avg"]
        team_df = s.copy()
        
        allow = request.form["allow"].replace(" ","")
        if allow.isdigit() == True:
            allow = int(allow)
            team_list= []
            num = 1
            for i in range(0,len(names)):
                team_list.append(num)
                num += 1
                if num > int(request.form["numteam"]):
                    num = 1
            for n in range(0,100):
                team_df = team_df.sample(len(team_df))

            go = 0
            n = 0
            fail = 0

            while go ==0:
                n+=1
                team_df = team_df.sample(frac=1).reset_index(drop = True)
                team_df = team_df.sample(len(team_df))
                team_df["team"] = team_list
            #             team_df["pts"] = df["pts"].astype(int)

                sums = team_df.groupby("team")["avg"].sum()
                if (sums.max()-sums.min())<allow:
                    go = 1
                if n == 5000:
                    go = 1
                    fail = 1
            if fail == 1:
                return("5,000 tries, and failed")
            team_df["name"] = team_df["name"].astype(str) + "/" + team_df["avg"].astype(str)
            team_df.sort_values("avg",ascending=False,inplace=True)
            team_df.reset_index(drop=True,inplace=True)
            result = team_df.pivot(values = "name", columns = "team").apply(lambda x: pd.Series(x.dropna().values))
            result.index += 1
            tot = team_df.groupby("team").sum().T
            tot.index = ["total"]
            result = result.append(tot)
            result = result.replace(np.nan, '', regex=True)
            return(result.to_html())
        
        
        return(s.to_html())
        
        
        
    scores = pd.ExcelFile("https://docs.google.com/spreadsheets/u/0/d/1TNjv8ANZEE58FjX3_cZXgkFHp8NT2Z54rarJbHSzTdM/export?format=xlsx&id=1TNjv8ANZEE58FjX3_cZXgkFHp8NT2Z54rarJbHSzTdM")
    sheets = scores.sheet_names
    s = pd.DataFrame()
    for i in sheets:
        df = scores.parse(i)
        df.set_index(df.columns[0],inplace=True)
        for c in range(0,len(df.columns)):
            df.iloc[:,c] = pd.to_numeric(df.iloc[:,c],errors="coerce",downcast="integer")
        df[i] = df.apply(lambda x: x.dropna().values.tolist(),axis=1)
        df = pd.DataFrame(df[i])
        s = pd.merge(s,df,left_index=True,right_index=True,how="outer")

    names = list(s.index.unique())
    names = ",".join(names)
    return render_template("random.html")+ names



if __name__ == "__main__":
    app.run(debug=True)
import os
from flask import (
    Flask,
    render_template,
    jsonify,
    request,
    redirect)
import pandas as pd
import numpy as np
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
                  "/addmember",
                  "/members",
                   "/editmember",
                  "/birthday",
                  "/passed",
                  "/inactivate",
                  "/reactivate",
                  "/inactive",
                  "/permanent",
#                    "/attendimport",
                   "/attendcheck",
                   "/attendstatus",
                  "/addscore",
                  "/scores",
                  "/removescore",
                  "/recentavg"]
    df["Title"]=df["Title"].apply(lambda x: '<a href="{0}">{0}</a>'.format(x))
    df["Contents"] = ["Gun-Bowl Member Management",
                     "adds member:회원추가",
                     "list of ACTIVE members:활동회원 리스트",
                      "edit ACTIVE member's DoB & DoE:활동회원 생년월일,가입일 수정",
                     "birthdays by month:회원 달별 생일",
                     "days passed after entry:가입후 경과 일자",
                     "inactivate active member: 활동회원 비활성화",
                     "reactivates inactive member: 비활동회원 활성화",
                     "list of INACTIVE members: 비활동회원 리스트",
                     "permanently remove INACTIVE member:비활동회원 영구삭제",
#                       "imports attendace data in mass: 출석 데이터 엑셀에서 변환",
                      "attendance check: 출석 체크",
                      "attendance status: 출석 현황",
                     "adds/edits score: 점수 추가/수정",
                     "list of scores: 점수 데이터",
                     "remove score: 점수 삭제(이름에 all 입력시 당일 점수 모두 삭제)",
                     "recent average on N number of games, and team set up: 최근 에버, 정모 팀짜기"]
    return (df.to_html(escape=False))

@app.route("/formatdb")
def formatdb():
    con = create_engine("postgres://qcumacnfmicopw:c700fed529373aa3b54a62168e0914d2a0d1d5b458aa965d4aea319662c6ed97@ec2-174-129-27-158.compute-1.amazonaws.com:5432/d5koeu8hgsrr65")
    
#     df = pd.DataFrame({"name":[],"gender":[],"DoB":[],"DoE":[]})
#     df = df.astype({"name":"object","gender":"int"})
#     df["DoB"]=pd.to_datetime(df["DoB"])
#     df["DoE"]=pd.to_datetime(df["DoE"])
# #     con = create_engine("sqlite:///data.sqlite")
#     df.to_sql("members", con, if_exists="replace",index=False)
    
#     df = pd.DataFrame({"name":[],"date":[],"scores":[]})
#     df = df.astype({"name":"object","scores":"object"})
#     df["date"]=pd.to_datetime(df["date"])
# #     con = create_engine("sqlite:///data.sqlite")
#     df.to_sql("scores", con, if_exists="replace",index=False)
    
#     days = ["name","year","month"]
#     for i in range(1,31+1):
#         days.append(str(i))
#     df = pd.DataFrame({"days":days})
#     df = df.T
#     df.columns = df.iloc[0]
#     df = df.iloc[1:]
#     df.to_sql("attendance", con, if_exists="replace",index=False)
    
#     df = pd.DataFrame()
#     df = pd.DataFrame({"name":[],"gender":[],"DoB":[],"DoE":[]})
#     df = df.astype({"name":"object","gender":"int"})
#     df["DoB"]=pd.to_datetime(df["DoB"])
#     df["DoE"]=pd.to_datetime(df["DoE"])
# #     con = create_engine("sqlite:///data.sqlite")
#     df.to_sql("inactive", con, if_exists="replace",index=False)
    df = pd.DataFrame({"name":[]})
    df = df.astype({"name":"object"})
    df.to_sql("regular", con, if_exists="replace", index = False)
    return ("Success")

@app.route("/addmember", methods=["GET", "POST"])
def addmember():
    if request.method == "POST":
        password = request.form["password"]
        if password != "7942":
            return("wrong password")
        
        doe = request.form["doe"].replace(" ","")
        name = request.form["name"].replace(" ","")
        gender = request.form["gender"].replace(" ","")
        dob = request.form["dob"].replace(" ","")
        
        if doe[-1] == ",":
            doe = doe[:-1]
        if name[-1] == ",":
            name = name[:-1]
        if gender != "" and gender[-1] == ",":
            gender = gender[:-1]
        if dob != "" and dob[-1] == ",":
            dob = dob[:-1]
            
        doe = doe.split(",")
        name = name.split(",")
        gender = gender.split(",")
        dob = dob.split(",")
        
        names = []
        dobs = []
        does = []
        genders = []
        names_left = []
        dobs_left = []
        does_left = []
        
        if doe[0].lower() == "import":
            for i in range(0,len(name),4):
                names.append(name[i])
            for i in range(1,len(name)+1,4):
                dobs.append(name[i])
            for i in range(2,len(name)+2,4):
                does.append(name[i])
            for i in range(3,len(name)+3,4):
                genders.append(name[i])
                
        else:
            names = name
            dobs = dob
            does = doe
            genders = gender
        
        if doe[0].lower()!= "import" and len(doe)!=len(name):
            does = []
            for i in range(0,len(name)):
                does.append(doe[0])
        
                
#         con = create_engine("sqlite:///data.sqlite")
        con = create_engine("postgres://qcumacnfmicopw:c700fed529373aa3b54a62168e0914d2a0d1d5b458aa965d4aea319662c6ed97@ec2-174-129-27-158.compute-1.amazonaws.com:5432/d5koeu8hgsrr65")
        members = pd.read_sql("members",con)
        inactive = pd.read_sql("inactive",con)
        left_df= pd.DataFrame()        
        
        for name in names:
            if names.count(name) > 1:
#                 print("no")
                return(f"{name} was foud multiple times")
            if name in list(members["name"]):
                return(f'{name} found in ACTIVE members already')
        
        
        df = pd.DataFrame()
        df["name"] = names
        df["gender"] = genders
        df["DoB"] = dobs
        df["DoE"] = does
        df["DoB"] = pd.to_datetime(df["DoB"])
        df["DoE"] = pd.to_datetime(df["DoE"])
#         df.index = df.index+1
        
        members = pd.concat([members,df]).drop_duplicates(["name"],keep = "last")
        members.to_sql("members", con, if_exists = "replace", index = False)
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

@app.route("/editmember", methods=["GET", "POST"])
def editmember():
    if request.method == "POST":
        password = request.form["password"]
        if password != "7942":
            return("wrong password")
        name = request.form["name"]
        gender = request.form["gender"]
        dob = request.form["dob"]
        if dob != "":
            dob = pd.to_datetime([dob])
        
        doe = request.form["doe"]
        if doe != "":
            doe = pd.to_datetime([doe])
        con = create_engine("postgres://qcumacnfmicopw:c700fed529373aa3b54a62168e0914d2a0d1d5b458aa965d4aea319662c6ed97@ec2-174-129-27-158.compute-1.amazonaws.com:5432/d5koeu8hgsrr65")
        members = pd.read_sql("members",con)
        
        if name not in list(members["name"]):
            return (f"could not find {name} in active members")
        df = members[members["name"]==name]
        if dob != "":
            df["DoB"] = dob
        if doe != "":
            df["DoE"] = doe
        if gender != "":
            df["gender"] = gender
        members = pd.concat([members,df]).drop_duplicates(["name"],keep = "last")
        members.to_sql("members", con, if_exists="replace",index=False)
        return(df.to_html())
    return render_template("editmember.html")
@app.route("/birthday")
def birthday():
#     con = create_engine("sqlite:///data.sqlite")
    con = create_engine("postgres://qcumacnfmicopw:c700fed529373aa3b54a62168e0914d2a0d1d5b458aa965d4aea319662c6ed97@ec2-174-129-27-158.compute-1.amazonaws.com:5432/d5koeu8hgsrr65")
    members = pd.read_sql("members",con)
    members["day"] = pd.DatetimeIndex(members["DoB"]).day
    members["name"] = members["name"] + "/" + members["day"].astype(str)
    members["month"] = pd.DatetimeIndex(members['DoB']).month
    members.sort_values("day",inplace = True)
    members.reset_index(drop = True,inplace = True)
    df = members.pivot(values="name",columns="month").apply(lambda x: pd.Series(x.dropna().values))
    df = df.replace(np.nan, '', regex=True)

    return (df.to_html())

@app.route("/passed")
def passed():
#     con = create_engine("sqlite:///data.sqlite")
    con = create_engine("postgres://qcumacnfmicopw:c700fed529373aa3b54a62168e0914d2a0d1d5b458aa965d4aea319662c6ed97@ec2-174-129-27-158.compute-1.amazonaws.com:5432/d5koeu8hgsrr65")
    members = pd.read_sql("members",con)
    today = pd.to_datetime("today")
    members["passed"] = today - members["DoE"]
    members = members.sort_values("passed",ascending=False)
    members.reset_index(drop = True, inplace = True)
    members.index+=1

    return (members.to_html())

@app.route("/inactivate", methods=["GET", "POST"])
def inactivate():
    if request.method == "POST":
#         con = create_engine("sqlite:///data.sqlite")
        password = request.form["password"]
        if password != "7942":
            return("wrong password")
        
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
        password = request.form["password"]
        if password != "7942":
            return("wrong password")
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
        password = request.form["password"]
        if password != "7942":
            return("wrong password")
        
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

@app.route("/attendimport", methods=["GET", "POST"])
def attendimport():
    if request.method == "POST":
        password = request.form["password"]
        if password != "7942":
            return("wrong password")
        
        date = request.form["date"]
        data = request.form["data"]
        date = pd.to_datetime([date])
        month = str((pd.DatetimeIndex(date).month)[0])
        year = str((pd.DatetimeIndex(date).year)[0])

        con = create_engine("postgres://qcumacnfmicopw:c700fed529373aa3b54a62168e0914d2a0d1d5b458aa965d4aea319662c6ed97@ec2-174-129-27-158.compute-1.amazonaws.com:5432/d5koeu8hgsrr65")
        attendance = pd.read_sql("attendance", con)

        data  = data.replace(" ","")
        if data[-1] == ",":
            data = data[:-1]
        data = data.split(",")

        typ_list = ["벙","정모","정기전","챔프","교류전","상주","건볼리그"]

        df0 = attendance.iloc[:0]
        df = pd.DataFrame(df0)
        day = 1
        result = pd.DataFrame()
        for i in range(0,len(data)):
            if len(data[i]) > 0 and data[i][0].isdigit() == False:
        #         print(data[i])
                df["name"] = [data[i]]
                df["year"] = [year]
                df["month"] = [month]
            if len(data[i])==0 or data[i][0].isdigit() == True:
        #         print(data[i])
                df[str(day)] = data[i] + ";" if data[i] != "" else data[i]
                #value_when_true if condition else value_when_false
                day+=1
            if i+1 <= len(data)-1 and len(data[i+1]) > 0 and data[i+1][0].isdigit() == False:
        #     else:
                result = result.append(df)
                df = pd.DataFrame(df0)
                day = 1
            if i == len(data)-1:
                result = result.append(df)
        result = result.fillna("")
        #save to database here

        attendance = pd.concat([attendance,result]).drop_duplicates(["name","year","month"],keep = "last")
        attendance.sort_values(["month","year","name"], inplace= True)
        attendance.to_sql("attendance", con, if_exists = "replace", index = False)
        # result

        for i in range(1,32):
            for n in range(0,7):
                result[str(i)] = result[str(i)].str.replace(str(n+1),typ_list[n])
        return(result.to_html())
    
    return render_template("attendimport.html")

@app.route("/attendcheck", methods=["GET", "POST"])
def attendcheck():
    if request.method == "POST":
        password = request.form["password"]
        if password != "7942":
            return("wrong password")
        date = request.form["date"]
        typ = request.form["typ"]
        names = request.form["names"]
        del_typ = request.form["del_typ"]
        
        con = create_engine("postgres://qcumacnfmicopw:c700fed529373aa3b54a62168e0914d2a0d1d5b458aa965d4aea319662c6ed97@ec2-174-129-27-158.compute-1.amazonaws.com:5432/d5koeu8hgsrr65")
        attendance = pd.read_sql("attendance", con)
        members = pd.read_sql("members", con)

        attendance = pd.DataFrame(attendance)
        year = pd.DatetimeIndex([date]).year
        year = str(year[0])
        month = pd.DatetimeIndex([date]).month
        month = str(month[0])
        day = pd.DatetimeIndex([date]).day
        day = str(day[0])
        if names[-1] == ",":
            names = names[:-1]
        names = names.replace(" ","").split(",")
        for name in names:
            if names.count(name) > 1:
#                 print("no")
                return(f"{name} was foud multiple times")
            if name not in list(members["name"]):
                return(f'{name} not found in active members')
        df = attendance[attendance["year"]==year][attendance["month"]==month][attendance["name"].isin(names)]
        df["name"] = names
        df["year"] = year
        df["month"] = month
        df = df.fillna("")
        if typ != "":
            typ = typ.replace(" ","").split(",")
            typ_list = ["벙","정모","정기전","챔프","교류전","리그","건볼리그"]
            for t in typ:
                if str(t) not in typ_list:
#                     print("no")
                    return(f'{t} was not find in attendance type')
            for t in typ:
                i = typ_list.index(t) + 1
                df[day] = df[day].str.replace(f"{str(i)};","")
                df[day] = df[day] + str(i) + ";"
        if del_typ != "":
            del_typ = del_typ.replace(" ","").split(",")
            typ_list = ["벙","정모","정기전","챔프","교류전","리그","건볼리그"]
            for t in del_typ:
                if str(t) not in typ_list:
#                     print("no")
                    return(f'{t} was not find in attendance type')
            for t in del_typ:
                i = typ_list.index(t) + 1
                df[day] = df[day].str.replace(f"{str(i)};","")
        attendance = pd.concat([attendance,df]).drop_duplicates(["name","year","month"],keep = "last")
        attendance.sort_values(["month","year","name"], inplace= True)
        attendance.to_sql("attendance", con, if_exists = "replace", index = False)
        for i in range(1,32):
            for n in range(0,7):
                df[str(i)] = df[str(i)].str.replace(str(n+1),typ_list[n])
        return(df.to_html())
    return render_template("attendcheck.html")


@app.route("/attendstatus", methods=["GET", "POST"])
def attendstatus():
    if request.method == "POST":
        con = create_engine("postgres://qcumacnfmicopw:c700fed529373aa3b54a62168e0914d2a0d1d5b458aa965d4aea319662c6ed97@ec2-174-129-27-158.compute-1.amazonaws.com:5432/d5koeu8hgsrr65")
        attendance = pd.read_sql("attendance", con)
        members = pd.read_sql("members",con)
        year = request.form["year"]
        month = request.form["month"].replace(" ","").split(",")

#         if month != "" and month[0] == "0":
#             month = month.replace("0","")
        
        df = attendance[attendance["name"].isin(list(members["name"]))][attendance["year"]==year]
        if month[0] != "":
            df = df[df["month"].isin(month)]
        df["apnd"] = df.iloc[:,3:].sum(axis = 1)
        # df = df[["name","year","month","apnd"]]
        typ_list = ["벙","정모","정기전","챔프","교류전","상주","건볼리그"]
        for typ in typ_list:
            n = typ_list.index(typ)+1
            df[typ] = df["apnd"].str.count(str(n))
        df.drop(columns = ["apnd"], inplace = True)
        df["Total"] = df.iloc[:,3:].sum(axis=1)
        
        if len(month) > 1:
            df = df.groupby(["name","year"]).sum()
            df.sort_values("Total",ascending=False,inplace = True)
            df.reset_index(inplace = True)
            
            noatd = members[members["name"].isin(list(df["name"]))==False]["name"]
            noatd = pd.DataFrame(noatd)
            noatd.sort_values("name",inplace = True)
            col = df.columns
            df = pd.concat([df,noatd])
            df = df[col]
            df.fillna("",inplace = True)
            df.reset_index(drop = True, inplace = True)
            
        if month[0] == "":
            df = df.groupby(["name","year"]).sum()
            df.sort_values("Total",ascending=False,inplace = True)
            df.reset_index(inplace = True)
        if month[0] != "" and len(month)==1:
            for i in range(1,32):
                for n in range(0,7):
                    df[str(i)] = df[str(i)].str.replace(str(n),typ_list[n-1])
                    df.sort_values("정기전",ascending=False,inplace = True)
            noatd = members[members["name"].isin(list(df["name"]))==False]["name"]
            noatd = pd.DataFrame(noatd)
            noatd.sort_values("name",inplace = True)
            col = df.columns
            df = pd.concat([df,noatd])
            df = df[col]
            df.fillna("",inplace = True)
            df.reset_index(drop = True, inplace = True)
        df.index += 1
        return(df.to_html())
    return render_template("attendstatus.html")

@app.route("/attenddata")
def attenddata():
    con = create_engine("postgres://qcumacnfmicopw:c700fed529373aa3b54a62168e0914d2a0d1d5b458aa965d4aea319662c6ed97@ec2-174-129-27-158.compute-1.amazonaws.com:5432/d5koeu8hgsrr65")
    attendance = pd.read_sql("attendance",con)
    attendance.sort_values("name",inplace = True)
    return(attendance.to_html())

@app.route("/addscore", methods=["GET", "POST"])
def addscore():
    if request.method == "POST":
        password = request.form["password"]
        if password != "7942":
            return("wrong password")
        
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
    df = df.replace(np.nan, '', regex=True)
    return(df.to_html())

@app.route("/removescore", methods=["GET", "POST"])
def removescore():
    if request.method == "POST":
        password = request.form["password"]
        if password != "7942":
            return("wrong password")
        
        password = request.form["password"]
        if password != "7942":
            return("wrong password")
        
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
        members = pd.read_sql("members",con)
        df = pd.read_sql("scores",con)
        df = df[df["name"].isin(list(members["name"]))]
        
        
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
        df["avg"] = (df.apply(lambda x: sum(x["scores"]),axis=1)/df["games"]).astype(int)#.round(1)
        df["stdev"] = df.apply(lambda x: np.std(x["scores"]),axis=1).round(1)
        df = df[["avg","stdev","games","scores"]].sort_values("avg",ascending=False).reset_index()
        df.index = df.index+1
        
        
        numteam = request.form["numteam"].replace(" ","")
        if numteam.isdigit() == True:
            members = pd.read_sql("members",con)
            players = request.form["players"].replace(" ","")
            if players[-1]==",":
                players = players[:-1]
            players = players.split(",")
#             allow = int(request.form["allow"].replace(" ",""))

            notfound = []
            for n in players:
                if n not in list(members["name"]):
                    notfound.append(n)
            if len(notfound)>0:
                return(f'could not find {notfound} in active members')
            
            df = df[["name","avg"]]
            team_df = pd.DataFrame({"name":players})
            team_df = pd.merge(team_df,df,on="name").sort_values("avg",ascending=False)
            
            #random team
            allow = request.form["allow"].replace(" ","")
            if allow.isdigit() == True:
                allow = int(allow)
                team_list= []
                num = 1
                for i in range(0,len(players)):
                    team_list.append(num)
                    num += 1
                    if num > int(numteam):
                        num = 1
                for shuffle in range(0,100):
                    random.shuffle(team_list)
                
                go = 0
                n = 0
                fail = 0
                
                while go ==0:
                    n+=1
                    team_df = team_df.sample(frac=1).reset_index(drop = True)
                    random.shuffle(team_list)
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
                    
                    
                    
                    
            #regular team        
            team_list = []
            num = 1
            up = 1
            skip = 0
            for i in range(0,len(players)):
                if skip == 0:
                    team_list.append(num)
                    if up == 1:
                        num += 1
                    if up == 0:
                        num -= 1
                    if num == int(numteam):
                        up = 0
                        team_list.append(num)
                        skip = 1
                    if num == 1:
                        up = 1
                        team_list.append(num)
                        skip = 1
                else:
                    skip = 0
            team_list = team_list[:len(players)]
            
            team_df["team"] = team_list
            team_df["name"] = team_df["name"] + "/" + team_df["avg"].astype(str)
            team_df.reset_index(drop = True, inplace=True)
            df = team_df.pivot(values="name",columns="team").apply(lambda x: pd.Series(x.dropna().values))
            df.index+=1
            
            tot = team_df.groupby("team").sum().T
            tot.index = ["total"]
            
            df = df.append(tot)
            df = df.replace(np.nan, '', regex=True)
            return(df.to_html())
        
        
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
            mg1 = x["gender"] == "1"
            mg2 = x["gender"] == "2"

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
        genders = members[["name","gender"]]
        df = df.merge(genders, on = "name")
        df.index+=1
        df = df.style.hide_columns(["gender"]).apply(highlight, axis=None)
#         df.drop(columns = ["gender"])
        return(df.render())
    return render_template("recentavg.html")


@app.route("/importmembers")
def importmembers():
    con = create_engine("postgres://qcumacnfmicopw:c700fed529373aa3b54a62168e0914d2a0d1d5b458aa965d4aea319662c6ed97@ec2-174-129-27-158.compute-1.amazonaws.com:5432/d5koeu8hgsrr65")
    members = pd.read_excel("members.xlsx")
    members.to_sql("members", con, if_exists = "replace", index = False)
    return("success")

@app.route("/regular", methods=["GET", "POST"])
def regular():
    if request.method == "POST":
        con = create_engine("postgres://qcumacnfmicopw:c700fed529373aa3b54a62168e0914d2a0d1d5b458aa965d4aea319662c6ed97@ec2-174-129-27-158.compute-1.amazonaws.com:5432/d5koeu8hgsrr65")
        members = pd.read_sql("members",con)
        
        name = request.form["name"]
        name = str(name).replace(" ","")
        if name not in list(members["name"]):
            return(f'[{name}]을 회원목록에서 찾지 못하였습니다, could not find [{name}] in members list')
        password = request.form["password"]
        newpw = request.form["newpw"]
        scores = request.form["scores"]
        scores = str(scores).replace(" ","")
        check = scores.replace(",","")
        
        if check != "" and check.isdigit()==False:
            return("점수가 숫자가 아닙니다, the scores inputted were not digits")
        check = scores.split(",")
        
        for c in check:
            if int(c)>300:
                return("점수가 300을 초과할 수 없습니다, score cannot be greater than 0")
            
        if scores != "":
            scores = ","+scores
        newpw = request.form["newpw"]
        date = datetime.datetime.now() + datetime.timedelta(hours=5)
        date = str(date.date())
        
        try:
            regular = pd.read_sql(name,con)
            if password != regular["password"][0]:
                return("wrong password, 암호가 틀렸습니다")
            elif newpw != "":               
                regular["password"] = [newpw]
        except:
            regular = pd.DataFrame()
            regular["name"] = [name]
            if password != "0000":
                return("wrong password, 암호가 틀렸습니다")
            if newpw == "":
                newpw = "0000"
            regular["password"] = [newpw]
        
        try:
            regular[date] += [scores]
        except:
            regular[date] = ""
            regular[date]+=[scores]
        regular.to_sql(name, con, if_exists = "replace", index = False)
        regular.drop(columns = ["password"],inplace = True)
        return(regular.to_html())
    return render_template("regular.html")

@app.route("/regulardata")
def regulardata():
    con = create_engine("postgres://qcumacnfmicopw:c700fed529373aa3b54a62168e0914d2a0d1d5b458aa965d4aea319662c6ed97@ec2-174-129-27-158.compute-1.amazonaws.com:5432/d5koeu8hgsrr65")
    members = pd.read_sql("members",con)
    df = pd.DataFrame()
    for name in list(members["name"]):
        try:
            apnd = pd.read_sql(name,con)
            df = df.append(apnd)
        except:
            print(f"{name} not found")
    df.drop(columns = ["password"],inplace = True)
    df.set_index("name",inplace = True)
    df.sort_index(axis = 1, ascending=False, inplace = True)
    df["scores"] = df.sum(axis=1).str[1:]
    df["scores"] = df["scores"].str.split(",")
    df["scores"] = df.apply(lambda x: [int(i) for i in x["scores"]],axis=1)
    df["games"] = df.apply(lambda x: len(x["scores"]),axis=1)
    df["avg"] = (df.apply(lambda x: sum(x["scores"]),axis=1)/df["games"]).astype(int)
    df["stdev"] = df.apply(lambda x: np.std(x["scores"]),axis=1).round(1)
    df.drop(columns = ["scores"],inplace = True)
    df.reset_index(inplace=True)
    df.sort_values("name",ascending = True, inplace = True)
    df.sort_values("games",ascending = False, inplace = True)
    df.set_index(["name","games","avg","stdev"],inplace = True)
    return(df.to_html())
    
if __name__ == "__main__":
    app.run()

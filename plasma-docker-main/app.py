from flask import Flask, render_template, request, redirect, url_for,session
import requests
import ibm_db
import re
import json

app = Flask(__name__)

app.secret_key = 'a'

conn = ibm_db.connect("DATABASE=bludb;HOSTNAME=54a2f15b-5c0f-46df-8954-7e38e612c2bd.c1ogj3sd0tgtu0lqde00.databases.appdomain.cloud;PORT=32733;SECURITY=SSL;SSLServerCertificate=DigiCertGlobalRootCA.crt;UID=ftz76909;PWD=ZHj9m5VHQ8Cpc6F7",'','')

app = Flask(__name__)

def check(email):
    url = "https://hh01wwg9p0.execute-api.us-east-2.amazonaws.com/plasma/getdata?email="+email
    status = requests.request("GET",url)
    print(status.json())
    return status.json()


@app.route('/registration')
def home():
    return render_template('register.html')

@app.route('/register',methods=['POST'])
def register():
    msg = ''
    if request.method == 'POST' :
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        phone = request.form['phone']
        infected = request.form['infect']
        bloodgrp = request.form['blood']
        sql = "SELECT * FROM user WHERE username =?"
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt,1,username)
        ibm_db.execute(stmt)
        account = ibm_db.fetch_assoc(stmt)
        print(sql)
        print(account)
        if account:
            msg = 'Account already exists !'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address !'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'name must contain only characters and numbers !'
        else:
            insert_sql = "INSERT INTO  user VALUES (?, ?, ?,?, ?, ?)"
            prep_stmt = ibm_db.prepare(conn, insert_sql)
            ibm_db.bind_param(prep_stmt, 1, username)
            ibm_db.bind_param(prep_stmt, 2, email)
            ibm_db.bind_param(prep_stmt, 3, password)
            ibm_db.bind_param(prep_stmt, 4, phone)
            ibm_db.bind_param(prep_stmt, 5, infected)
            ibm_db.bind_param(prep_stmt, 6, bloodgrp)
            
            ibm_db.execute(prep_stmt)
            msg = 'You have successfully registered !'
            
    elif request.method == 'POST':
        msg = 'Please fill out the form !'
    return render_template('register.html', msg = msg)


@app.route('/')    
@app.route('/login')
def login():
    return render_template('login.html')
    
@app.route('/loginpage',methods=['POST'])
def loginpage():
    user = request.form['username']
    password = request.form['password']
    print(user,password)
    global userid
    msg = ''
   
    if request.method == 'POST' :
        username = request.form['username']
        password = request.form['password']
        sql = "SELECT * FROM user WHERE username =? AND password=?"
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt,1,username)
        ibm_db.bind_param(stmt,2,password)
        ibm_db.execute(stmt)
        account = ibm_db.fetch_assoc(stmt)
        print (account)
        if account:
            #session['loggedin'] = True
            #'session['id'] = account['USERNAME']
            #userid=  account['USERNAME']
            #'session['username'] = account['USERNAME']
                       
            msg = 'Logged in successfully !'
            return render_template('request.html', msg = msg)
        else:
            msg = 'Incorrect username / password !'
    return render_template('login.html', msg = msg)
        
@app.route('/stats')
def stats():
    url = "https://hh01wwg9p0.execute-api.us-east-2.amazonaws.com/plasma/getbloodgroupsdata"
    response = requests.get(url)
    r = response.json()
    print(r)
    return render_template('stats.html',b=sum(r),b1=str(r[0]),b2=str(r[1]),b3=str(r[2]),b4=str(r[3]),b5=str(r[4]),b6=str(r[5]),b7=str(r[6]),b8=str(r[7]))

@app.route('/requester')
def requester():
    return render_template('request.html')


@app.route('/requested',methods=['POST'])
def requested():
    bloodgrp = request.form['bloodgrp']
    address = request.form['address']
    print(address)
    msg = ''
    if request.method == 'POST' :
        sql = "SELECT * FROM user WHERE blooggrp=?"
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt,1,bloodgrp)
        ibm_db.execute(stmt)
        account = ibm_db.fetch_assoc(stmt)
        phone=[]
        msg = "Need Plasma of your blood group for: "+address
        while account != False:
            print ("The NAME is : ", account["USERNAME"])
            print ("The PHONE is : ", account["PHONE"])
            myphone=account["PHONE"]
            url="https://www.fast2sms.com/dev/bulkV2?authorization=Fc6VjHa1oE7pmAtWfnkLxXgQidN0rPqz9eIuKl4JGb5SUs8BMOdBYNMtOlvzUoFRGwagj8pmkyi0n1Zq&route=q&message="+msg+"&language=english&flash=0&numbers="+myphone

            #url="https://www.fast2sms.com/dev/bulk?authorization=xCXuwWTzyjOD2ARd1EngbH3a7tKIq5PklJ8YSf0Lh4FQZecs9iNI1dSvuqprxFwCKYJXA5amQkBE36Rl&sender_id=FSTSMS&message="+msg+"&language=english&route=p&numbers="+str(i['phone'])
            result=requests.request("GET",url)
            print(result)
            phone.append(account["PHONE"])
            account = ibm_db.fetch_assoc(stmt)
     
    
        print(phone)
       
        
              
    elif request.method == 'POST':
        msg = 'Please fill out the form !'
    return render_template('request.html', msg = msg)
    phone=[]
    msg = "Need Plasma of your blood group for: "+address
      
    return render_template('request.html', pred="Your request is sent to the concerned people.")
    

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080,debug=True)

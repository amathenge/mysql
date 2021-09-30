import os
from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
import cred

app = Flask(__name__)

# Enter your database connection details below
app.config['SECRET_KEY'] = cred.secret_key
app.config['MYSQL_HOST'] = cred.mysql_host
app.config['MYSQL_DB'] = cred.mysql_db
app.config['MYSQL_USER'] = cred.mysql_user
app.config['MYSQL_PASSWORD'] = cred.mysql_password
app.config['MYSQL_CURSORCLASS'] = cred.mysql_cursorclass

# Intialize MySQL
mysql = MySQL(app)

'''
    Table = customers
    columns: id, integer, auto_increment, primary key
        firstname varchar(64)
        lastname varchar(64)
        email varchar(255)
        birthdate datetime
        joindate datetime
        country varchar(64)
        password varchar(32)
        admin integer  (0 or 1)
'''

@app.route('/')
def home():
    if 'user' not in session:
        return redirect(url_for('login'))
    user = session['user']
    cur = mysql.connection.cursor()
    sql = 'select id, firstname, lastname, email, country from customers'
    cur.execute(sql)
    customers = cur.fetchall()
    return render_template('index.html', customers=customers, user=user)

@app.route('/login', methods=['GET','POST'])
def login():
    if 'user' in session:
        session.pop('user')

    if request.method == 'POST':
        cur = mysql.connection.cursor()
        user = request.form['username']
        pwd = request.form['password']
        sql = "select user, password from users where user = %s and password = md5(%s)"
        cur.execute(sql,[user,pwd])
        result = cur.fetchone()
        if result == None:
            return render_template('index.html', msg='Invalid User or Password')
        else:
            session['user'] = result['user']
            return redirect(url_for('home'))

    return render_template('login.html', msg='')

@app.route('/logout')
def logout():
    if 'user' in session:
        session.pop('user')

    return render_template('logout.html')

@app.route('/search', methods=['GET', 'POST'])
def search():
    if 'user' not in session:
        return redirect(url_for('login'))

    user = session['user']

    if request.method == 'POST':
        firstname = request.form['firstname'].strip()
        lastname = request.form['lastname'].strip()
        email = request.form['email'].strip()
        country = request.form['country'].strip()

        # build the query
        sql = 'select id, firstname, lastname, email, birthdate, joindate, country from customers where '
        a = ''
        paramcount = 0
        param = []
        if firstname != '':
            sql += a+'firstname like %s '
            a = ' and '
            paramcount += 1
            param.append('%'+firstname+'%')
        if lastname != '':
            sql += a+'lastname like %s'
            a = ' and '
            paramcount += 1
            param.append('%'+lastname+'%')
        if email != '':
            sql += a+'email like %s'
            a = ' and '
            paramcount += 1
            param.append('%'+email+'%')
        if country != '':
            sql += a+'country like %s'
            a = ' and '
            paramcount += 1
            param.append('%'+country+'%')

        if paramcount > 0:
            cur = mysql.connection.cursor()
            cur.execute(sql, param)
            result = cur.fetchall()
            # sql += ' | ' + str(param)
            return render_template('search.html', user=user, customers=result)

    return render_template('search.html', user=user, customers=None)

@app.route('/country/<cname>', methods=['GET', 'POST'])
def country(cname):
    if 'user' not in session:
        return redirect(url_for('login'))

    user = session['user']

    cur = mysql.connection.cursor()
    sql = 'select id, firstname, lastname, email, birthdate, joindate, country from customers '
    sql += 'where country = %s'
    rowcount = cur.execute(sql, [cname])
    result = cur.fetchall()
    if rowcount == 0:
        result = None
    return render_template('search.html', user=user, customers=result)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")

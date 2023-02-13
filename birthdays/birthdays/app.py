import os

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session

# Configure application
app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///birthdays.db")


WAF = ['union', 'select', 'from', 'as', 'asc', 'desc', 'order', 'by', 'sort', 'and', 'or', 'load', 'delete',
       'update', 'execute', 'count', 'top', 'between', 'declare', 'distinct', 'distinctrow', 'sleep',
       'waitfor', 'delay', 'having', 'sysdate', 'when', 'dba_user', 'case', 'delay']


def waf(*string):
    ls = list(map(lambda x: x.lower(), string))
    for elem in ls:
        for word in elem.split():
            if word in WAF:
                return False
    return True


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        # TODO: Add the user's entry into the database
        name = request.form.get("name")
        month = request.form.get("month")
        day = request.form.get("day")
        if waf(name, month, day):
            db.execute("INSERT INTO birthdays (name, month, day) VALUES(?, ?, ?)", name, month, day)
            flash("Пользователь добавлен")
            return redirect("/")
        else:
            flash("Обнаружена попытка взлома", "error")
            return redirect("/")

    else:
        # TODO: Display the entries in the database on index.html
        persons = db.execute("SELECT * FROM birthdays")
        print(persons)
        return render_template("index.html", persons=persons)


import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash
import datetime
from helpers import apology, login_required, lookup, usd
import re

app = Flask(__name__)

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# подключаем sql
db = SQL("sqlite:///finance.db")

# проверка что api_key ввели
if not os.environ.get("API_KEY"):
    raise RuntimeError("API_KEY not set")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""
    user_id = session['user_id']

    transaction = db.execute(
        "SELECT symbol, SUM(shares) as shares, purchase_price FROM purchases WHERE owner_id = :id GROUP BY symbol",
        id=session['user_id'])

    current_balance = db.execute("SELECT cash FROM users WHERE id = :id", id=user_id)[0]["cash"]

    for row in transaction:
        quote = lookup(row["symbol"])  # <-- эта строка возвращает котировку только для последней покупки
        row["current_price"] = quote["price"]
        row["total_amount"] = row["current_price"] * row["shares"]
    grand_total = sum([row["total_amount"] for row in transaction]) + current_balance
    return render_template("index.html", transaction=transaction,
                           current_balance=current_balance, grand_total=grand_total)


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""
    if request.method == "GET":
        return render_template("buy.html")

    else:
        symbol = request.form.get("symbol")
        shares = request.form.get("shares")

        if not shares.isdigit():
            return apology("You must enter a integer numbers of shares")

        shares = int(shares)

        if shares < 0:
            return apology("You must enter a positive numbers of shares")

        elif not symbol:
            return apology("You must enter symbol ticker")

        stock = lookup(symbol.upper())

        if stock is None:
            return apology("Ticker does not exist")

        transaction = shares * stock["price"]

        # получаем значение баланса текущего юзера
        user_id = session["user_id"]
        row = db.execute("SELECT cash FROM users WHERE id = ?", user_id)
        user_cash = row[0]["cash"]

        if user_cash < transaction:  # недостаточно средств
            return apology("Insufficient funds")

        new_balance = user_cash - transaction

        # обновляем значенияв бд
        db.execute("UPDATE users SET cash = :cash WHERE id = :id", cash=new_balance, id=user_id)

        date = datetime.datetime.now()

        db.execute("INSERT INTO purchases (owner_id, symbol, shares, purchase_price, date) VALUES (?, ?, ?, ?, ?)",
                   user_id,
                   stock["symbol"], shares, stock["price"], date)

        flash("Bought!")

        # возвращаем пользователя на домашнюю страницу
        return redirect("/")


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    user_id = session["user_id"]
    history_db = db.execute("SELECT * FROM purchases WHERE owner_id = :id", id=user_id)
    return render_template("history.html", history=history_db)


@app.route("/add_balance", methods=["GET", "POST"])
@login_required
def add_balance():
    """func with adding balance"""
    user_id = session["user_id"]
    if request.method == "GET":
        return render_template("add_balance.html")
    else:
        new_balance = int(request.form.get("add_balance"))

        if not new_balance:
            return apology("You must give cash")

        balance_now = db.execute("SELECT cash FROM users WHERE id = ?", user_id)[0]["cash"]
        balance_after = balance_now + new_balance
        db.execute("UPDATE users SET cash = :cash WHERE id = :id", cash=balance_after, id=user_id)
        return redirect("/")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # очищаем сессию
    session.clear()

    if request.method == "POST":

        # проверка что логин был введен
        if not request.form.get("username"):
            return apology("must provide username")

        # проверка что пароль был введен
        elif not request.form.get("password"):
            return apology("must provide password")

        # запрос в бд для получения инфы о юзере
        rows = db.execute("SELECT * FROM users WHERE username = :name", name=request.form.get("username"))

        # првоеряем что пароль и логин ввели правильно
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password")

        # запоминаем пользователя в сессию
        session["user_id"] = rows[0]["id"]

        flash("You are logged in")
        # возвращаем пользователя на домашнюю страницу
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # очищаем текущую сессию
    session.clear()

    # отправляем юзера на домашнюю страницу
    return redirect("/")


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""
    if request.method == "POST":
        if not request.form.get("symbol"):
            return apology("must provide symbol")

        stock = lookup(request.form.get("symbol").upper())
        if stock is None:
            return apology("No share found for this symbol")

        return render_template("quoted.html", quote=stock)

    # если метод get
    else:
        return render_template("quote.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    # очищаем сессию
    session.clear()

    if request.method == "POST":

        # проверяем что пользователь ввел юзернейм
        if not request.form.get("username"):
            return apology("must provide username")

        # проверяем что пользователь ввел пароль
        elif not request.form.get("password"):
            return apology("must provide username")

        # убеждаемся что потверждение пароля пользователь ввел
        elif not request.form.get("confirmation"):
            return apology("must provide confirm password")

        # проверяем что пароль и потверждение совпадает
        elif request.form.get("password") != request.form.get("confirmation"):
            return apology("Password mismatch")

        # проверяем что пользователь ввел уникальный юзернейм
        try:
            db.execute("INSERT INTO users (username, hash) VALUES(?, ?)",
                       request.form.get("username"), generate_password_hash(request.form.get("password")))
        except:
            return apology("username already exists")

        # запоминаем пользователя в текущую сессию
        user_data = db.execute("SELECT * FROM users WHERE username = :name", name=request.form.get("username"))
        session["user_id"] = user_data[0]["id"]

        flash("You are registered")

        # возвращаемся на домашнюю странциу
        return redirect("/")

    # если метод GET
    else:
        return render_template("register.html")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    if request.method == "POST":
        # проверяем на правильный символ
        symbol = request.form.get("symbol")
        shares = int(request.form.get("shares"))

        if not symbol:
            return apology("You must enter symbol ticker")

        stock = lookup(request.form.get("symbol").upper())

        if stock is None:
            return apology("Ticker does not exist")

        if shares < 0:
            return apology("The minimum number of shares must be at least 1")

        user_id = session["user_id"]
        # stocks = db.execute("SELECT shares, symbol FROM purchases WHERE owner_id=:id", id=session["user_id"])

        # обновляем баланс пользователя
        transaction_val = shares * stock["price"]
        cash = db.execute("SELECT cash FROM users WHERE id = :id", id=user_id)[0]["cash"]
        new_balance = cash + transaction_val

        db.execute("UPDATE users SET cash = :new_balance WHERE id = :id", id=user_id,
                   new_balance=new_balance)

        # добавляем строку описывающую текущую операцию
        date = datetime.datetime.now()
        db.execute("INSERT INTO purchases (owner_id, symbol, shares, purchase_price, date) VALUES (?, ?, ?, ?, ?)",
                   user_id,
                   stock["symbol"], (-1) * shares, stock["price"], date)

        # проверка есть ли у пользователя данные акции на продажу
        user_shares = db.execute("SELECT shares FROM purchases WHERE owner_id = :id AND symbol=:symbol", id=user_id,
                                 symbol=stock["symbol"])

        if user_shares[0]["shares"] < shares:
            return apology("Too many shares you wanna sell")


        flash('Sold!')

        # возвращаемся на домашнюю странциу
        return redirect("/")

    else:
        # если метод GET
        symbols = db.execute("SELECT symbol FROM purchases WHERE owner_id=:id GROUP BY symbol HAVING SUM(shares)",
                             id=session["user_id"])
        return render_template("sell.html", symbols=symbols)

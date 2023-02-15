import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash
import datetime
from helpers import apology, login_required, lookup, usd
import colorama

# Configure application
app = Flask(__name__)

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")

# Make sure API key is set
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

    user = db.execute("SELECT id, cash FROM users WHERE id = :id", id=session['user_id'])
    print(f"session user={session}, users: {user}")

    rows = db.execute("SELECT * FROM purchases WHERE owner_id = :id", id=session['user_id'])
    print(rows)

    current_balance = user[0]['cash']

    for row in rows:
        if row["symbol"]:
            quote = lookup(row["symbol"])  # <-- эта строка возвращает котировку только для последней покупки
            row["current_price"] = quote["price"]
            row["total_amount"] = row["current_price"] * row["shares"]
        else:
            row["current_price"] = 0.0
            row["total_amount"] = 0

    grand_total = sum([row["total_amount"] for row in rows]) + current_balance
    return render_template("index.html", rows=rows,
                           current_balance=current_balance, grand_total=grand_total)


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""
    if request.method == "GET":
        return render_template("buy.html")

    else:
        symbol = request.form.get("symbol")
        shares = int(request.form.get("shares"))

        if not symbol:
            return apology("You must enter symbol ticker")

        stock = lookup(symbol.upper())

        if stock is None:
            return apology("Ticker does not exist")

        if shares < 1:
            return apology("The minimum number of shares must be at least 1")

        transaction_value = shares * stock["price"]

        user_id = session["user_id"]
        user_cash_db = db.execute("SELECT cash FROM users WHERE id = :id", id=user_id)
        user_cash = user_cash_db[0]["cash"]

        if user_cash < transaction_value:  # недостаточно средств
            return apology("Insufficient funds")

        uptd_cash = user_cash - transaction_value

        # update the SQL database
        db.execute("UPDATE users SET cash = :cash WHERE id = :id", cash=uptd_cash, id=user_id)

        date = datetime.datetime.now()

        print(f"{shares} cost {stock['price']}")
        db.execute("INSERT INTO purchases (owner_id, symbol, shares, purchase_price, date) VALUES (?, ?, ?, ?, ?)",
                   user_id,
                   stock["symbol"], shares, stock["price"], date)

        flash("Bought!")

        # redirect to main page
        return redirect("/")


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    user_id = session["user_id"]
    history_db = db.execute("SELECT * FROM purchases WHERE owner_id = :id", id=user_id)
    print(history_db)
    return render_template("history.html", history=history_db)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :name", name=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        flash("You are logged in")
        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""
    if request.method == "POST":
        try:
            quote = lookup(request.form.get("requested_share"))

        except:
            return apology("No share found for this symbol")

        return render_template("quoted.html", quote=quote)

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("quote.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    # Forget any user_id
    session.clear()

    if request.method == "POST":

        # Ensure what username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure what password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Ensure what password confirm was submitted
        elif not request.form.get("confirmation"):
            return apology("must provide confirm password", 403)

        # Ensure what password and confirm password are equal
        elif request.form.get("password") != request.form.get("confirmation"):
            return apology("Password mismatch", 403)

        # check for uniql username
        try:
            db.execute("INSERT INTO users (username, hash) VALUES(?, ?)",
                       request.form.get("username"), generate_password_hash(request.form.get("password")))
        except:
            return apology("username already exists", 400)

        # Remember which user has logged in
        user_data = db.execute("SELECT * FROM users WHERE username = :name", name=request.form.get("username"))
        session["user_id"] = user_data[0]["id"]

        # db.execute("INSERT INTO purchases (owner_id, symbol, shares, purchase_price, date) VALUES (?, ?, ?, ?, ?)",
        #            session["user_id"], "", 0, "Cash", datetime.datetime.now())

        flash("You are registered")

        # Redirect user to home page
        return redirect("/")

    # if request == GET
    else:
        return render_template("register.html")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    if request.method == "POST":
        # проверяем на правильный символ
        stock = lookup(request.form.get("symbol"))
        if not stock:
            return apology("Missing Symbol")

        # убеждаемся, что пароль был отправлен
        elif not request.form.get("shares"):
            return apology("Missing shares")

        else:
            shares = int(request.form.get("shares"))

            # cash = db.execute("SELECT cash FROM users WHERE id = :id", id=session["user_id"])
            # cash = cash[0]["cash"]

            # select the symbol shares of that user
            user_id = session["user_id"]
            user_shares = db.execute("SELECT shares FROM purchases WHERE owner_id = :id AND symbol=:symbol", id=user_id,
                                     symbol=stock["symbol"])

            # stocks = db.execute("SELECT shares, symbol FROM purchases WHERE owner_id=:id", id=session["user_id"])

            # check if enough shares to sell
            if user_shares[0]["shares"] < shares:
                return apology("Too many shares you wanna sell")

            # update  of a sell
            date = datetime.datetime.now()
            db.execute("INSERT INTO purchases (owner_id, symbol, shares, purchase_price, date) VALUES (?, ?, ?, ?, ?)",
                       user_id,
                       stock["symbol"], shares, stock["price"], date)

            # update user cash (increase)
            db.execute("UPDATE users SET cash = cash + :cash_after WHERE id = :id", id=session["user_id"],
                       cash_after=stock["price"] * float(shares))

            # decrement the shares count
            print("кол-во акций юзера", user_shares[0]["shares"])
            shares_total = user_shares[0]["shares"] - shares

            # если после вычитания ноль, удалить акции из портфеля
            if shares_total == 0:
                db.execute("DELETE FROM purchases \
                        WHERE owner_id=:id AND symbol=:symbol", id=session["user_id"], symbol=stock["symbol"])
            # otherwise, update portfolio shares count
            else:
                db.execute("UPDATE purchases SET shares=:shares \
                    WHERE owner_id=:id AND symbol=:symbol", shares=shares_total, id=session["user_id"],
                           symbol=stock["symbol"])

            # flash bought alert
            flash('Sold!')

            # Redirect user to home page
            return redirect("/")

    else:
        # If request method GET
        stocks = db.execute("SELECT shares, symbol FROM purchases WHERE owner_id=:id", id=session["user_id"])
        return render_template("sell.html", stocks=stocks)

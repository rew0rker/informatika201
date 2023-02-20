# decrement the shares count
shares_total = user_shares[0]["shares"] - share
# если после вычитания ноль, удалить акции из портфеля
if shares_total == 0:
    db.execute("DELETE FROM purchases \
            WHERE owner_id=:id AND symbol=:symbol", id=session["user_id"], symbol=stock["symbol"])
# otherwise, update portfolio shares count
else:
    db.execute("UPDATE purchases SET shares=:shares \
        WHERE owner_id=:id AND symbol=:symbol", shares=shares_total, id=session["user_id"],
               symbol=stock["symbol"])
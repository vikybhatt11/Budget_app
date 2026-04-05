from flask import Flask, render_template, request, redirect, url_for
from database import get_db, init_db

app = Flask(__name__)

with app.app_context():
    init_db()

@app.route("/")
def index():
    db = get_db()
    paychecks = db.execute("SELECT * FROM paychecks ORDER BY date DESC").fetchall()
    result = []
    for p in paychecks:
        allocations = db.execute(
            "SELECT * FROM allocations WHERE paycheck_id = ?", (p["id"],)
        ).fetchall()
        total_allocated = sum(a["amount"] for a in allocations)
        result.append({
            "date": p["date"],
            "amount": p["amount"],
            "allocations": allocations,
            "remaining": p["amount"] - total_allocated
        })

    db.close()
    return render_template("index.html", paychecks=result)

@app.route("/add-paycheck", methods=["POST"])
def add_paycheck():
    date = request.form["date"]
    amount = request.form["amount"]
    db = get_db()
    cursor = db.execute(
        "INSERT INTO paychecks (date, amount) VALUES (?, ?)", (date, amount)
    )
    paycheck_id = cursor.lastrowid

    categories = ["roth","house","emergency","rent","car","food","subscriptions","dining","misc"]
    for category in categories:
        value = float(request.form.get(category, 0))
        db.execute(
            "INSERT INTO allocations (paycheck_id, category, amount) VALUES (?, ?, ?)",
            (paycheck_id, category, value)
        )
    db.execute("INSERT INTO paychecks (date, amount) VALUES (?, ?)", (date, amount))

    db.commit()
    db.close()
    return redirect(url_for("index"))

@app.route("/monthly")
def monthly():
    db = get_db()
    
    paychecks = db.execute(
        "SELECT * FROM paychecks ORDER BY date DESC"
    ).fetchall()

    monthly_data = {}
    for p in paychecks:
        month = p["date"][:7]  # gets "2026-04"
        if month not in monthly_data:
            monthly_data[month] = {"income": 0, "allocations": {}}
        
        monthly_data[month]["income"] += p["amount"]
        
        allocations = db.execute(
            "SELECT * FROM allocations WHERE paycheck_id = ?", (p["id"],)
        ).fetchall()
        
        for a in allocations:
            cat = a["category"]
            if cat not in monthly_data[month]["allocations"]:
                monthly_data[month]["allocations"][cat] = 0
            monthly_data[month]["allocations"][cat] += a["amount"]

    db.close()
    return render_template("monthly.html", monthly_data=monthly_data)

@app.route("/yearly")
def yearly():
    db = get_db()

    paychecks = db.execute(
        "SELECT * FROM paychecks ORDER BY date DESC"
    ).fetchall()

    yearly_data = {}
    for p in paychecks:
        year = p["date"][:4]  # gets "2026"
        if year not in yearly_data:
            yearly_data[year] = {"income": 0, "allocations": {}}

        yearly_data[year]["income"] += p["amount"]

        allocations = db.execute(
            "SELECT * FROM allocations WHERE paycheck_id = ?", (p["id"],)
        ).fetchall()

        for a in allocations:
            cat = a["category"]
            if cat not in yearly_data[year]["allocations"]:
                yearly_data[year]["allocations"][cat] = 0
            yearly_data[year]["allocations"][cat] += a["amount"]

    db.close()
    return render_template("yearly.html", yearly_data=yearly_data)

@app.route("/goals")
def goals():
    db = get_db()
    goals = db.execute("SELECT * FROM goals ORDER BY deadline ASC").fetchall()
    db.close()
    return render_template("goals.html", goals=goals)

@app.route("/add-goal", methods=["POST"])
def add_goal():
    name = request.form["name"]
    target = float(request.form["target"])
    saved = float(request.form.get("saved", 0))
    deadline = request.form["deadline"]
    db = get_db()
    db.execute(
        "INSERT INTO goals (name, target, saved, deadline) VALUES (?, ?, ?, ?)",
        (name, target, saved, deadline)
    )
    db.commit()
    db.close()
    return redirect(url_for("goals"))

@app.route("/update-goal/<int:goal_id>", methods=["POST"])
def update_goal(goal_id):
    saved = float(request.form["saved"])
    db = get_db()
    db.execute("UPDATE goals SET saved = ? WHERE id = ?", (saved, goal_id))
    db.commit()
    db.close()
    return redirect(url_for("goals"))

@app.route("/delete-goal/<int:goal_id>", methods=["POST"])
def delete_goal(goal_id):
    db = get_db()
    db.execute("DELETE FROM goals WHERE id = ?", (goal_id,))
    db.commit()
    db.close()
    return redirect(url_for("goals"))
if __name__ == "__main__":
    app.run(debug=True)
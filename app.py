##221644989 KA KGOPA
from flask import Flask, render_template, request, redirect, url_for,Response
import mysql.connector
import matplotlib.pyplot as plt
import pandas as pd
import io

app = Flask(__name__)
##connection to database
db = mysql.connector.connect(
        host="127.0.0.1",
        user="root",
        password="root",
        database="apple_db"
    )

cur=db.cursor()
cur.execute("USE apple_db")
cur.execute("CREATE TABLE IF NOT EXISTS users(id int auto_increment primary key ,name varchar(50),email varchar(50),password varchar(50))")

##login
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        conn = db
        cur = conn.cursor()

        cur.execute("SELECT * FROM users WHERE email=%s AND password=%s", (email, password))
        user = cur.fetchone()

        cur.close()
        conn.close()

        if user:
            return redirect(url_for('dashboard'))
        else:
            return "Invalid details"

    return render_template("login.html")


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        conn = db
        cur = conn.cursor()

        cur.execute(
            "INSERT INTO users (name, email, password) VALUES (%s, %s, %s)",
            (name, email, password)
        )

        conn.commit()
        cur.close()
        conn.close()

        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/dashboard')
def dashboard():
    df = pd.read_csv("apple_data.csv")

    df["Total_kWh"] = df[
        ["Year1_kWh","Year2_kWh","Year3_kWh","Year4_kWh","Year5_kWh"]
    ].sum(axis=1)

    df["Total_CO2"] = df[
        ["Year1_CO2e","Year2_CO2e","Year3_CO2e","Year4_CO2e","Year5_CO2e"]
    ].sum(axis=1)

    summary = df.groupby("Product")[["Total_kWh","Total_CO2"]].sum().reset_index()

    return render_template("dashboard.html",
                           products=summary["Product"].tolist(),
                           energy=summary["Total_kWh"].tolist(),
                           co2=summary["Total_CO2"].tolist())
@app.route('/energy_chart')
def energy_chart():
    df = pd.read_csv("apple_data.csv")

    df["Total_kWh"] = df[
        ["Year1_kWh","Year2_kWh","Year3_kWh","Year4_kWh","Year5_kWh"]
    ].sum(axis=1)

    summary = df.groupby("Product")["Total_kWh"].sum()

    plt.figure()
    summary.plot(kind='bar')
    plt.title("Total Electricity Consumption (kWh)")
    plt.xlabel("Product")
    plt.ylabel("kWh")

    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plt.close()

    return Response(img.getvalue(), mimetype='image/png')


@app.route('/co2_chart')
def co2_chart():
    df = pd.read_csv("apple_data.csv")

    df["Total_CO2"] = df[
        ["Year1_CO2e","Year2_CO2e","Year3_CO2e","Year4_CO2e","Year5_CO2e"]
    ].sum(axis=1)

    summary = df.groupby("Product")["Total_CO2"].sum()

    plt.figure()
    summary.plot(kind='bar')
    plt.title("Total CO₂ Emissions")
    plt.xlabel("Product")
    plt.ylabel("CO₂")

    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plt.close()

    return Response(img.getvalue(), mimetype='image/png')


if __name__ == "__main__":
    app.run(debug=True)
from flask import Flask, request, render_template, redirect, url_for, session, jsonify, flash
import requests
import os
from flask_jwt_extended import JWTManager


LOGIN_MICROSERVICE = os.getenv("LOGIN_MICROSERVICE", "http://login-service:5001")
TODO_MICROSERVICE = os.getenv("TODO_MICROSERVICE", "http://todo-service:5002")

app = Flask(__name__)
app.secret_key = "myjwtsecret"
jwt = JWTManager(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    next_url = request.args.get("next", url_for("todo_page"))

    if request.method == 'GET':
        return render_template('login.html', next=next_url)

    elif request.method == 'POST':
        username = request.form.get("username")
        password = request.form.get("password")

        if not username or not password:
            return "Missing form data!", 400
        
        data = {"username": username, "password": password}
        headers = {"Content-Type": "application/json"}

        response = requests.post(f"{LOGIN_MICROSERVICE}/login", json=data, headers=headers)

        print("Login Response Status Code:", response.status_code)
        print("Login Response Data:", response.text)

        if response.status_code == 200:
            json_response = response.json()
            session["token"] = json_response.get("access_token", "")

            print("Stored Token:", session.get("token"))

            return redirect(next_url)

        elif response.status_code in [400, 401]:
            flash("Unable to login, please check your credentials", "failure")
            return redirect(url_for("login"))

        else:
            flash("An unexpected error occurred", "failure")
            return redirect(url_for("login"))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    elif request.method == 'POST':
        data = {"username": request.form["username"], "password": request.form["password"]}
        response = requests.post(f"{LOGIN_MICROSERVICE}/register", json=data)

        if response.status_code == 201:
            return redirect(url_for("login"))
        return "Registration failed!", 400

@app.route('/todo', methods=['GET', 'POST'])
def todo_page():
    token = session.get('token')
    if not token:
        return redirect(url_for("login", next=request.url))

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }

    print("Request Headers being sent:", headers)

    if request.method == 'GET':
        response = requests.get(f"{TODO_MICROSERVICE}/todo", headers=headers)
        if response.status_code != 200:
            return jsonify({"error": "Failed to load tasks"}), response.status_code
        tasks = response.json()
        return render_template("todo.html", tasks=tasks)

    elif request.method == 'POST':
        data = {
            "task": request.form["task"],
            "description": request.form.get("description", ""),
            "isCompleted": request.form.get("isCompleted", "").lower() in ["true", "on", "1", True]
        }
        response = requests.post(f"{TODO_MICROSERVICE}/todo", json=data, headers=headers)
        if response.status_code == 201:
            return redirect(url_for("todo_page"))
        return jsonify({"error": "Failed to create task"}), 400


@app.route('/todo/update/<int:id>', methods=['GET', 'POST'])
def alter_data(id):
    token = session.get('token')
    if not token:
        return jsonify({"error": "Unauthorized"}), 401

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }

    print(token)

    if request.method == 'GET':
        response = requests.get(f"{TODO_MICROSERVICE}/todo/update/{id}", headers=headers)
        if response.status_code != 200:
            return jsonify({"error": "Failed to load tasks"}), response.status_code
        task = response.json()
        return render_template('update_form.html', task=task)

    elif request.method == 'POST':
        data = {
                "task": request.form["task"],
                "description": request.form.get("description", ""),
                "isCompleted": request.form.get("isCompleted").lower() in ["true", "on", "1", True]
            }
        response = requests.post(f"{TODO_MICROSERVICE}/todo/update/{id}", json=data, headers=headers)

        print(response.status_code)
        print(response.text)

        if response.status_code in [200, 204]:
            flash("Task updated successfully", "success")
            return redirect(url_for("todo_page"))
        return jsonify({"error": "Failed to process request"}), response.status_code


@app.route('/todo/delete/<int:id>', methods=['POST'])
def delete_data(id):
    token = session.get('token')
    if not token:
        return jsonify({"error": "Unauthorized"}), 401

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }
    
    response = requests.post(f"{TODO_MICROSERVICE}/todo/delete/{id}", headers=headers)
    print(headers)
    print(f"esponse Status: {response.status_code}, Response Data: {response.text}")
    if response.status_code in [200, 204]:
        flash("Task deleted successfully", "success")
        return redirect(url_for("todo_page"))
    return jsonify({"error": "Failed to delete task"}), 400

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

if __name__ == '__main__':
    app.run(host="0.0.0.0",port=5050, debug=True)
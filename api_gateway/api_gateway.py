from flask import Flask, request, render_template, redirect, url_for, session, jsonify
import requests
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity


LOGIN_MICROSERVICE = 'http://127.0.0.1:5001'
TODO_MICROSERVICE = 'http://127.0.0.1:5002'

app = Flask(__name__)
app.secret_key = "supersecretkey"
jwt = JWTManager(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    elif request.method == 'POST':
        data = {"username": request.form["username"], "password": request.form["password"]}
        response = requests.post(f"{LOGIN_MICROSERVICE}/login", json=data)

        if response.status_code == 200:
            json_response = response.json()
            session["token"] = response.json()["token"]
            return redirect(url_for("todo_page"))
        return "Login failed!", 401

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
@jwt_required()
def todo_page():
    current_user = get_jwt_identity()
    headers = {"Authorization": f"Bearer {session.get('token', '')}"}

    if request.method == 'GET':
        response = requests.get(f"{TODO_MICROSERVICE}/todo", headers=headers)
        if response.status_code == 401:
            return redirect(url_for("login"))
        tasks = response.json() if response.status_code == 200 else []
        return render_template("todo.html", tasks=tasks, user=current_user)
    
    elif request.method == 'POST':
        data = {"task": request.form["task"], "description": request.form["description"], "isCompleted": request.form["isCompleted"]}
        response = requests.post(f"{TODO_MICROSERVICE}/todo", json=data, headers=headers)
        if response.status_code == 401:
            return redirect(url_for("login"))
        tasks = response.json() if response.status_code == 200 else []
        return redirect(url_for("todo_page"))

@app.route('/todo/<int:id>', methods=['PUT', 'DELETE'])
@jwt_required()
def alter_data(id):
    headers = {"Authorization": f"Bearer {session.get('token', '')}"}

    if request.method == 'PUT':
        data = request.json
        response = requests.put(f"{TODO_MICROSERVICE}/todo/{id}", json=data, headers=headers)
        if response.status_code in [200, 204]:
            return jsonify({"message": "Success"}), response.status_code
        return jsonify({"error": "Failed to process request"}), response.status_code
    
    elif request.method == 'DELETE':
        response = requests.delete(f"{TODO_MICROSERVICE}/todo/{id}", headers=headers)
        if response.status_code in [200, 204]:
            return jsonify({"message": "Success"}), response.status_code
        return jsonify({"error": "Failed to process request"}), response.status_code


if __name__ == '__main__':
    app.run(port=5000, debug=True)
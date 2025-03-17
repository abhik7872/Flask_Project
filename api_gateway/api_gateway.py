from flask import Flask, request, render_template, redirect, url_for, session, jsonify
import requests
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity


LOGIN_MICROSERVICE = 'http://127.0.0.1:5001'
TODO_MICROSERVICE = 'http://127.0.0.1:5002'

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
            session["token"] = json_response.get("access_token", "")  # ✅ Fix key name

            print("Stored Token:", session.get("token"))  # Debugging

            return redirect(next_url)

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
def todo_page():
    token = session.get('token')
    if not token:
        return redirect(url_for("login", next=request.url))

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"  # ✅ Ensure token is included
    }

    print("Request Headers being sent:", headers)  # Debugging

    if request.method == 'GET':
        response = requests.get(f"{TODO_MICROSERVICE}/todo", headers=headers)
        if response.status_code != 200:
            return jsonify({"error": "Failed to load tasks"}), response.status_code
        tasks = response.json()
        return render_template("todo.html", tasks=tasks)

    elif request.method == 'POST':
        data = {
            "task": request.form["task"],
            "description": request.form.get("description", "")
        }
        response = requests.post(f"{TODO_MICROSERVICE}/todo", json=data, headers=headers)
        if response.status_code == 201:
            return redirect(url_for("todo_page"))
        return jsonify({"error": "Failed to create task"}), 400


@app.route('/todo/<int:id>', methods=['PUT', 'DELETE'])
def alter_data(id):
    token = session.get('token')
    if not token:
        return jsonify({"error": "Unauthorized"}), 401

    headers = {
        "Authorization": f"Bearer {token}"
    }

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
from flask import Flask, request, jsonify
from flask_migrate import Migrate
from flask_jwt_extended import jwt_required, get_jwt_identity, JWTManager
from model import db, ToDO
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE", "postgresql://abhikchatterjee:ABHIK@localhost/dummy_db")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = "myjwtsecret"
app.config['JWT_TOKEN_LOCATION'] = ['headers']
app.config["JWT_HEADER_NAME"] = "Authorization"
app.config["JWT_HEADER_TYPE"] = "Bearer"

db.init_app(app)
migrate = Migrate(app, db)
jwt = JWTManager(app)

@app.route('/todo', methods=['GET'], endpoint="get_todo")
@jwt_required()
def get_todo():
    print(request.headers)
    user_id = get_jwt_identity()
    print(user_id)
    todos = ToDO.query.filter_by(user_id=user_id).all()
    return jsonify([{ "id": todo.id, "task": todo.task, "description": todo.description, "isCompleted": todo.isCompleted } for todo in todos])

@app.route("/todo", methods=["POST"])
@jwt_required()
def create_todo():
    user_id = get_jwt_identity()
    data = request.json

    new_todo = ToDO(task=data["task"], description=data.get("description", ""), isCompleted=data.get("isCompleted", False), user_id=user_id)
    db.session.add(new_todo)
    db.session.commit()

    return jsonify({"message": "Task created successfully!"}), 201

@app.route("/todo/update/<int:id>", methods=["GET", "POST"], endpoint="update_todo")
@jwt_required()
def update_todo(id):
    user_id = int(get_jwt_identity())
    todo = ToDO.query.get(id)
    
    print(f"User ID from token: {user_id}")
    print(f"Task ID: {id}, Owner: {todo.user_id if todo else 'Not Found'}") 

    if not todo:
        return jsonify({"error": "Task not found"}), 404

    if todo.user_id != user_id:
        return jsonify({"error": "Unauthorized"}), 403

    if request.method == 'GET':
        print(f"Task details: ID={todo.id}, Task={todo.task}, Description={todo.description}, Completed={todo.isCompleted}")
        return jsonify({
            "id": todo.id,
            "task": todo.task,
            "description": todo.description,
            "isCompleted": todo.isCompleted
        })

    elif request.method == "POST":
        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid JSON data"}), 400
        todo.task = data.get("task", todo.task)
        todo.description = data.get("description", todo.description)
        todo.isCompleted = str(data.get("isCompleted", todo.isCompleted)).lower() in ["true", "on", "1", True]
        db.session.commit()
        return jsonify({"message": "Task updated successfully!"})
    

@app.route("/todo/delete/<int:id>", methods=["POST"], endpoint="delete_todo")
@jwt_required()
def delete_todo(id):
    user_id = int(get_jwt_identity())
    todo = ToDO.query.get(id)
    
    print(f"User ID from token: {user_id}")
    print(type(user_id), type(id), type(todo.user_id))
    print(f"Task ID: {id}, Owner: {todo.user_id if todo else 'Not Found'}") 

    if not todo:
        return jsonify({"error": "Task not found"}), 404

    if todo.user_id != user_id:
        return jsonify({"error": "Unauthorized"}), 403

    # data = request.get_json()
    # if not data:
    #     return jsonify({"error": "Invalid JSON data"}), 400
    
    # method = request.form.get("_method")
    
    db.session.delete(todo)
    db.session.commit()
    return jsonify({"message": "Task deleted successfully!"})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002, debug=True)
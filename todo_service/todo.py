from flask import Flask, request, jsonify
from flask_migrate import Migrate
from flask_jwt_extended import jwt_required, get_jwt_identity, JWTManager
from model import db, ToDO

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://abhikchatterjee:ABHIK@localhost/dummy_db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = "myjwtsecret"
app.config['JWT_TOKEN_LOCATION'] = ['headers']
app.config["JWT_HEADER_NAME"] = "Authorization"  # ✅ Set Authorization header
app.config["JWT_HEADER_TYPE"] = "Bearer"  # ✅ Define token prefix

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

    new_todo = ToDO(task=data["task"], description=data.get("description", ""), user_id=user_id)
    db.session.add(new_todo)
    db.session.commit()

    return jsonify({"message": "Task created successfully!"}), 201

@app.route("/todo/<int:id>", methods=["PUT", "DELETE", "POST"], endpoint="update_todo")
@jwt_required()
def update_todo(id):
    user_id = get_jwt_identity()
    todo = ToDO.query.get(id)
    
    print(f"🔹 User ID from token: {user_id}")  # Debugging
    print(f"🔹 Task ID: {id}, Owner: {todo.user_id if todo else 'Not Found'}") 

    if not todo:
        return jsonify({"error": "Task not found"}), 404

    if todo.user_id != user_id:
        return jsonify({"error": "Unauthorized"}), 403

    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid JSON data"}), 400
    
    method = request.form.get("_method")

    if method == 'PUT':
        todo.task = data.get("task", todo.task)
        todo.description = data.get("description", todo.description)
        todo.isCompleted = data.get("isCompleted", todo.isCompleted)
        db.session.commit()
        return jsonify({"message": "Task updated successfully!"})
    
    elif method == 'DELETE':
        db.session.delete(todo)
        db.session.commit()
        return jsonify({"message": "Task deleted successfully!"})


if __name__ == '__main__':
    app.run(port=5002, debug=True)
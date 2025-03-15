from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager, create_access_token
from model import db, ToDO

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://abhikchatterjee:ABHIK@localhost/todo_db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
migrate = Migrate(app, db)

@app.route('/todo', methods=['GET'])
def get_todo():
    todos = ToDO.query.all()
    return jsonify([{ "id": todo.id, "task": todo.task, "description": todo.description, "isCompleted": todo.isCompleted } for todo in todos])

@app.route("/todo", methods=["POST"])
def create_todo():
    data = request.json
    new_todo = ToDO(task=data["task"], description=data.get("description"))
    db.session.add(new_todo)
    db.session.commit()
    return jsonify({"message": "Task created successfully!"}), 201

@app.route("/todo/<int:id>", methods=["PUT"])
def update_todo(id):
    todo = ToDO.query.get(id)
    if not todo:
        return jsonify({"error": "Task not found"}), 404
    
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid json data"}), 400
    
    todo.task = data.get("task", todo.task)
    todo.description = data.get("description", todo.description)
    todo.isCompleted = data.get("isCompleted", todo.isCompleted)
    db.session.commit()
    return jsonify({"message": "Task updated successfully!"})

@app.route("/todo/<int:id>", methods=["DELETE"])
def delete_todo(id):
    todo = ToDO.query.get(id)
    if not todo:
        return jsonify({"error": "Task not found"}), 404
    db.session.delete(todo)
    db.session.commit()
    return jsonify({"message": "Task deleted successfully!"})

if __name__ == '__main__':
    app.run(port=5002, debug=True)
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager, create_access_token
from model import db, User

app = Flask(__name__)
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://abhikchatterjee:ABHIK@localhost/dummy_db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = "myjwtsecret"

db.init_app(app)
migrate = Migrate(app, db)
jwt = JWTManager(app)

@app.route('/users', methods=['GET'])
def userList():
    users = User.query.all()
    return jsonify([{ "id": user.id, "username": user.username, "password": user.password } for user in users])

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    if User.query.filter_by(username=data['username']).first():
        return jsonify({"error": "User already exists"}), 400
    
    user = User(username=data['username'], password=data['password'])
    db.session.add(user)
    db.session.commit()
    return jsonify({"message": "User registered"}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(username=data['username'], password=data['password']).first()
    if not user:
        return jsonify({"error": "Invalid credentials"}), 401
    token = create_access_token(identity=str(user.id))
    return jsonify({"access_token": token})

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5001, debug=True)
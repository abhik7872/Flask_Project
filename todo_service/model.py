from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class ToDO(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    task = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(255), nullable=False)
    isCompleted = db.Column(db.Boolean, default=False)
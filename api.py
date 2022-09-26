from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app=Flask(__name__)

app.config['SECRET_KEY']='secret'
app.config['SQLALCEHMY_DATABASE_URI']='sqlite://tmp/tasj.db'

db=SQLAlchemy(app)

class User(db.Model):
    id=db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(20),unique=True)
    password = db.Column(db.String(20))
    admin= db.Column(db.Boolean)

class task(db.Model):
    id=db.Column(db.Integer, primary_key=True)
    text=db.Column(db.String(100))
    complete=db.Column(db.Boolean)
    user_id =db.Column(db.Integer)

if __name__== '__main__':
    app.run(debug=True)

db.create_all()
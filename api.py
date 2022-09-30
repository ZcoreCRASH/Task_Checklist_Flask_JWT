
from flask import Flask, request, jsonify, make_response
import jwt
import datetime
from flask_sqlalchemy import SQLAlchemy
from crypt import methods
import uuid # TO generate random IDs
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

app=Flask(__name__)

app.config['SECRET_KEY']= 'secret' # Specifying the secret key for the token
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:////mnt/c/Users/Aditya/tutorial-env/Flask_git/task.db'

db= SQLAlchemy(app) #Passing the app to SQLAlchemy

# Initiating two tables one for users and the other for tasks to be performed 

class User(db.Model): # Making the table inherit the db.model
    id = db.Column(db.Integer, primary_key=True)
    # Using another ID since one is put in the token and the number of users can be seen if token is decoded
    public_id = db.Column(db.String(50), unique=True) 
    name=db.Column(db.String(50))
    password= db.Column(db.String(50))
    admin=db.Column(db.Boolean) # Admin column to specify whether the user is an admin or not

class Task(db.Model):
    id=db.Column(db.Integer, primary_key=True) # ID of the task 
    text=db.Column(db.String(100)) # Description of the task
    complete=db.Column(db.Boolean) # Show true when the task is completed
    user_id=db.Column(db.Integer) # The same user ID as the User table

def token_required(f):
    @wraps(f)
    def decorated(*args,**kwargs):
        token=None

        if 'X-Access-Token' in request.headers:
            token=request.headers['X-Access-Token']
        if not token:
            return jsonify({"message":"No token found"}), 401
        try:
            data= jwt.decode(token, app.config['SECRET_KEY'])
            current_user=User.query.filter_by(public_id=data['public_id']).first()
        except:
            return jsonify({"message":"Token is Invalid"}), 401
        
        return f(current_user,*args,**kwargs)
    return decorated

def admin_required(f):
    @wraps(f)
    def decorator(*args,**kwargs):
        token=request.headers['X-Access-Token']
        data= jwt.decode(token, app.config['SECRET_KEY'])
        current_admin=User.query.filter_by(public_id=data['public_id']).first()
        if not current_admin.admin:
            return jsonify({'message':'Cannot perform that function'})
        return f(current_admin,*args,**kwargs)
    return decorator

@app.route('/user',methods=['POST'])
@token_required
@admin_required
def create_user(current_user):
    data= request.get_json()
    hashed_password= generate_password_hash(data['password'],method='sha256')

    new_user = User(public_id=str(uuid.uuid1()),name=data['name'], password=hashed_password, admin=False)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'New user created!'})

@app.route('/user')
@token_required 
@admin_required
def get_all_users(current_user,current_admin):

    users= User.query.all() # SQLAlchemy queries all records from the user table

    output=[]

    for user in users:
        user_data={}
        user_data['public_id']=user.public_id
        user_data['name']=user.name
        user_data['password']= user.password
        user_data['admin']=user.admin
        output+=[user_data]

    return jsonify({'users' : output})
    
@app.route('/user/<public_id>')
@token_required 
@admin_required
def get_one_user(current_user,public_id):
    
    user=User.query.filter_by(public_id=public_id).first()

    if not user:
        return jsonify({"message":"No user found"})

    user_data={}
    user_data['public_id']=user.public_id
    user_data['name']=user.name
    user_data['password']= user.password
    user_data['admin']=user.admin

    return jsonify({'user':user_data})


@app.route('/user/<public_id>',methods=["PUT"])
@token_required 
@admin_required
def promote_user(current_user,public_id): # Promotes a user ID passed to an admin user
    
    user=User.query.filter_by(public_id=public_id).first()

    if not user:
        return jsonify({"message":"No user found"})
    user.admin=True
    db.session.commit()
    return jsonify({'message':'The user has been promoted!'})

@app.route('/user/<public_id>',methods=["DELETE"])
@token_required 
@admin_required
def delete_user(current_user,public_id):
    user=User.query.filter_by(public_id=public_id).first()

    if not user:
        return jsonify({"message":"No user found"})
    db.session.delete(user)
    db.session.commit()
    
    return jsonify({"message":"The user has been deleted!"})

@app.route('/login')
def login():
    auth= request.authorization

    if not auth or not auth.username or not auth.password:
        return make_response("Could not verify", 401,{'WWW-Authenticate':'Basic realm="Login Required!"'})
    user= User.query.filter_by(name=auth.username).first()

    if not user:
        return make_response("Could not verify", 401,{'WWW-Authenticate':'Basic realm="Login Required!"'})
    
    if check_password_hash(user.password,auth.password):
        token = jwt.encode({"public_id":user.public_id , "exp" :   datetime.datetime.utcnow() + datetime.timedelta(minutes=30)}, app.config['SECRET_KEY'])

        return jsonify({'token': token.decode('UTF-8')})
    return make_response("Could not verify", 401,{'WWW-Authenticate':'Basic realm="Login Required!"'})

@app.route('/tasks',methods=['POST'])
@token_required
def create_task(current_user):
    data=request.get_json()
    new_task = Task(text=data['text'],complete=False,user_id=current_user.id)
    db.session.add(new_task)
    db.session.commit()
    return jsonify({"message":"New task created!"})

@app.route('/tasks',methods=["GET"])
@token_required
def get_all_tasks(current_user):
    tasks=Task.query.filter_by(user_id=current_user.id).all()
    output=[]

    for task in tasks:
        task_data={}
        task_data['id']=task.id
        task_data['text']=task.text
        task_data['complete']=task.complete
        output+=[task_data]
    return jsonify(output)

@app.route('/tasks/<task_id>',methods=['GET'])
@token_required
def get_one_task(current_user,task_id):
    task=Task.query.filter_by(id=task_id,user_id=current_user.id).first()

    if not task:
        return jsonify({"message":"No task found with that ID"})
    task_data={}
    task_data['id']=task.id
    task_data['text']=task.text
    task_data['complete']=task.complete  

    return jsonify(task_data)

@app.route('/tasks/<task_id>',methods=['PUT'])
@token_required
def complete_task(current_user,task_id):
    task=Task.query.filter_by(id=task_id,user_id=current_user.id).first()

    if not task:
        return jsonify({"message":"No task found with that ID"})
    
    task.complete=True
    db.session.commit()
    
    return jsonify({"message":"Task has been completed!"})

@app.route('/tasks/<task_id>',methods=['DELETE'])
@token_required
def delete_task(current_user,task_id):
    task=Task.query.filter_by(id=task_id,user_id=current_user.id).first()

    if not task:
        return jsonify({"message":"No task found with that ID"})
    db.session.delete(task)
    db.session.commit()
    return jsonify({"message":"The task has been deleted"})

if __name__=='__main__':
    app.run(debug=True)
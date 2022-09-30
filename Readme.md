# A Task Checklist system implemented with RESTFUL APIs in python using Flask.

The objective of this program is to serve as the backend for a system where a regular user can create tasks, mark them as completed or delete tasks. Admin users have control over creating new users, getting all users or deleting users. After initial login, subsequent requests are authenticated using JSON Web Tokens or JWT. The users and tasks are stored and retrieved from the database using SQLAlchemy.

## Modules used

- Flask 
- JWT
- flask_sqlalchemy
- uuid
- werkzeug.security
- functools
- datetime

## Test

Each of the REST APIs were simultaneously tested on the Postman API Platform upon creation and were found to be running perfectly.


from thoughts_app.config.mysqlconnection import connectToMySQL
from thoughts_app.models import thought
from flask import flash
import re

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$') 
NAME_REGEX=re.compile(r"^[A-Z][a-zA-Z '.-]*[A-Za-z][^-]$")

class User:
    def __init__(self,data):
        self.id=data['id']
        self.fname=data['fname']
        self.lname=data['lname']
        self.email=data['email']
        self.password = data['password']
        self.created_at = data['created_at']
        self.updated_at = data['updated_at']
        self.thoughts=[]

    @classmethod
    def getAll (cls):
        query="SELECT * FROM users;"
        results=connectToMySQL('exam').query_db(query)
        users=[]
        for user in results:
            users.append(cls(user))
        return users
    
    @classmethod
    def getEmail (cls,email):
        query="SELECT * FROM users WHERE email = %(email)s"
        data={
            'email':email
        }
        result=connectToMySQL('exam').query_db(query,data)
        if len(result)>0:
            return cls(result[0])
        else:
            return None

    @classmethod
    def getId (cls,id):
        query="SELECT * FROM users WHERE id = %(id)s"
        data={
            'id':id
        }
        result=connectToMySQL('exam').query_db(query,data)
        print("Result", result)
        if len(result)>0:
            return cls(result[0])
        else:
            return None
    
    @classmethod
    def save(cls, data):
        query = "INSERT INTO users (id, fname, lname, email, password, created_at, updated_at) VALUES (%(id)s,%(fname)s, %(lname)s, %(email)s, %(pswrd)s, NOW(),NOW());"
        mysql = connectToMySQL('exam')
        result = mysql.query_db(query, data)
        print(result)
        data_usuario={'id':data['id']}
        print(data_usuario)
        return cls.getId(data_usuario['id'])
    
    @classmethod
    def get_liked_thoughts_of_user(cls, id):
        query= f"SELECT * FROM users LEFT JOIN likes ON likes.user_id=users.id LEFT JOIN thoughts ON likes.thought_id=thoughts.id WHERE users.id={id};"
        results=  connectToMySQL('exam').query_db( query )
        user = cls( results[0] )
        for row_from_db in results:
            thought_data = {
                "id" : row_from_db["thoughts.id"],
                "thought" : row_from_db["thought"],
                "created_at" : row_from_db["thoughts.created_at"],
                "updated_at" : row_from_db["thoughts.updated_at"],
                "user_id_creator": row_from_db['user_id_creator'],
                "likes": row_from_db['likes']
            }
            user.thoughts.append(thought.Thought(thought_data))
        return user
    
    @staticmethod
    def user_validations(user):
        is_valid=True
        if user['fname'] == "" or user['lname'] == "" or user['pswrd'] == ""  :
            flash("Missing fields.")
            is_valid=False
        if len(user['fname']) < 2 or len(user['lname']) < 2:
            flash ("First name and last name must be at least of 2 characters.")
            is_valid=False
        if not NAME_REGEX.match(user['fname']):
            flash("Please enter a valid first name.")
            is_valid=False
        if not NAME_REGEX.match(user['lname']):
            flash("Please enter a valid last name.")
            is_valid=False
        if not EMAIL_REGEX.match(user['email']): 
            flash("Invalid email address!")
            is_valid = False
        if User.getEmail(user['email']) != None:
            flash("User's email already register, please sign in.")
            is_valid=False
        if len(user['pswrd']) < 8: 
            flash('Password must be at least 8 characters.')
            is_valid=False
        return is_valid
    

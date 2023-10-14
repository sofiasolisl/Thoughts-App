from thoughts_app.config.mysqlconnection import connectToMySQL
from thoughts_app.models import user 
from flask import flash

class Thought:
    def __init__(self, data):
        self.id=data['id']
        self.thought=data['thought']
        self.created_at = data['created_at']
        self.updated_at = data['updated_at']
        self.user_id_creator=data['user_id_creator']
        self.likes=data['likes']
        self.users=[]

    @classmethod
    def getAll (cls):
        query="SELECT * FROM thoughts;"
        results=connectToMySQL('exam').query_db(query)
        thoughts=[]
        for thought in results:
            thoughts.append(cls(thought))
        return thoughts
        
    @classmethod
    def getId (cls,id):
        query="SELECT * FROM thoughts WHERE id = %(id)s"
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
    def addLike (cls,data):
        query="UPDATE thoughts SET likes = %(likes)s WHERE id = %(id)s;"
        result =connectToMySQL('exam').query_db(query,data)
        query="INSERT INTO likes (user_id, thought_id) VALUES (%(user_id)s,%(id)s);"
        result =connectToMySQL('exam').query_db(query,data)
        query= "SELECT * FROM thoughts LEFT JOIN likes ON likes.thought_id=thoughts.id LEFT JOIN users ON likes.user_id=users.id WHERE thoughts.id = %(id)s AND users.id=%(user_id)s;"
        results =  connectToMySQL('exam').query_db( query,data )
        thought = cls( results[0] )
        for row_from_db in results:
            user_data = {
                "id" : row_from_db["users.id"],
                "fname": row_from_db['fname'],
                "lname": row_from_db['lname'],
                "email": row_from_db['email'],
                "password": row_from_db['password'],
                "created_at" : row_from_db["users.created_at"],
                "updated_at" : row_from_db["users.updated_at"],
            }
            thought.users.append(user.User(user_data))
        return thought
    @classmethod
    def removeLike (cls,data):
        query="UPDATE thoughts SET likes =%(likes)s WHERE id = %(id)s;"
        result =connectToMySQL('exam').query_db(query,data)
        query= "SELECT * FROM thoughts LEFT JOIN likes ON likes.thought_id=thoughts.id LEFT JOIN users ON likes.user_id=users.id WHERE thoughts.id = %(id)s AND users.id=%(user_id)s;"
        results =  connectToMySQL('exam').query_db( query ,data)
        thought = cls( results[0] )
        for row_from_db in results:
            user_data = {
                "id" : row_from_db["users.id"],
                "fname": row_from_db['fname'],
                "lname": row_from_db['lname'],
                "email": row_from_db['email'],
                "password": row_from_db['password'],
                "created_at" : row_from_db["users.created_at"],
                "updated_at" : row_from_db["users.updated_at"],
            }
            for user in thought.users:
                if user.id == user_data['id']:
                    print("USER.ID",user.id)

        query="DELETE from likes WHERE user_id= %(user_id)s AND thought_id=%(id)s;"
        result =connectToMySQL('exam').query_db(query,data)
        return thought
    @classmethod
    def save(cls, data):
        query = "INSERT INTO thoughts (id, thought, created_at, updated_at, user_id_creator,likes) VALUES (%(id)s,%(thought)s, NOW(),NOW(),%(user_id_creator)s, %(likes)s);"
        print(query)
        mysql = connectToMySQL('exam')
        result = mysql.query_db(query, data)
        print('Resultttt',result)
        data_usuario={'id':data['id']}
        print(data_usuario)
        return cls.getId(data_usuario['id'])
    
    @classmethod
    def delete(cls, data):
        query = "DELETE FROM thoughts WHERE id = %(id)s and user_id_creator = %(user_id_creator)s;"
        mysql = connectToMySQL('exam')
        result = mysql.query_db(query, data)
        query="DELETE from likes WHERE thought_id=%(id)s ;"
        result =connectToMySQL('exam').query_db(query)
        return result
    
    @staticmethod
    def validations(thought):
        is_valid=True
        if thought['thought'] == "" or len(thought['thought'])<5:
            flash('Thought is required and must be of at least 5 characters')
            is_valid=False
        return is_valid

from thoughts_app import app
from thoughts_app.models.user import User
from thoughts_app.models.thought import Thought
from flask import render_template, redirect, request, session
from flask_bcrypt import Bcrypt
from flask import flash
bcrypt = Bcrypt(app) 

@app.route("/", methods = ['GET','POST'])
@app.route("/signup", methods = ['GET','POST'])
def signup():
    if request.method == "POST":
        if request.form['pswrd'] == request.form['pswrd_confirm']:
            data=dict(request.form)
            print("password", request.form['pswrd'])
            if request.form['pswrd'] == "" :
                flash("Input a Password")
                return redirect ('/')
            data['pswrd'] = bcrypt.generate_password_hash(request.form['pswrd'])
            if User.getAll() == None:
                data ['id']=1
            else:
                data ['id']=len(User.getAll()) + 1
            print (data)
            if User.user_validations(request.form):
                print("Super con las validaciones")
                user=User.save(data)
                session['id']=user.id
                return redirect ('/dashboard')
        else:
            flash("Password must be the same")
    return render_template('index.html')

@app.route("/signin", methods = ['GET','POST'])
def signin():
    if request.method == "POST":
        data=dict(request.form)
        db_user=User.getEmail(data.get('email'))
        print(db_user)
        if  db_user is None or not bcrypt.check_password_hash(db_user.password , data.get('pswrd')) :
            flash ("Invalid Email/Password")
            return redirect ('/')
        session["id"]=db_user.id
        return redirect ("/dashboard")
    else:
        return render_template('index.html')

@app.route("/dashboard", methods=['GET','POST'])
def dashboard():
        if session.get('id') == None:
            return redirect ('/')
        if request.method == "POST":
            data=dict(request.form)
            if Thought.validations(data):
                print("Super con las validaciones")
                print(Thought.getAll())
                if Thought.getAll()== []:
                    data ['id']=1
                else:
                    data ['id']=len(Thought.getAll()) + 1
                data ['user_id_creator'] = session.get('id')
                data ['likes']=0
                print(data)
                Thought.save(data)
                return redirect ('/dashboard')
            else:
                return redirect ('/dashboard')
        else:
            user = User.getId(session.get('id'))
            thoughts=Thought.getAll()
            users= User.getAll()
            all_user_liked_thoughts=User.get_liked_thoughts_of_user(session.get('id')).thoughts
            return render_template('dashboard.html', user=user, all_thoughts=thoughts, all_users=users, all_user_liked_thoughts=all_user_liked_thoughts)
@app.route ('/user_thoughts/<int:user_id>')
def user_thoughts(user_id):
    if session.get('id') == None:
        return redirect ('/')
    session_user=User.getId(session.get('id'))
    user_to_display=User.getId(user_id)
    all_users=User.getAll()
    all_thoughts=Thought.getAll()
    all_user_thoughts=[]
    for thought in all_thoughts:
        if thought.user_id_creator == user_to_display.id:
            all_user_thoughts.append(thought)
    print(all_user_thoughts)
    return render_template('user_thoughts.html', session_user=session_user, user_to_display=user_to_display, all_users=all_users, all_user_thoughts=all_user_thoughts)
    
@app.route("/like/<int:thought_id>/<string:value>")
def like(thought_id,value):
    if value=="like":
        if session.get('id') == None:
            return redirect ('/')
        user=User.getId(session.get('id'))
        thought=Thought.getId(thought_id)
        likes=thought.likes
        likes=likes+1
        data = {
            'id': thought.id,
            'likes': likes,
            'user_id':user.id
        }
        Thought.addLike(data)
        return redirect ('/dashboard')
    else:
        if session.get('id') == None:
            return redirect ('/')
        user=User.getId(session.get('id'))
        thought=Thought.getId(thought_id)
        likes=thought.likes
        likes=likes-1
        data = {
            'id': thought.id,
            'likes': likes,
            'user_id':user.id
        }
        Thought.removeLike(data)
        return redirect ('/dashboard')


@app.route('/delete/<int:thought_id>')
def delete(thought_id):
    thought=Thought.getId(thought_id)
    data={}
    if session.get('id') == thought.user_id_creator:
        data['id']=thought.id
        data['user_id_creator']=thought.user_id_creator
        Thought.delete(data)
        return redirect ('/dashboard')
    else:
        return redirect ('/dashboard')


@app.route("/logout")
def logout():
    if session.get('id') == None:
        return redirect ('/')
    session.clear()
    return redirect ('/')
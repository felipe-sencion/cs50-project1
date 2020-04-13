import os

from flask import Flask, session, render_template, request
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)

# Check for environment variable
if not os.getenv('DATABASE_URL'):
    raise RuntimeError('DATABASE_URL is not set')

# Configure session to use filesystem
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

# Set up database
engine = create_engine(os.getenv('DATABASE_URL'))
db = scoped_session(sessionmaker(bind=engine))


@app.route("/", methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if request.form.get('button') == 'log_in':
            user = db.execute('SELECT * FROM users WHERE username = :username AND password = :password',
            {'username':username, 'password':password}).fetchone()
            if user is None:
                return render_template('error.html', message='Incorrect Username or Password. Please try again.')
            else:
                session['id'] = user.id
                session['username'] = user.username
                session['password'] = user.password
                print(f'user_id: {session["id"]}, username: {session["username"]}, password: {session["password"]}')
        else:
            if db.execute('SELECT * FROM users WHERE username = :username',
            {'username':username}).rowcount == 0:
                db.execute('INSERT INTO users(username, password) VALUES (:username, :password)', {'username':username, 'password':password})
                db.commit()
                return render_template('success.html')
            else:
                return render_template('error.html', message=f'The user "{username}" has already been taken.')
        #print(f'posted online {session["username"]} {session["password"]} {request.form.get("button")}')
    return render_template('index.html')

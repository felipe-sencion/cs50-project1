import os

from flask import Flask, session, render_template, request
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)
MIN_PASSWORD_LENGTH = 8

# Check for environment variable
if not os.getenv('DATABASE_URL'):
    raise RuntimeError('DATABASE_URL is not set')

# Configure sess WHERE isbn LIKE "\%1\%"') WHERE isbn LIKE "\%1\%"') WHERE isbn LIKE "\%1\%"') WHERE isbn LIKE "\%1\%"') WHERE isbn LIKE "\%1\%"')ion to use filesystem
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

# Set up database
engine = create_engine(os.getenv('DATABASE_URL'))
db = scoped_session(sessionmaker(bind=engine))


@app.route("/", methods=['GET', 'POST'])
def index():
    if request.form.get('button') == 'log_out':
        session['id'] = None
        session['username'] = ""
        session['password'] = ""
        return render_template('index.html')

    if request.method == 'GET' and session['id'] is not None:
        return render_template('home.html')
    return render_template('index.html')

@app.route('/home', methods=['POST'])
def home():
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
                return render_template('home.html')
                print(f'user_id: {session["id"]}, username: {session["username"]}, password: {session["password"]}')
        elif request.form.get('button') == 'sign_up':
            if db.execute('SELECT * FROM users WHERE username = :username',
            {'username':username}).rowcount == 0:
                if len(password) < MIN_PASSWORD_LENGTH:
                    return render_template('error.html', message=f'Password must be at least {MIN_PASSWORD_LENGTH} characters long.')
                else:
                    db.execute('INSERT INTO users(username, password) VALUES (:username, :password)', {'username':username, 'password':password})
                    db.commit()
                    return render_template('success.html')
            else:
                return render_template('error.html', message=f'The user "{username}" has already been taken.')
        elif request.form.get('button') == 'search':
            pattern = request.form.get('book')
            filtered_books = []
            print('searcheando')
            if len(pattern) >= 0:
                books = db.execute('SELECT * FROM books').fetchall()
                for book in books:
                    if pattern in book.isbn or pattern in book.title or pattern in book.author:
                        filtered_books.append(book)
                        print(f'isbn: {book.isbn} title: {book.title} author: {book.author} year: {book.year}')
                return render_template('home.html', books=filtered_books)
        #print(f'posted online {session["username"]} {session["password"]} {request.form.get("button")}')
    return render_template('home.html')

@app.route('/book/<string:isbn>')
def book(isbn):
    isbn = isbn.zfill(10)
    book = db.execute('SELECT * FROM books WHERE isbn=:isbn', {'isbn':isbn}).fetchone()
    return render_template('book.html', book=book)

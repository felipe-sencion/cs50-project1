import os
import requests
import random

from flask import Flask, session, render_template, request, jsonify
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

    if request.method == 'GET' and session.get('id') is not None:
        start = random.randint(1, 4950)
        books = db.execute('SELECT * FROM books WHERE books.id > :book_id LIMIT 50', {'book_id':start}).fetchall()
        return render_template('home.html', books=books)
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
                start = random.randint(1, 4950)
                books = db.execute('SELECT * FROM books WHERE books.id > :book_id LIMIT 50', {'book_id':start}).fetchall()
                return render_template('home.html', books=books)
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
            if len(pattern) >= 0:
                books = db.execute('SELECT * FROM books').fetchall()
                for book in books:
                    if pattern in book.isbn or pattern in book.title or pattern in book.author:
                        filtered_books.append(book)
                return render_template('home.html', books=filtered_books, message='No books found.')
    return render_template('home.html')

@app.route('/book/<string:isbn>', methods=['GET','POST'])
def book(isbn):
    isbn = isbn.zfill(10)
    book = db.execute('SELECT * FROM books WHERE isbn=:isbn', {'isbn':isbn}).fetchone()
    if book is None:
        return render_template('error.html', message='Oops wrong isbn'), 404
    goodreads_data = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "z2OYZnE8iD5zVH7WhIr8GA", "isbns": isbn})
    reviews = db.execute('SELECT * FROM reviews WHERE book_id=:book_id', {'book_id':book.id}).fetchall()

    if request.method == 'POST':
        if session.get('id') is None:
            return render_template('error.html', message='You must be logged before rating')
        else:
            rating = int(request.form.get('rating_select'))
            review = request.form.get('review_text')
            print(f'rating{rating} review{review}')
            if db.execute('SELECT * FROM reviews WHERE book_id=:book_id AND user_id=:user_id', {'book_id':book.id, 'user_id':session['id']}).rowcount == 0:
                db.execute('INSERT INTO reviews(rating, text, book_id, user_id) VALUES(:rating, :text, :book_id, :user_id)', {'rating':rating, 'text':review, 'book_id':book.id, 'user_id':session['id']})
                db.commit()
            else:
                return render_template('error.html', message=f'You have already made a review for {book.title}')

    return render_template('book.html', book=book, goodreads_data=(goodreads_data.json())['books'][0], reviews=reviews)

@app.route('/api/book/<string:isbn>', methods=['GET'])
def book_api(isbn):
    isbn = isbn.zfill(10)
    book = db.execute('SELECT * FROM books WHERE isbn=:isbn', {'isbn':isbn}).fetchone()

    if book is None:
        return render_template('error.html', message='Oops wrong isbn'), 404

    review = goodreads_data = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "z2OYZnE8iD5zVH7WhIr8GA", "isbns": isbn})
    review_json = review.json()['books'][0]
    return jsonify(
    {
        'title': book.title,
        'author': book.author,
        'year': book.year,
        'isbn': book.isbn,
        'review_count': review_json['reviews_count'],
        'average_score': review_json['average_rating']
    }
    )

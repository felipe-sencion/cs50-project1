import csv
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

def populate():
    engine = create_engine(os.getenv('DATABASE_URL'))
    db = scoped_session(sessionmaker(bind=engine))

    file = open('books.csv')
    books = csv.reader(file)

    for isbn, title, author, year in books:
        year = int(year)
        db.execute('INSERT INTO books (isbn, title, author, year) \
        VALUES(:isbn, :title, :author, :year)',
        {'isbn':isbn, 'title':title, 'author':author, 'year':year})
        print(f'Added {isbn},{title},{author},{year}')
    db.commit()


def main():
    populate()

if __name__ == '__main__':
    main()

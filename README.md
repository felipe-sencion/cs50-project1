GoodReviews platform

The project consists of a platform for reviewing books and an API that allow clients to get data about the books.

Users can create an account and log into the platform. In order to create an account a user must provide an username and a password. Usernames must be unique and passwords must be at least 8 characters long. 

Once the user has entered the platform he/she will see a list of some of the books the site offers. The list contains 50 books and those books might be different each time the user lands in the home page.

Every user has an active session until they log out from the platform.

Users can search for books given an isbn number, author name or title. The search looks for patterns into those fields of a book, thus if the user only writes part of the title the book will still be found.

This project uses Postgresql and sqlalchemy for database managment and python/flask for the backend. The frontend uses bootstrap and CSS.
	

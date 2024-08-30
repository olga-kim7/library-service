LIBRARY SERVICE

Requirements:

Functional (what the system should do): Web-based

Manage books inventory
Manage books borrowing
Manage customers
Display notifications
Handle payments
Non-functional (what the system should deal with):

Support for 5 concurrent users
Handle up to 1000 books
Support 50,000 borrowings per year
Approximate data usage of ~30MB per year
Specific Endpoint Requirements: Payment Endpoint:

Implement an endpoint that makes requests to the Stripe service to handle payments.

Borrowers List Endpoint:

Endpoint takes a search string as an argument and returns a list of current borrowers.

Local Database Integration:

Requests of the implemented API should work with the local database (fetch data from the database, not from the Library API)

Technologies to Use:

Stripe API: Stripe API Documentation
Telegram API: Telegram API Documentation
Celery Beat:
Use Celery Beat as a task scheduler to check all overdue borrowers.
Celery for Asynchronous Requests:
Use Celery to make asynchronous requests to Telegram to notify about each new borrower.
Swagger Documentation:
All endpoints should be documented via Swagger.
How to Run:

Copy .env.sample to .env and populate it with all required data.
Run the following command to build and start the application:
docker-compose up --build

Create an admin user and schedule the synchronization of overdue borrowers.# library-service

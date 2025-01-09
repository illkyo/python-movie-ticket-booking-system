import sqlite3
import os

# Get the directory where the Python script is located
script_dir = os.path.dirname(os.path.abspath(__file__))

# Construct the full path to the sys.db file
db_path = os.path.join(script_dir, "sys.db")

# Connect to SQLite database
conn = sqlite3.connect(db_path)
conn.execute("PRAGMA foreign_keys = ON")

cur = conn.cursor()

# Create Cinemas Table
cur.execute("""
CREATE TABLE IF NOT EXISTS CINEMAS (
    ID INTEGER PRIMARY KEY,
    NAME TEXT,
    CITY TEXT,
    ADDRESS TEXT
)
""")

# Create Screens Table
cur.execute("""
CREATE TABLE IF NOT EXISTS SCREENS (
    SCREEN_NUM INTEGER PRIMARY KEY,
    CINEMA_ID INTEGER NOT NULL,
    FLOOR INTEGER,
    SEATS INTEGER,
    FOREIGN KEY(CINEMA_ID) REFERENCES CINEMAS(ID)
)
""")

# Create Seats Table
cur.execute("""
CREATE TABLE IF NOT EXISTS SEATS (
    SEAT_NUM INTEGER PRIMARY KEY,
    CINEMA_ID INTEGER NOT NULL,
    SCREEN INTEGER NOT NULL,
    TYPE TEXT NOT NULL,
    STATUS TEXT,
    FOREIGN KEY(CINEMA_ID) REFERENCES CINEMAS(ID),
    FOREIGN KEY(SCREEN) REFERENCES SCREENS(SCREEN_NUM)
)
""")


# Create User table
cur.execute('''
CREATE TABLE IF NOT EXISTS USERS (
    ID INTEGER PRIMARY KEY,
    FIRST_NAME TEXT NOT NULL,
    LAST_NAME TEXT NOT NULL,
    FULL_NAME TEXT GENERATED ALWAYS AS (FIRST_NAME || ' ' || LAST_NAME) STORED,
    EMAIL TEXT NOT NULL,
    PASSWORD TEXT NOT NULL,
    ROLE TEXT NOT NULL,
    CINEMA_ID INTEGER,
    FOREIGN KEY(CINEMA_ID) REFERENCES CINEMAS(ID)
)
''')

# Create Films Table
cur.execute("""
CREATE TABLE IF NOT EXISTS FILMS (
    ID INTEGER PRIMARY KEY,
    NAME TEXT NOT NULL,
    SYNOPSIS TEXT NOT NULL,
    GENRE TEXT NOT NULL,
    RATING TEXT NOT NULL,
    SCREEN_TIME TEXT NOT NULL,
    CINEMA_ID INTEGER NOT NULL,
    SCREEN INTEGER NOT NULL,
    FOREIGN KEY(CINEMA_ID) REFERENCES CINEMAS(ID),
    FOREIGN KEY(SCREEN) REFERENCES SCREENS(SCREEN_NUM)
)
""")

# Create Bookings Table
cur.execute("""
CREATE TABLE IF NOT EXISTS BOOKINGS (
    REFERENCE TEXT NOT NULL,
    FILM_ID INTEGER NOT NULL,
    BOOK_DATE TEXT NOT NULL,
    SHOW_TIME TEXT NOT NULL,
    TICKET_COUNT INTEGER NOT NULL,
    TOTAL_PRICE REAL NOT NULL,
    CUSTOMER TEXT NOT NULL,
    STAFF_ID INTEGER NOT NULL,
    FOREIGN KEY(FILM_ID) REFERENCES FILMS(ID),
    FOREIGN KEY(STAFF_ID) REFERENCES USERS(ID)
)
""")

# Insert Dummy Cinemas to Cinemas Table
cur.executemany('''
INSERT INTO CINEMAS (ID, NAME, CITY, ADDRESS) VALUES (?, ?, ?, ?)
''', [
    (180, 'Horizon Colin', 'Birmingham', 'Downing Street'),
    (250, 'Horizon Supreme', 'Bristol', 'Worchester Road'),
    (350, 'Horizons', 'Cardiff', 'Clover Lane'),
    (490, 'Horizon Beckham Cine', 'London', 'Near Wembley')
])

# Insert Dummy Screens to Screens Table
cur.executemany('''
INSERT INTO SCREENS (SCREEN_NUM, CINEMA_ID, FLOOR, SEATS) VALUES (?, ?, ?, ?)
''', [
    (3, 180, 2, 55),
    (5, 180, 1, 120),
    (6, 180, 1, 55),
    (2, 180, 1, 50)
])


# Insert Dummy Seats to Seats Table
cur.executemany('''
INSERT INTO SEATS (SEAT_NUM, CINEMA_ID , SCREEN, TYPE, STATUS) VALUES (?, ?, ?, ?, ?)
''', [
    (114, 180, 5, 'Upper Gallery', 'Reserved'),
    (43, 180, 3, 'Upper Gallery', 'Reserved'),
    (20, 180, 6, 'Lower Hall', 'Unreserved'),
    (14, 180, 2, 'Lower Hall', 'Unreserved')
])

# Initialize a Dummy Superadmin User
id = 1
first_name = 'John'
last_name = 'Smith'
email = 'johnsmith1@gmail.com'
password = '123'
role = 'Admin'
cinema_id = 180

superadmin = (id, first_name, last_name, email, password, role, cinema_id)

# Insert Dummy Users to Users Table
cur.executemany('''
INSERT INTO USERS (ID, FIRST_NAME, LAST_NAME, EMAIL, PASSWORD, ROLE, CINEMA_ID) VALUES (?, ?, ?, ?, ?, ?, ?)
''', [
    superadmin,
    ('2', 'Ellie', 'Walker', 'ellie3@gmail.com', '145', 'Admin', 180),
    ('3', 'Jamal', 'Adams', 'jamlads@gmail.com' ,'213', 'Manager', 180),
    ('4', 'Abdul', 'Kalam', 'kalamid@outlook.com','167', 'Staff', 180),
])

# Insert Dummy Films to Films Table
cur.executemany('''
INSERT INTO FILMS (ID, NAME, SYNOPSIS, GENRE, RATING, SCREEN_TIME, CINEMA_ID, SCREEN) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
''', [
    (1, 'Alien', 'Aliens walk amongst us, We are no longer humans...', 'Sci-Fi', 'PG-13', '2024-07-17 20:00', 180, 3),
    (2, 'Predator', 'Aubrey Drake Graham will show you a real predator', 'Action', 'R', '2024-07-13 21:00', 180, 5),
    (3, 'Interstellar', 'A space movie. A movie set in space. A very spacial movie. Spacious', 'Sci-Fi', 'PG-13', '2024-07-21 18:00', 180, 6)
])

# Insert Dummy Booking to Bookings Table 
# Reference Number where first sequence of digits tells Cinema, next digit Screen, next digit Film ID, next digit Seat Type, next digit Ticket amount
cur.executemany('''
INSERT INTO BOOKINGS (REFERENCE, FILM_ID, BOOK_DATE, SHOW_TIME, TICKET_COUNT, TOTAL_PRICE, CUSTOMER, STAFF_ID) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
''', [
    ('B180-3-1-0-1', 1, '2024-07-04 20:00', '2024-07-17 20:00', 1, 8.4, 'Jack', 4), # Upper Gallery
    ('B180-5-2-0-3', 2, '2024-07-11 20:00', '2024-07-13 21:00', 3, 25.2, 'Mary', 4), # Upper Gallery
    ('B180-6-3-1-1', 3, '2024-07-10 20:00', '2024-07-21 18:00', 1, 7.0, 'Wiley', 4) # Lower Hall
])

conn.commit()
conn.close()

print("Database Setup Successful")
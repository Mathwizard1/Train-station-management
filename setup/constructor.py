import pymysql

# ---------- Configuration ----------
HOST = 'localHOST'        # or your DB HOST
USER = 'root'
PASSWORD = 'pass@123'
DATABASE_NAME = 'TrainMangament'
# DUMP_FILE = ''

# ---------- SQL TABLE Definitions ----------
station_table = """
CREATE TABLE USERs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100),
    email VARCHAR(100) UNIQUE
);
"""
train_table = """
CREATE TABLE USERs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100),
    email VARCHAR(100) UNIQUE
);
"""
schedule_table = """
CREATE TABLE posts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    USER_id INT,
    title VARCHAR(200),
    content TEXT,
    FOREIGN KEY (USER_id) REFERENCES USERs(id)
);
"""

coach_table = """
CREATE TABLE comments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    post_id INT,
    USER_id INT,
    comment TEXT,
    FOREIGN KEY (post_id) REFERENCES posts(id),
    FOREIGN KEY (USER_id) REFERENCES USERs(id)
);
"""
ticket_table = """
CREATE TABLE posts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    USER_id INT,
    title VARCHAR(200),
    content TEXT,
    FOREIGN KEY (USER_id) REFERENCES USERs(id)
);
"""

booking_table = """
CREATE TABLE posts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    USER_id INT,
    title VARCHAR(200),
    content TEXT,
    FOREIGN KEY (USER_id) REFERENCES USERs(id)
);
"""

# ---------- SQL TRIGGER Definitions ----------



# ---------- Connection and Execution ----------
try:
    # Connect to MySQL server (without specifying DB yet)
    connection = pymysql.connect(
        HOST=HOST,
        USER=USER,
        PASSWORD=PASSWORD,
        charset='utf8mb4',
        # autocommit=True,
        cursorclass= pymysql.cursors.DictCursor
    )

    with connection.cursor() as cursor:
        # Create database
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DATABASE_NAME}")
        print(f"Database `{DATABASE_NAME}` created or already exists.")

    # Connect to the newly created database
    connection.select_db(DATABASE_NAME)

    with connection.cursor() as cursor:
        cursor.execute(station_table)
        

        cursor.execute(train_table)
        

        cursor.execute(coach_table)
    

    connection.commit()

except Exception as e:
    print("Error:", e)

finally:
    connection.close()

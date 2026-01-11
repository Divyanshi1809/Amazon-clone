import sqlite3
import os

db_name = "student_records.db"

# Remove existing database to start fresh (optional)
if os.path.exists(db_name):
    os.remove(db_name)
    print(f"✓ Removed existing {db_name}")


# Connect to database
with sqlite3.connect(db_name) as conn:
    print(f"✓ Connected to database: {db_name}")
   
    # Create a cursor to execute SQL commands
    cursor = conn.cursor()
   
    # SQLite data types: INTEGER, REAL, TEXT, BLOB, NULL
    cursor.execute("""
        CREATE TABLE students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            age INTEGER,
            grade TEXT,
            email TEXT
        )
    """)
   
    print("✓ Created 'students' table")
   
    # Commit the changes
    conn.commit()

# Method 1: Insert single record
with sqlite3.connect(db_name) as conn:
    cursor = conn.cursor()
   
    cursor.execute("""
        INSERT INTO students (name, age, grade, email)
        VALUES ('Alice Johnson', 20, 'A', 'alice@example.com')
    """)
   
    print("✓ Inserted 1 student")
    conn.commit()


# Method 2: Using placeholders (RECOMMENDED - prevents SQL injection)
with sqlite3.connect(db_name) as conn:
    cursor = conn.cursor()
   
    # Single insert with placeholders
    cursor.execute("""
        INSERT INTO students (name, age, grade, email)
        VALUES (?, ?, ?, ?)
    """, ('Bob Smith', 19, 'B', 'bob@example.com'))
   
    print("✓ Inserted 1 student using placeholders")
    conn.commit()


# Method 3: Insert multiple records at once
with sqlite3.connect(db_name) as conn:
    cursor = conn.cursor()
   
    students_data = [
        ('Charlie Brown', 21, 'A', 'charlie@example.com'),
        ('Diana Prince', 20, 'B', 'diana@example.com'),
        ('Eve Wilson', 19, 'C', 'eve@example.com'),
    ]
   
    cursor.executemany("""
        INSERT INTO students (name, age, grade, email)
        VALUES (?, ?, ?, ?)
    """, students_data)
   
    print(f"✓ Inserted {len(students_data)} students using executemany()")
    conn.commit()


# Verify the data
with sqlite3.connect(db_name) as conn:
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM students")
    count = cursor.fetchone()[0]
    print(f"✓ Total students in database: {count}\n")


# Basic SELECT - get all records
with sqlite3.connect(db_name) as conn:
    cursor = conn.cursor()
   
    print("\n1. All students:")
    cursor.execute("SELECT * FROM students")
    all_students = cursor.fetchall()
    for student in all_students:
        print(f"   {student}")


# Select specific columns
with sqlite3.connect(db_name) as conn:
    cursor = conn.cursor()
   
    print("\n2. Names and grades only:")
    cursor.execute("SELECT name, grade FROM students")
    for row in cursor.fetchall():
        print(f"   {row[0]} - Grade: {row[1]}")


from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)
db = sqlite3.connect('bug_tracker.db', check_same_thread=False)

def initialize_database():
    cursor = db.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS bugs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            status TEXT NOT NULL,
            assigned_to TEXT NOT NULL
        )
    ''')
    cursor.close()

# Call the database initialization function
initialize_database()


@app.route('/')
def home():
    # Fetch all bugs from the database
    cursor = db.cursor()
    cursor.execute('SELECT * FROM bugs')
    bugs = cursor.fetchall()
    cursor.close()

    return render_template('bug_list.html', bugs=bugs)

@app.route('/bug/create', methods=['GET', 'POST'])
def create_bug():
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        status = request.form.get('status')
        assigned_to = request.form.get('assigned_to')

        # Insert the bug into the database
        cursor = db.cursor()
        cursor.execute('INSERT INTO bugs (title, description, status, assigned_to) VALUES (?, ?, ?, ?)',
                       (title, description, status, assigned_to))
        db.commit()
        cursor.close()

        return redirect(url_for('home'))
    
    return render_template('create_bug.html')

if __name__ == '__main__':
    app.run(debug=True)

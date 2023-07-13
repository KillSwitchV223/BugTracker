
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
def index():
    return render_template('home.html')

@app.route('/')
def home():
    return render_template('index.html')
    # Fetch all bugs from the database

@app.route('/dashboard')
def dashboard():
    cursor = db.cursor()
    cursor.execute('SELECT * FROM bugs ORDER BY id DESC LIMIT 10')
    bugs = cursor.fetchall()
    cursor.close()
    return render_template('dashboard.html', bugs=bugs)

from werkzeug.utils import secure_filename
import os

# Set the upload folder for attachments
UPLOAD_FOLDER = 'attachments'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Helper function to handle file uploads
def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/bug/create', methods=['GET', 'POST'])
def create_bug():
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        status = request.form.get('status')
        assigned_to = request.form.get('assigned_to')
        priority =  request.form.get('priority')
        category = request.form.get('category')
        attachment = request.files['attachment']


         # Validate and save the attachment file
        if attachment and allowed_file(attachment.filename):
            filename = secure_filename(attachment.filename)
            attachment.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            attachment_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        else:
            attachment_path = None

        # Insert the bug into the database
        cursor = db.cursor()
        cursor.execute('INSERT INTO bugs (title, description, status, assigned_to, priority, category, attachment_path) '
                       'VALUES (?, ?, ?, ?, ?, ?, ?)',
                       (title, description, status, assigned_to, priority, category, attachment_path))
        db.commit()
        cursor.close()

        return redirect(url_for('home'))
    
    return render_template('create_bug.html')


@app.route('/bug/<int:bug_id>')
def view_bug(bug_id):
    # Fetch the bug details from the database
    cursor = db.cursor()
    cursor.execute('SELECT * FROM bugs WHERE id = ?', (bug_id,))
    bug = cursor.fetchone()

    # Fetch comments for the ticket
    cursor.execute('SELECT * FROM ticket_comments WHERE ticket_id = ?', (bug_id,))
    comments = cursor.fetchall()

     # Fetch attachments for the ticket
    cursor.execute('SELECT * FROM ticket_attachments WHERE ticket_id = ?', (bug_id,))
    attachments = cursor.fetchall()

    # Close connection to DB after fetching data
    cursor.close()

    if bug:
        return render_template('bug_details.html', bug=bug, comments=comments, attachments=attachments)
    else:
        return "Bug not found"
    

# Updated route for ticket updates
@app.route('/bug/<int:bug_id>/update', methods=['GET', 'POST'])
def update_bug(bug_id):
    if request.method == 'POST':
        status = request.form.get('status')
        priority = request.form.get('priority')
        category = request.form.get('category')
        assigned_to = request.form.get('assigned_to')

        cursor = db.cursor()
        cursor.execute('UPDATE bugs SET status = ?, priority = ?, category = ?, assigned_to = ? WHERE id = ?',
                       (status, priority, category, assigned_to, bug_id))
        db.commit()
        cursor.close()

        return redirect(url_for('view_bug', bug_id=bug_id))

    cursor = db.cursor()
    cursor.execute('SELECT * FROM bugs WHERE id = ?', (bug_id,))
    bug = cursor.fetchone()
    cursor.close()

    return render_template('update_bug.html', bug=bug)

# Route for ticket deletion
@app.route('/bug/<int:bug_id>/delete', methods=['POST'])
def delete_bug(bug_id):
    cursor = db.cursor()
    cursor.execute('DELETE FROM bugs WHERE id = ?', (bug_id,))
    db.commit()
    cursor.close()

    return redirect(url_for('home'))


if __name__ == '__main__':
    try:
        app.run(debug=True, port=8000)
    except Exception as e:
        print(f"An error occurred: {e}")

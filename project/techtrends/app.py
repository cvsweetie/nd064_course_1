import sqlite3
import logging
import sys

from flask import Flask, jsonify, json, render_template, request, url_for, redirect, flash
from werkzeug.exceptions import abort
from logging.config import dictConfig

db_connection_count = 0
# Function to get a database connection.
# This function connects to database with the name `database.db`
def get_db_connection():
    global db_connection_count
    connection = sqlite3.connect('database.db')
    connection.row_factory = sqlite3.Row
    db_connection_count +=1
    return connection


# Function to get a post using its ID
def get_post(post_id):
    connection = get_db_connection()
    post = connection.execute('SELECT * FROM posts WHERE id = ?',
                        (post_id,)).fetchone()
    connection.close()
    return post

# Define the Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your secret key'

#TEchtrend application healthz and metrics endpoints
@app.route('/healthz')
def healthz():
    try:
        connection = sqlite3.connect('database.db')
        posts = connection.execute('SELECT * FROM posts').fetchall()
        response = app.response_class(response=json.dumps({"result":"OK- Healthy"}),
            status=200,
            mimetype='application/json')
    except sqlite3.Error as error:   
        response = app.response_class(response=json.dumps({"result":"ERROR- UnHealthy"}),
            status=500,
            mimetype='application/json')
    finally:
        if connection:
            connection.close();
    app.logger.info('Healthz request successful')
    return response

@app.route('/metrics')
def metrics():
    connection = get_db_connection()
    posts = connection.execute('SELECT * FROM posts').fetchall()
    connection.close()
    post_count=len(posts)
    response = app.response_class(response=json.dumps({"db_connection_count":db_connection_count , "post_count": post_count}),
            status=200,
            mimetype='application/json')
    app.logger.info('Metrics request successfull')
    return response


# Define the main route of the web application 
@app.route('/')
def index():
    connection = get_db_connection()
    posts = connection.execute('SELECT * FROM posts').fetchall()
    connection.close()
   
    return render_template('index.html', posts=posts)

# Define how each individual article is rendered 
# If the post ID is not found a 404 page is shown
@app.route('/<int:post_id>')
def post(post_id):
    post = get_post(post_id)
    if post is None:
      app.logger.info('Article id %s does not exist!!',post_id)
      return render_template('404.html'), 404
    else:
      app.logger.info('Article %s retrived.', post['title'])
      return render_template('post.html', post=post)

# Define the About Us page
@app.route('/about')
def about():
    app.logger.info('About page  is retrieved.')
    return render_template('about.html')

# Define the post creation functionality 
@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!')
        else:
            connection = get_db_connection()
            connection.execute('INSERT INTO posts (title, content) VALUES (?, ?)',
                         (title, content))
            connection.commit()
            connection.close()
            app.logger.info('Article created: ',title)
            return redirect(url_for('index'))

    return render_template('create.html')

# start the application on port 3111
if __name__ == "__main__":
   logger = logging.getLogger()
   logger.setLevel(logging.DEBUG)
   
   stdout_handler = logging.StreamHandler(sys.stdout)
   stdout_handler.setLevel(logging.DEBUG)

   stderr_handler = logging.StreamHandler(sys.stderr)
   stderr_handler.setLevel(logging.ERROR)
   
   logger.addHandler(stdout_handler)
   logger.addHandler(stderr_handler)

   logging.basicConfig(format='%(levelname)s:%(name)s:%(asctime)s, %(message)s',level=logging.DEBUG,handlers=[stderr_handler, stdout_handler])
   app.run(host='0.0.0.0', port='3111')
# all the imports
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash
from flask import render_template
from points import Points
from tour_result import TourResult
from calendar import Calendar
import json
import os
import sqlite3
import time
from werkzeug import secure_filename



app = Flask(__name__)


app.config.from_object(__name__) # load config from this file , chtk.py

# Load default config and override config from an environment variable
app.config.update(dict(
    UPLOAD_FOLDER_TOUR='static/tours/',
    UPLOAD_FOLDER='static/images/',
    DATABASE=os.path.join(app.root_path, 'chtk.db'),
    SECRET_KEY='development key',
    USERNAME='admin',
    PASSWORD='default'
))
app.config.from_envvar('CHTK_SETTINGS', silent=True)


def connect_db():
    """Connects to the specific database."""
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv


def init_db():
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()


@app.cli.command('initdb')
def initdb_command():
    """Initializes the database."""
    init_db()
    print('Initialized the database.')


def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db


@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()


@app.route('/')
def show_entries():
    db = get_db()
    cur = db.execute('select title, text, date_of_article, images, tour from entries order by id desc')
    entries = cur.fetchall()
    return render_template('show_entries.html', entries=entries)


@app.route('/add', methods=['POST'])
def add_entry():
    if not session.get('logged_in'):
        abort(401)
    db = get_db()
    dt = time.strftime("%d/%m/%Y")
    file = request.files['file']
    tour = request.files['tour']
    if tour:
        filename_tour = secure_filename(tour.filename)
        path_to_file_tour = os.path.join(app.config['UPLOAD_FOLDER_TOUR'], filename_tour)
        tour.save(os.path.join(app.config['UPLOAD_FOLDER_TOUR'], filename_tour))
    else:
        path_to_file_tour = None
    if file:
        filename = secure_filename(file.filename)
        path_to_file = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    else:
        path_to_file = None
    db.execute('insert into entries (title, text, date_of_article, images, tour) values (?, ?, ?, ?, ?)',
                 [request.form['title'], request.form['text'], dt, path_to_file, path_to_file_tour])
    db.commit()
    flash('New entry was successfully posted')
    return redirect(url_for('show_entries'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            error = 'Invalid username'
        elif request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            flash('You were logged in')
            return redirect(url_for('show_entries'))
    return render_template('login.html', error=error)


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('show_entries'))


f = open('new_list_2.txt', 'r')
json_string = f.readline()
parsed_string = json.loads(json_string)
points = Points()
tour_result = TourResult(parsed_string)
f.close()
#calendar = Calendar()


def rating_show(parsed_string):
    new_list = []
    rating = {}
    for el in parsed_string:
        s = 1
        points_1 = 0
        while ('Турнир_' + str(s)) in el:
            points_1 += int(el['Турнир_' + str(s)])
            s += 1
        rating.update({el['Фамилия'] + ' ' + el['Имя']: points_1})
    while rating:
        for key, el in rating.items():
            if el == max(rating.values()):
                new_list.append([key, el])
                rating.pop(key)
                break
    return new_list


def number_of_tournaments():
    return len(parsed_string[0])-2


@app.route('/base.html')
@app.route('/')
def show_method():

    return render_template("base.html", number=number_of_tournaments())


@app.route('/rating/')
def show_method_2():
    peremen = rating_show(parsed_string)
    counter = 1
    return render_template("rating.html", peremen=peremen, counter=counter)


@app.route('/tour/')
def pick_num_tour():
    return render_template('picktour.html')


@app.route('/tour/<int:tour_id>/')
def shopping(tour_id):
    num_tour = tour_result.tour_result(tour_id)
    date = Calendar()
    date = date.get_date(tour_id)
    return render_template("tour.html", num_tour=num_tour, tour_id=tour_id, date=date)


@app.route('/rules/')
def rules():
    return render_template('test.html')


@app.route('/contacts/')
def contacts():
    return render_template('contacts.html')


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')

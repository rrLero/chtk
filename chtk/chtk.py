# -*- coding: utf-8 -*-
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash
from points import Points
from tour_result import TourResult
from mycalendar import MyCalendar
import json
import os
import sqlite3
import time
from werkzeug import secure_filename
from StatsPlayers import StatsPlayers
from flask_admin import Admin
from flask_sqlalchemy import SQLAlchemy
from flask_admin.contrib import sqla
from flask_admin import BaseView, expose


app = Flask(__name__)


app.config.from_object(__name__) # load config from this file , chtk.py
app.config.update(dict(
    UPLOAD_FOLDER_TOUR='static/tours/',
    UPLOAD_FOLDER='static/images/',
    UPLOAD_FOLDER_PLAYERS='static/players/',
    DATABASE=os.path.join(app.root_path, 'chtk.db'),
    SECRET_KEY='development key',
    USERNAME='admin',
    PASSWORD='default',
    SQLALCHEMY_ECHO=True,
    SQLALCHEMY_TRACK_MODIFICATIONS=False

))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + app.config['DATABASE']
app.config.from_envvar('CHTK_SETTINGS', silent=True)

dab = SQLAlchemy(app)


class Entries(dab.Model):
    id = dab.Column(dab.Integer, primary_key=True)
    title = dab.Column(dab.String(100))
    text = dab.Column(dab.String(450))
    date_of_article = dab.Column(dab.String(20))
    images = dab.Column(dab.String(60))
    tour = dab.Column(dab.String(60))

    def __str__(self):
        return self.username


class Players(dab.Model):
    id = dab.Column(dab.Integer, primary_key=True)
    player_name = dab.Column(dab.String(20))
    player_surname = dab.Column(dab.String(20))
    path_photo = dab.Column(dab.String(40))

    def __str__(self):
        return self.username


class MyModelView(sqla.ModelView):

    def is_accessible(self):
        if not session.get('logged_in'):
            return False
        else:
            return True


class AnalyticsView(BaseView):
    @expose('/')
    def index(self):
        return self.render('base.html')


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


@app.route('/<int:page>/', methods=['GET', 'POST'])
@app.route('/')
def show_entries(page=1):
    pagination = Entries.query.order_by(Entries.id.desc()).paginate(page, 3, False)
    db = get_db()
    cur_1 = db.execute('select id, player_name, player_surname, path_photo from players order by id')
    players = cur_1.fetchall()
    return render_template('show_entries.html', players=players, pagination=pagination)


@app.route('/add_photo', methods=['POST'])
def add_photo():
    if not session.get('logged_in'):
        abort(401)
    db = get_db()
    file = request.files['file']
    player_id = request.form['title']
    if file:
        filename = secure_filename(file.filename)
        path_to_file = os.path.join(app.config['UPLOAD_FOLDER_PLAYERS'], filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER_PLAYERS'], filename))
    else:
        path_to_file = None
    db.execute("update players set path_photo = '%s' where id = '%d'" % (path_to_file, int(player_id)))
    db.commit()
    flash('New PHOTO was successfully posted')
    return render_template('player.html', player_id=player_id, players=get_data_players())


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


def rating_show(parsed_string):
    new_list = {}
    counter = 1
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
                new_list[counter] = {'Очки': el, 'Фамилия': key}
                counter += 1
                rating.pop(key)
                break
    return new_list


def get_position(rating):
    for key, el in rating_show(parsed_string).items():
        if el['Очки'] == rating:
            return key


def number_of_tournaments():
    return len(parsed_string[0])-2


def get_data_players():
    db = get_db()
    cur_1 = db.execute('select id, player_name, player_surname, path_photo from players order by id')
    players = cur_1.fetchall()
    return players


def show_method():
    return render_template("base.html", number=number_of_tournaments(), players=get_data_players())


@app.route('/rating/')
def show_method_2():
    peremen = rating_show(parsed_string)
    return render_template("rating.html", peremen=peremen, players=get_data_players())


@app.route('/tour/<int:tour_id>/')
def shopping(tour_id):
    num_tour = tour_result.tour_result(tour_id)
    date = MyCalendar()
    date = date.get_date(tour_id)
    return render_template("tour.html", num_tour=num_tour, tour_id=tour_id, date=date, players=get_data_players())


@app.route('/player/<int:player_id>/')
def player(player_id):
    db = get_db()
    name = db.execute('select player_name from players where id = %d' % player_id)
    name = name.fetchone()
    surname = db.execute('select player_surname from players where id = %d' % player_id)
    surname = surname.fetchone()
    stats = StatsPlayers()
    list_of_player = stats.get_number_of_tours(parsed_string, name[0], surname[0])
    position = get_position(list_of_player[0])
    list_of_player.append(position)
    return render_template("player.html", player_id=player_id, players=get_data_players(), list_of_player=list_of_player)


@app.route('/rules/')
def rules():
    return render_template('test.html', players=get_data_players())


@app.route('/contacts/')
def contacts():
    return render_template('contacts.html', players=get_data_players())


admin = Admin(app, name='chtk', template_mode='bootstrap3')
admin.add_view(MyModelView(Entries, dab.session))
admin.add_view(MyModelView(Players, dab.session))
admin.add_view(AnalyticsView(name='BasePage', endpoint='analytics'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')

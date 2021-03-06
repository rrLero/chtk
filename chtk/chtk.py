# -*- coding: utf-8 -*-
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash
from points import Points
from tour_result import TourResult
from mycalendar import MyCalendar
import json
from flask import jsonify
import os
import os.path as op
import sqlite3
import time
from werkzeug import secure_filename
from StatsPlayers import StatsPlayers
from flask_admin import Admin
from flask_sqlalchemy import SQLAlchemy
from flask_admin.contrib import sqla
from flask_admin import BaseView, expose, form
from jinja2 import Markup
from sqlalchemy.event import listens_for
from flask_cors import CORS, cross_origin

app = Flask(__name__)
CORS(app)


app.config.from_object(__name__) # load config from this file , chtk.py
app.config.update(dict(
    UPLOAD_FOLDER_TOUR='static/tours/',
    UPLOAD_FOLDER='static/images/',
    UPLOAD_FOLDER_PLAYERS='static/players/',
    DATABASE=os.path.join(app.root_path, 'chtk.db'),
    SECRET_KEY='development key',
    USERNAME='rrlero',
    PASSWORD='rrlero',
    SQLALCHEMY_ECHO=True,
    SQLALCHEMY_TRACK_MODIFICATIONS=False

))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + app.config['DATABASE']
app.config.from_envvar('CHTK_SETTINGS', silent=True)

dab = SQLAlchemy(app)


file_path = op.join(op.dirname(__file__), 'static/files')
try:
    os.mkdir(file_path)
except OSError:
    pass


class File(dab.Model):
    id = dab.Column(dab.Integer, primary_key=True)
    name = dab.Column(dab.Unicode(64))
    path = dab.Column(dab.Unicode(128))

    def __unicode__(self):
        return self.name


class Image(dab.Model):
    id = dab.Column(dab.Integer, primary_key=True)
    name = dab.Column(dab.Unicode(64))
    path = dab.Column(dab.Unicode(128))

    def __str__(self):
        return self.name


class Courts(dab.Model):
    id = dab.Column(dab.Integer, primary_key=True)
    name = dab.Column(dab.String(100))
    adress = dab.Column(dab.String(450))
    phones = dab.Column(dab.String(60))
    type = dab.Column(dab.String(60))
    description = dab.Column(dab.String(240))
    path_hoto = dab.Column(dab.Integer, dab.ForeignKey('image.path'))
    path_photo_ = dab.relationship(Image, backref='image_courts')


class Coaches(dab.Model):
    id = dab.Column(dab.Integer, primary_key=True)
    name = dab.Column(dab.String(40))
    surname = dab.Column(dab.String(40))
    phones = dab.Column(dab.String(40))
    description = dab.Column(dab.String(240))
    path_photo = dab.Column(dab.Integer, dab.ForeignKey('image.path'))
    path_photo_ = dab.relationship(Image, backref='image_coaches')


@listens_for(File, 'after_delete')
def del_file(mapper, connection, target):
    if target.path:
        try:
            os.remove(op.join(file_path, target.path))
        except OSError:
            # Don't care if was not deleted because it does not exist
            pass


@listens_for(Image, 'after_delete')
def del_image(mapper, connection, target):
    if target.path:
        # Delete image
        try:
            os.remove(op.join(file_path, target.path))
        except OSError:
            pass

        # Delete thumbnail
        try:
            os.remove(op.join(file_path,
                              form.thumbgen_filename(target.path)))
        except OSError:
            pass


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


class Tournaments(dab.Model):
    id = dab.Column(dab.Integer, primary_key=True)
    path_tour = dab.Column(dab.String(40))

    def __str__(self):
        return self.username


class MyModelView(sqla.ModelView):

    def is_accessible(self):
        if not session.get('logged_in'):
            return False
        else:
            return True


class ImageView(sqla.ModelView):
    def _list_thumbnail(view, context, model, name):
        if not model.path:
            return ''

        return Markup('<img src="/static/files/%s">' % form.thumbgen_filename(model.path))

    column_formatters = {
        'path': _list_thumbnail
    }

    # Alternative way to contribute field is to override it completely.
    # In this case, Flask-Admin won't attempt to merge various parameters for the field.
    form_extra_fields = {
        'path': form.ImageUploadField('Image',
                                      base_path=file_path,
                                      thumbnail_size=(100, 100, True))
    }


class FileView(sqla.ModelView):
    # Override form field to use Flask-Admin FileUploadField
    form_overrides = {
        'path': form.FileUploadField
    }

    # Pass additional parameters to 'path' to FileUploadField constructor
    form_args = {
        'path': {
            'label': 'File',
            'base_path': file_path,
            'allow_overwrite': False
        }
            }


class AnalyticsView(BaseView):
    @expose('/')
    def index(self):
        return self.render('base.html', len_2016=len_2016, len_2017=len_2017)


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


def number_of_tournaments(list_year):
    return len(list_year[0])-2


def rating_show(list_year):
    new_list = {}
    counter = 1
    rating = {}
    for el in list_year:
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


def get_position(rating, list_year):
    for key, el in rating_show(list_year).items():
        if el['Очки'] == rating:
            return key


def get_data_players():
    db = get_db()
    cur_1 = db.execute('select id, player_name, player_surname, path_photo from players order by player_surname')
    players = cur_1.fetchall()
    return players


def show_method():
    return render_template("base.html", number=number_of_tournaments(parsed_string), players=get_data_players())


def get_court():
    court = Courts.query.order_by(Courts.id.desc())
    return court

f = open('new_list_2.txt', 'r')
json_string = f.readline()
parsed_string = json.loads(json_string)
f.close()

f_2017 = open('new_list_2017.txt', 'r')
json_string_new = f_2017.readline()
parsed_string_new = json.loads(json_string_new)
f_2017.close()

points = Points()
tour_result = TourResult(parsed_string)
tour_result_2017 = TourResult(parsed_string_new)

len_2016 = number_of_tournaments(parsed_string)
len_2017 = number_of_tournaments(parsed_string_new)


@app.route('/<int:page>/', methods=['GET', 'POST'])
@app.route('/')
def show_entries(page=1):
    pagination = Entries.query.order_by(Entries.id.desc()).paginate(page, 3, False)
    db = get_db()
    cur_1 = db.execute('select id, player_name, player_surname, path_photo from players order by player_surname')
    players = cur_1.fetchall()
    return render_template('show_entries.html', court=get_court(), players=players, pagination=pagination, len_2016=len_2016, len_2017=len_2017)


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
    return render_template('player.html', player_id=player_id, court=get_court(), players=get_data_players(), len_2016=len_2016, len_2017=len_2017)


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
        db.execute('insert into tournaments (path_tour) values (?)',
                   [path_to_file_tour])
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
    return render_template('login.html', error=error, len_2016=len_2016, len_2017=len_2017, court=get_court(),)


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('show_entries'))


@app.route('/rating/<int:year>/')
def show_method_1(year):
    if year == 2016:
        peremen = rating_show(parsed_string)
        year = 2016
    elif year == 2017:
        peremen = rating_show(parsed_string_new)
        year = 2017
    return render_template("rating.html", peremen=peremen, court=get_court(), players=get_data_players(), year=year, len_2016=len_2016, len_2017=len_2017)


@app.route('/<int:year>/<int:tour_id>/')
def shopping(tour_id, year):
    if year == 2016:
        num_tour = tour_result.tour_result(tour_id)
    elif year == 2017:
        num_tour = tour_result_2017.tour_result(tour_id)
    date = MyCalendar()
    date_2016 = date.get_date(tour_id)
    date_2017 = date.get_date_2017(tour_id)
    # db = get_db()
    # cur = db.execute('select id, path_tour from tournaments order by id')
    # tournaments = cur.fetchall()
    tournaments = Tournaments.query
    return render_template("tour.html", tournaments=tournaments, court=get_court(), num_tour=num_tour, tour_id=tour_id, year=year, date_2016=date_2016, date_2017=date_2017, players=get_data_players(), len_2016=len_2016, len_2017=len_2017)


@app.route('/player/<int:year>/<int:player_id>/')
def player(player_id, year):
    db = get_db()
    name = db.execute('select player_name from players where id = %d' % player_id)
    name = name.fetchone()
    surname = db.execute('select player_surname from players where id = %d' % player_id)
    surname = surname.fetchone()
    stats = StatsPlayers()
    if year == 2017:
        list_of_player = stats.get_number_of_tours(parsed_string_new, name[0], surname[0])
        position = get_position(list_of_player[0], parsed_string_new)
        list_of_player.append(position)
    elif year == 2016:
        list_of_player = stats.get_number_of_tours(parsed_string, name[0], surname[0])
        position = get_position(list_of_player[0], parsed_string)
        list_of_player.append(position)
    return render_template("player.html", player_id=player_id, players=get_data_players(), court=get_court(), list_of_player=list_of_player, len_2016=len_2016, len_2017=len_2017)


@app.route('/rules/')
def rules():
    return render_template('test.html', players=get_data_players(), court=get_court(), len_2016=len_2016, len_2017=len_2017)


@app.route('/contacts/')
def contacts():
    return render_template('contacts.html', players=get_data_players(), court=get_court(), len_2016=len_2016, len_2017=len_2017)


@app.route('/coaches/')
def coaches():
    coach = Coaches.query.order_by(Coaches.id)
    return render_template('coaches.html', coach=coach, court=get_court(),
                           len_2016=len_2016, len_2017=len_2017)


@app.route('/courts/<current_court>/')
def current_courts(current_court):
    return render_template('current_court.html', current_court=current_court, court=get_court(), len_2016=len_2016, len_2017=len_2017)


# new API FOR NEW SITE
@app.route('/api/news')
def api_news():
    page = 1
    pagination = Entries.query.order_by(Entries.id.desc()).paginate(page, 10, False)
    db = get_db()
    cur_1 = db.execute('select id, player_name, player_surname, path_photo from players order by player_surname')
    players = cur_1.fetchall()
    news_list = [{'id': entry.id, 'date': entry.date_of_article, 'title': entry.title,
                       'text': entry.text, 'image': entry.images, 'tour': entry.tour} for entry in pagination.items]
    return jsonify(news_list)


@app.route('/api/courts')
def api_courts():
    courts = get_court()
    result = [{'id': court.id, 'name': court.name, 'adress': court.adress, 'phones': court.phones, 'type': court.type,
               'description': court.description, 'image': court.path_hoto} for court in courts]
    return jsonify(result)


@app.route('/api/rating/<int:year>/')
def api_rating(year):
    players = get_data_players()
    if year == 2016:
        peremen = rating_show(parsed_string)
        year = 2016
    elif year == 2017:
        peremen = rating_show(parsed_string_new)
        year = 2017
    new_array = [{'place': key, 'surname': val['Фамилия'], 'points': val['Очки']} for key, val in peremen.items() if val['Очки'] != 0]
    for array in new_array:
        for player in players:
            if array['surname'] == player[2] + ' ' + player[1]:
                array['id'] = player[0]
    return jsonify(new_array)


@app.route('/api/coaches')
def api_coaches():
    coaches = Coaches.query.order_by(Coaches.id)
    result = [{'id': coach.id, 'name': coach.name, 'surname': coach.surname, 'phones': coach.phones,
               'description': coach.description, 'image': coach.path_photo} for coach in coaches]
    return jsonify(result)


@app.route('/api/player/<int:year>/<int:player_id>/')
def api_player(player_id, year):
    db = get_db()
    name = db.execute('select player_name from players where id = %d' % player_id)
    name = name.fetchone()
    surname = db.execute('select player_surname from players where id = %d' % player_id)
    surname = surname.fetchone()
    stats = StatsPlayers()
    path_photo = db.execute('select path_photo from players where id = %d' % player_id)
    path_photo = path_photo.fetchone()
    if year == 2017:
        list_of_player = stats.get_number_of_tours(parsed_string_new, name[0], surname[0])
        position = get_position(list_of_player[0], parsed_string_new)
        list_of_player.append(position)
        return jsonify({'name': name[0], 'surname': surname[0], 'points': list_of_player[0], 'played': list_of_player[1], 'place1': list_of_player[2], 'place2': list_of_player[3], 'place3': list_of_player[4], 'position': list_of_player[5], 'path_photo': path_photo[0]})
    elif year == 2016:
        list_of_player = stats.get_number_of_tours(parsed_string, name[0], surname[0])
        position = get_position(list_of_player[0], parsed_string)
        list_of_player.append(position)
        return jsonify({'name': name[0], 'surname': surname[0], 'points': list_of_player[0], 'played': list_of_player[1], 'place1': list_of_player[2], 'place2': list_of_player[3], 'place3': list_of_player[4], 'position': list_of_player[5], 'path_photo': path_photo[0]})
    return jsonify([])


admin = Admin(app, name='chtk', template_mode='bootstrap3')
admin.add_view(MyModelView(Entries, dab.session))
admin.add_view(MyModelView(Players, dab.session))
admin.add_view(MyModelView(Tournaments, dab.session))
admin.add_view(ImageView(Image, dab.session))
admin.add_view(FileView(File, dab.session))
admin.add_view(MyModelView(Courts, dab.session))
admin.add_view(MyModelView(Coaches, dab.session))
admin.add_view(AnalyticsView(name='BasePage', endpoint='analytics'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
import os
from collections import Counter

import mysql.connector
from DBcm import UseDatabase, CredentialsError, ConnectionError

from search4web import search4letters
from flask import Flask, render_template, request, session
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'python'
app.idUsuarios = 0

IMG_FOLDER = os.path.join('static','img')
app.config['UPLOAD_FOLDER'] = IMG_FOLDER
app.config['dbconfig'] = {
    'host': '127.0.0.1',
    'user': 'root',
    'password': 'BBDDPython',
    'database': 'search_log',
    'auth_plugin': 'mysql_native_password'
}


@app.route('/')
@app.route('/index')
def index_page() -> 'html':
    current_time = datetime.now().strftime('%H:%M:%S')
    Flask_Logo = os.path.join(app.config['UPLOAD_FOLDER'], 'icono.jpg')
    Flask_Logo2 = os.path.join(app.config['UPLOAD_FOLDER'], 'icono2.ico')
    return render_template('index.html', current_time=current_time, user_image=Flask_Logo, user_image2=Flask_Logo2)

@app.route('/favicon.ico')
def favicon():
    return app.send_static_file('icono2.ico')

@app.route('/login')
def login_page()->'html':
    current_time = datetime.now().strftime('%H:%M:%S')
    Flask_Logo = os.path.join(app.config['UPLOAD_FOLDER'], 'icono.jpg')
    Flask_Logo2 = os.path.join(app.config['UPLOAD_FOLDER'], 'icono2.ico')
    return render_template('login.html', current_time=current_time, the_title='Welcome to search for letters on the web', user_image=Flask_Logo, user_image2=Flask_Logo2)

@app.route('/login', methods=['POST'])
def login():
    user = request.form['Nombre']
    passw = request.form['password']
    logged_in = False
    message = ""

    with UseDatabase(app.config['dbconfig']) as cursor:
        _SQL = """select idUsuarios from usuarios where Nombre = %s and password = %s"""
        cursor.execute(_SQL, (user, passw))
        contents = cursor.fetchall()

        if len(contents) == 1:
            app.idUsuarios = contents[0][0]
            logged_in = True
        elif user == 'anonimo':
            _SQL = """insert into usuarios (Nombre, password) values (%s, %s)"""
            cursor.execute(_SQL, (user, passw))
            _SQL = """select idUsuarios from usuarios where Nombre = %s and password = %s"""
            cursor.execute(_SQL, (user, passw))
            contents = cursor.fetchall()

            app.idUsuarios = contents[0][0]

            _SQL = """insert into visitas (idUsuarios, ContadorVisitas) values (%s, %s)"""
            cursor.execute(_SQL, (app.idUsuarios, 1))

            logged_in = True
        else:
            message = "La identificación del usuario es incorrecta"

    if logged_in:
        session['logged_in'] = True
        current_time = datetime.now().strftime('%H:%M:%S')
        Flask_Logo = os.path.join(app.config['UPLOAD_FOLDER'], 'icono.jpg')
        Flask_Logo2 = os.path.join(app.config['UPLOAD_FOLDER'], 'icono2.ico')
        return render_template('index.html', current_time=current_time, user_image=Flask_Logo, user_image2=Flask_Logo2)
    else:
        return message if message else "La identificación introducida es incorrecta o no existe"



@app.route('/newuser', methods=['POST'])
def createNewUser():
    user = request.form['new_Nombre']
    passw = request.form['new_password']
    message = ""
    print(user)

    with UseDatabase(app.config['dbconfig']) as cursor:
        _SQL = """select idUsuarios from usuarios where Nombre = %s"""
        cursor.execute(_SQL, (user,))
        contents = cursor.fetchall()
        print(len(contents))

        if len(contents) == 0:
            _SQL = """insert into usuarios (Nombre, password) values (%s, %s)"""
            cursor.execute(_SQL, (user, passw))
            _SQL = """select idUsuarios from usuarios where Nombre = %s and password = %s"""
            cursor.execute(_SQL, (user, passw))
            contents = cursor.fetchall()

            app.idUsuarios = contents[0][0]

            _SQL = """insert into visitas (idUsuarios, ContadorVisitas) values (%s, %s)"""
            cursor.execute(_SQL, (app.idUsuarios, 1))

            session['logged_in'] = True
            current_time = datetime.now().strftime('%H:%M:%S')
            Flask_Logo = os.path.join(app.config['UPLOAD_FOLDER'], 'icono.jpg')
            Flask_Logo2 = os.path.join(app.config['UPLOAD_FOLDER'], 'icono2.ico')
            return render_template('index.html', current_time=current_time, user_image=Flask_Logo, user_image2=Flask_Logo2)
        else:
            message = "Este usuario ya está en uso, por favor ingresa un nuevo nombre de usuario"

            return message if message else "Ocurrió un error al crear el usuario"




@app.route('/entry')
def entry_page() -> 'html':
    current_time = datetime.now().strftime('%H:%M:%S')
    Flask_Logo = os.path.join(app.config['UPLOAD_FOLDER'], 'icono.jpg')
    Flask_Logo2 = os.path.join(app.config['UPLOAD_FOLDER'], 'icono2.ico')
    return render_template('index.html', current_time=current_time, user_image=Flask_Logo, user_image2=Flask_Logo2)


@app.route('/search', methods=['POST'])
def do_search() -> str:
    phrase = request.form['phrase']
    letters = request.form['letters']
    title = 'Here are your results: '
    results = str(search4letters(phrase, letters))
    idUsuarios = app.idUsuarios
    with UseDatabase(app.config['dbconfig']) as cursor:
        _SQL = """INSERT INTO log7 (phrase, letters, ip, results, idUsuarios) VALUES (%s, %s, %s, %s, %s)"""
        cursor.execute(_SQL, (request.form['phrase'], request.form['letters'], request.remote_addr, results, idUsuarios))
    # log_request(request, results)
    return render_template('results.html', the_title=title, the_phrase=phrase, the_letters=letters, the_results=results)


@app.route('/viewlog')
def view_the_log() -> str:
    with open('search.log', 'r') as log:
        contents = log.read()
    return contents


def getTopUsers():
    with UseDatabase(app.config['dbconfig']) as cursor:
        _SQL = """SELECT usuarios.Nombre, visitas.ContadorVisitas
                  FROM usuarios
                  JOIN visitas ON usuarios.idUsuarios = visitas.idUsuarios"""
        cursor.execute(_SQL)
        top_users = cursor.fetchall()

    return top_users


def getTopWords():
    with UseDatabase(app.config['dbconfig']) as cursor:
        _SQL = """SELECT phrase FROM log7"""
        cursor.execute(_SQL)
        phrases = [phrase[0] for phrase in cursor.fetchall()]

    words = []
    for phrase in phrases:
        words.extend(phrase.split())

    word_counts = Counter(words)
    top_words = word_counts.items()
    top_words = list(top_words)
    return top_words


@app.route('/stats')
def view_stats():
    try:
        with UseDatabase(app.config['dbconfig']) as cursor:
            n_request = get_total_requests(cursor)
            common_letters = get_common_letters(cursor)
            ip_addr = get_common_ip_addresses(cursor)
            n_request1 = get_user_requests(cursor)
            common_letters1 = get_user_common_letters(cursor)
            ip_addr1 = get_user_ip_addresses(cursor)

        top5Users = getTopUsers()
        n_anonimo = top5Users[0][1]
        top5Users.pop(0)
        top5Users.sort(key=lambda x: x[1], reverse=True)

        top5Words = getTopWords()
        Flask_Logo = os.path.join(app.config['UPLOAD_FOLDER'], 'icon.jpg')
        return render_template('stats.html',
                               the_title='Stats',
                               n_request=n_request,
                               common_letters=common_letters,
                               ip_addr=ip_addr,
                               n_request1=n_request1,
                               common_letters1=common_letters1,
                               ip_addr1=ip_addr1,
                               user_image=Flask_Logo,
                               n_anonimo=n_anonimo,
                               rows=top5Users,
                               words=top5Words
                               )

    except ConnectionError as err:
        print('Is your database switched on? Error:', str(err))

    except CredentialsError as err:
        print('User-id/Password issues -', str(err))

    except Exception as err:
        print("Something went wrong:", str(err))

    return 'No se tienen suficientes estadísticas'


def get_total_requests(cursor):
    _SQL = """select count(*) as total_requests from log7"""
    cursor.execute(_SQL)
    result = cursor.fetchone()
    return result['total_requests']


def get_common_letters(cursor):
    _SQL = """select letters from log7"""
    cursor.execute(_SQL)
    letters = Counter(cursor.fetchall())
    common_letters = letters.most_common()
    return common_letters[0][0][0]


def get_common_ip_addresses(cursor):
    _SQL = """select ip from log7"""
    cursor.execute(_SQL)
    ip = Counter(cursor.fetchall())
    common_ip = ip.most_common()
    return common_ip[0][0][0]


def get_user_requests(cursor):
    _SQL = """select count(*) as user_requests from log7 where idUsuarios = %s"""
    cursor.execute(_SQL, (app.idUsuarios,))
    result = cursor.fetchone()
    return result['user_requests']


def get_user_common_letters(cursor):
    _SQL = """select letters from log7 where idUsuarios = %s"""
    cursor.execute(_SQL, (app.idUsuarios,))
    letters = Counter(cursor.fetchall())
    common_letters = letters.most_common()
    return common_letters[0][0][0]


def get_user_ip_addresses(cursor):
    _SQL = """select ip from log7 where idUsuarios = %s"""
    cursor.execute(_SQL, (app.idUsuarios,))
    ip = Counter(cursor.fetchall())
    common_ip = ip.most_common()
    return common_ip[0][0][0]


@app.route('/logged')
def do_login() -> str:
    session['logged_in'] = True
    return 'You are now logged in.'

@app.route('/logout')
def do_logout() -> str:
    session.pop('logged_in')
    return 'Bye. You are now logged out'

@app.route('/status')
def check_status() -> str:
    if 'logged_in' in session:
        return 'You are currently logged in.'
    return render_template('status.html','You are NOT logged in.')




if __name__ == '__main__':
    # run app in debug mode on port 5000
    app.run(debug=True, port=5000)
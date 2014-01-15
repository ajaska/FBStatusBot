from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash, jsonify
import api, markov_model
from chatterbotapi import ChatterBotFactory, ChatterBotType
from user import User

factory = ChatterBotFactory()

DATABASE = '/tmp/dev.db'
DEBUG = True
SECRET_KEY = 'dev key'
USERNAME = 'admin'
PASSWORD = 'password'
PORT = 8080

app = Flask(__name__)
app.config.from_object(__name__)
#app.config.from_object('SERVER_SETTINGS')

users = {}

@app.route('/')
def front_page():
    if session.get('id'):
        return render_template('chatbot.html', uid=session['id'])
    else:
        return render_template('landing.html')

@app.route('/facebook-login')
def oauth_redirect():
    if session.get('access_token'):
        return session['access_token']['access_token']
        return render_template('chatbot.html')
    else:
        return api.login()

@app.route('/facebook-login/<uniqueid>')
def code_process(uniqueid):
    if 'code' in request.args:
        code = request.args.get('code')
        token = api.getToken(code, uniqueid)
        if api.verifyToken(token):
            users[uniqueid] = User(token, uniqueid)
            session['id'] = uniqueid
        return redirect(url_for('front_page'))
    elif 'error' in request.args:
        raise api.APIError(request.args.get('error_description'))

@app.route('/get-chat-line/<uniqueid>')
def generate_message(uniqueid):
    if not 'id' in session or session['id'] != uniqueid:
        abort(403)
    else:
        return jsonify({"message":users[uniqueid].generateMessage()})

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/token')
def token_zzz():
    return jsonify(session)

@app.route('/random-crap')
def show_list():
    data = g.db.execute('SELECT tanker,shares FROM tankers ORDER BY shares DESC, tanker ASC').fetchall()
    entries = []
    for row in data:
        entries.append( dict(tanker=row[0], shares=row[1]))
    data = g.db.execute('SELECT tanker FROM tankers ORDER BY tanker ASC').fetchall()
    entries2 = []
    for row in data:
        entries2.append( dict(tanker=row[0]))
    
    shares = sum([x['shares'] for x in entries])
    return render_template('show_entries.html', entries=entries, entries2=entries2,shares=shares)

@app.route('/logout')
def logout():
    session.pop('access_token', None)
    flash('You were logged out')
    return redirect(url_for('front_page'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=PORT)

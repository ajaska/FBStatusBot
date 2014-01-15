from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash, jsonify
import api
from user import User

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

@app.route('/logout')
def logout():
    session.pop('access_token', None)
    flash('You were logged out')
    return redirect(url_for('front_page'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=PORT)

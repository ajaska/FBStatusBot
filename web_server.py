from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash, jsonify
import api, markov_model
from chatterbotapi import ChatterBotFactory, ChatterBotType

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

myturn = {}
model = {}
lastmessage= {}
botsession = {}

@app.route('/')
def front_page():
    if session.get('access_token'):
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
            session['access_token'] = token
            session['id'] = uniqueid
            session['name'] = api.getFirstName(token)
        return redirect(url_for('front_page'))
    elif 'error' in request.args:
        raise api.APIError(request.args.get('error_description'))

@app.route('/get-chat-line/<uniqueid>')
def generate_message(uniqueid):
    if not 'id' in session or session['id'] != uniqueid:
        abort(403)
    else:
        if not uniqueid in model:
            statuses = api.getAllStatuses(session['access_token'])
            markov = markov_model.generateMarkovMap(statuses)
            model[uniqueid] = lambda: markov_model.generateStatus(markov, statuses)
        if not uniqueid in myturn:
            myturn[uniqueid] = True
        if not uniqueid in botsession:
            botsession[uniqueid] = factory.create(ChatterBotType.CLEVERBOT).create_session()
        if not uniqueid in lastmessage:
            lastmessage[uniqueid] = 'Hi'

        if myturn[uniqueid]:
            myturn[uniqueid] = not myturn[uniqueid]
            message = markov_model.makeSimilarStatus(lastmessage[uniqueid], model[uniqueid])
            lastmessage[uniqueid] = message
            return jsonify({"message":session['name']+ ": " + message})
        else:
            myturn[uniqueid] = not myturn[uniqueid]
            message =  botsession[uniqueid].think(lastmessage[uniqueid])
            lastmessage[uniqueid] = message
            return jsonify({"message":"Cleverbot: "+  message})

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

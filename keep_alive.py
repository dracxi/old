from flask import Flask, render_template, request, redirect, url_for, session
from threading import Thread
app = Flask(__name__, static_folder="static")

@app.route('/')
def main():
  return render_template('index.html')


def run():
  app.run(host="0.0.0.0", port=8080)


def keep_alive():
  server = Thread(target=run)
  server.start()
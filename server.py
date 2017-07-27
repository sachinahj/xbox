import json
import hashlib
import requests
from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask, render_template, redirect, request
from friends import Friends

app = Flask(__name__, template_folder='.')
sched = BackgroundScheduler()
friends = Friends()

@app.route("/")
def index():
    return render_template('index.html')

@app.route("/friends")
def get_friends():
    return json.dumps([friend.dump() for friend in friends.gold()])

@app.route("/follow", methods = ['POST'])
def follow_friends():
    secret = request.headers.get("S-AUTH", "")
    if hashlib.sha224(secret.encode('utf-8')).hexdigest() == "66de1a3afbebba2648fb742e0385e4e998d354aab823e2bcd2f6a2e0":
        follow_list = request.form.getlist('friend[]')
        friends.follow(follow_list)
        return ('', requests.codes.ok)
    else:
        return ('', requests.codes.unauthorized)
if __name__ == '__main__':
    friends.populate()
    friends.notify()

    @sched.scheduled_job('cron', minute="*")
    def notify():
        friends.notify()

    @sched.scheduled_job('cron', hour="*", minute=5)
    def populate():
        friends.populate()

    sched.start()

    app.run(host = '0.0.0.0', port = 3000)

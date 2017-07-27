import json
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
    return json.dumps([friend.dump() for friend in friends.get_gold()])

@app.route("/follow", methods = ['POST'])
def follow_friends():
    follow_list = request.form.getlist('friend[]')
    friends.update_follow(follow_list)
    return redirect("/")

if __name__ == '__main__':
    friends.notify()

    @sched.scheduled_job('cron', hour="*", minute="5")
    def populate():
        friends.populate()

    sched.start()

    app.run(host = '0.0.0.0', port = 3000, threaded=True)

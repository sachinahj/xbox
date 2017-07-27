import config

XUID = config.xuid
HEADERS = {'X-AUTH': config.xboxApiToken}

import json
import requests
from flask import Flask, render_template, redirect, request
from friends import Friends

response = requests.get("https://xboxapi.com/v2/accountxuid", headers=HEADERS)
me_raw = json.loads(response.content)
me_raw["id"] = me_raw["xuid"]
me_raw["Gamertag"] = me_raw["gamertag"]
me_raw["AccountTier"] = "Gold"

response = requests.get("https://xboxapi.com/v2/{}/friends".format(XUID), headers=HEADERS)
friends_raw = json.loads(response.content)
friends = Friends(me_raw, friends_raw)

app = Flask(__name__, template_folder='.')
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
    app.run(host = '0.0.0.0', port = 3000, threaded=True)

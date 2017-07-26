import config

XUID = config.xuid
HEADERS = {'X-AUTH': config.xboxApiToken}

import asyncio
import json
import requests
import threading
from flask import Flask, render_template, redirect, request


response = requests.get("https://xboxapi.com/v2/{}/friends".format(XUID), headers=HEADERS)
allFriends = json.loads(response.content)
goldFriends = list(filter(lambda friend: friend["AccountTier"] == "Gold", allFriends))
friends = list(map(lambda friend: dict([("gamertag", friend["Gamertag"]), ("id", friend["id"]), ("following", False), ("online", False)]), goldFriends))

app = Flask(__name__, template_folder='.')
@app.route("/")
def index():
    return render_template('index.html')

@app.route("/friends")
def get_friends():
    return json.dumps(friends)

@app.route("/follow", methods = ['POST'])
def follow_friends():
    global friends
    follow_list = request.form.getlist('friend[]')
    def follow_update(friend):
        if str(friend["id"]) in follow_list:
            friend.update(following = True)
        else:
            friend.update(following = False, online = False)
        return friend
    friends = list(map(follow_update, friends))
    return redirect("/")

def check():
    global friends
    print("check")
    for friend in friends:
        if (friend["following"] == True):
                print("before", friend)
                response = requests.get("https://xboxapi.com/v2/{}/presence".format(XUID), headers=HEADERS)
                data = json.loads(response.content)
                friend["online"] = True if data["state"] == "Online" else False
                print("updated", friend)


    threading.Timer(5, check).start()


if __name__ == '__main__':
    check()
    app.run(host = '0.0.0.0', port = 3000, threaded=True)

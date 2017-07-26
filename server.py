import config

XUID = config.xuid
HEADERS = {'X-AUTH': config.xboxApiToken}

import json
import requests
from flask import Flask, render_template, redirect, request

response = requests.get("https://xboxapi.com/v2/{}/friends".format(XUID), headers=HEADERS)
allFriends = json.loads(response.content)
goldFriends = list(filter(lambda friend: friend["AccountTier"] == "Gold", allFriends))
friends = list(map(lambda friend: dict([("gamertag", friend["Gamertag"]), ("id", friend["id"]), ("following", False)]), goldFriends))

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
        following = False
        if str(friend["id"]) in follow_list:
            following = True
        friend.update(following = following)
        return friend
    friends = list(map(follow_update, friends))
    return redirect("/")

if __name__ == '__main__':
    app.run(host = '0.0.0.0', port = 3000)


# response = requests.get("https://xboxapi.com/v2/{}/presence".format(XUID), headers=HEADERS)
# data = json.loads(response.content)
# state = data["state"]
# print(type(state))

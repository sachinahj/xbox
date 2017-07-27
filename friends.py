import config
import json
import requests
import threading
from twilio.rest import Client

HEADERS = {'X-AUTH': config.xboxApiToken}
client = Client(config.accountSid, config.authToken)

class Friends:
    def __init__(self, me_raw, friends_raw):
        self.friends = list(map(lambda friend: Friend(friend), friends_raw))
        self.friends.insert(0, Friend(me_raw))

    def get_all(self):
        return self.friends

    def get_gold(self):
        return list(filter(lambda friend: friend.account_tier == "Gold", self.friends))

    def update_follow(self, follow_list):
        def update(friend):
            if str(friend.id) in follow_list:
                friend.following = True
            else:
                friend.following = False
                friend.online = False
            return friend
        self.friends = list(map(update, self.friends))

    def notify(self):

        def text(friend):
            body ="{} is now online!".format(friend.gamertag)
            message = client.messages.create(to="+12252876416", from_="+13237468466", body=body)
            print(body)

        for friend in self.get_gold():
            if (friend.following == True):
                response = requests.get("https://xboxapi.com/v2/{}/presence".format(friend.id), headers=HEADERS)
                if (response.status == 200):
                    presence = json.loads(response.content)
                    online = True if presence["state"] == "Online" else False

                    print("-------------------------", response.headers["X-RateLimit-Remaining"])
                    print("friend:", friend.gamertag)
                    print("presence state:", presence["state"])
                    print("current state:", friend.online)
                    print("online:", online)

                    if (friend.online == False and online):
                        text(friend)

                    friend.online = online

        threading.Timer(60, self.notify).start()

class Friend:
    def __init__(self, friend_raw):
        self.id = friend_raw["id"]
        self.gamertag = friend_raw["Gamertag"]
        self.account_tier = friend_raw["AccountTier"]
        self.following = False
        self.online = None

    def dump(self):
        return {
            "id": self.id,
            "gamertag": self.gamertag,
            "following": self.following,
        }

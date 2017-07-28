import config
import json
import requests
from twilio.rest import Client

XUID = config.xbox_xuid
HEADERS = {'X-AUTH': config.xbox_api_token}
client = Client(config.twilio_account_sid, config.twilio_auth_token)

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
            "online": self.online,
        }

class Friends:
    def __init__(self):
        self.friends = []

    def populate(self):
        print("populating!")
        response = requests.get("https://xboxapi.com/v2/accountxuid", headers=HEADERS)
        if response.status_code == requests.codes.ok:
            me_raw = json.loads(response.content)
            me_raw["id"] = me_raw["xuid"]
            me_raw["Gamertag"] = me_raw["gamertag"]
            me_raw["AccountTier"] = "Gold"

            response = requests.get("https://xboxapi.com/v2/{}/friends".format(XUID), headers=HEADERS)
            if response.status_code == requests.codes.ok:
                friends_raw = json.loads(response.content)

                follow_list = list(map(lambda friend: friend.id, filter(lambda friend: friend.following == True, self.friends)))
                print("follow_list", follow_list)

                def fn(friend):
                    f = Friend(friend)
                    if f.id in follow_list:
                        f.following = True
                    return f

                friends_raw.insert(0, me_raw)
                self.friends = list(map(fn, friends_raw))
                print("succesfully done populating!")

    def all(self):
        return self.friends

    def gold(self):
        return list(filter(lambda friend: friend.account_tier == "Gold", self.friends))

    def follow(self, follow_list):
        def update(friend):
            if str(friend.id) in follow_list:
                friend.following = True
            else:
                friend.following = False
                friend.online = False
            return friend
        self.friends = list(map(update, self.friends))

    def notify(self):
        print("notifying!")

        def text(friend):
            body ="{} is now online!".format(friend.gamertag)
            message = client.messages.create(to=config.twilio_phone_to, from_=config.twilio_phone_from, body=body)
            print(body)

        for friend in self.gold():
            if (friend.following == True):
                response = requests.get("https://xboxapi.com/v2/{}/presence".format(friend.id), headers=HEADERS)
                if response.status_code == requests.codes.ok:
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

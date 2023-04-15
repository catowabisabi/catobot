from    app                 import bcrypt, db
from    app.models.models   import User
import  json

from app.services.service_utilities import CommonFunctions


class AppFormater:
    def __init__(self) -> None:
        pass

    def quick_format():
        db.create_all()

    def create_new_user(_user):
        
        username    = _user['username']
        nickname    = _user['nickname']
        email       = _user['email']
        password    = bcrypt.generate_password_hash(_user['password'])
        avatar_url  = _user['avatar_img_url']
        user        = User(username = username, email = email, password =  password, nickname = nickname, avatar_img = avatar_url)
        db.session.add(user)
        db.session.commit()
    
    #def start_new_db_with_template_info(self):

    def create_api_for_user(_user, api):

        CommonFunctions.create_api_to_db(api, _user)

        

class CreateNew:
    def __init__(self):
        self.user1 = {  "username"      : "enomars",
                        "nickname"      : "貓咪神",
                        "email"         : "abcss@gmail.com",
                        "password"      : "123456ssabc",
                        "avatar_img_url": "/static/asset/avatar_4.jpg"}

        self.user2 = {  "username"      : "foxster",
                        "nickname"      : "foxster",
                        "email"         : "foxss8@gmail.com",
                        "password"      : "123456abc",
                        "avatar_img_url": "/static/asset/avatar_3.jpg"}

        self.users = [self.user1, self.user2]

    #AppFormater.quick_format()

    def create_user(self):
        for user in self.users:
            try:
                self.user = AppFormater.create_new_user(user)
            except Exception as e:
                print(e)
    
    def create_api(self):
        api_data ={
        "api_name"          :   "CatoBot Test",
        "exchange"          :   "OKX",
        "api_key"           :   "xxx",
        "api_secret"        :   "yyy",
        "api_password"      :   "CatoBotLcfzzz!",
        "signal_password"   :   "vvv",
        "username"          :   "bbb",
        "robot_id"          :   "rrr"
        }
        api  = CommonFunctions.create_api_obj(api_data)
        user = User.query.filter_by(username = api_data["username"]).first()
        CommonFunctions.create_api_to_db(api, user)
import      configparser
#import      ccxt
import      logging
#from        flask import Flask
#from        flask import request, abort
import      json
import      urllib.request
import      requests
import      os 
import      _thread
import      time
from        datetime    import datetime
import      config.config as config
import      ast 
import      ccxt
import      pandas      as      pd

from app                             import app, bcrypt, db
from flask                           import request, render_template, flash, redirect, url_for
from flask_login                     import login_user, login_required, current_user, logout_user
from app.models.models               import User, Post, Api
from app.forms                       import EditProfileForm, PasswordResetForm, RegisterForm, LoginForm, ResetPasswordForm, PostTweetForm, UploadPhotoForm, SetApiForm, GenSignalForm
from app.services.service_email      import send_reset_password_token

from werkzeug.utils                  import secure_filename
import os
from datetime                        import datetime
import json
import yaml

#================================================================inport services
from app.services.service_gen_signal                  import GenSignalJson
from app.services.service_robot_1      import *
from app.services.service_sizer      import *
from app.services.service_trade      import TradeService
from app.services.service_utilities  import CommonFunctions
from app.services.service_follower   import Follower
from app.services.service_user_info  import UserInfo

from pprint import pprint

#================================================================import flask function and basic app function
from app                             import app, bcrypt, db
from flask                           import request, render_template, flash, redirect, url_for
from flask_login                     import login_required, current_user, logout_user
from app.forms                       import EditProfileForm, PasswordResetForm, RegisterForm, LoginForm, ResetPasswordForm, PostTweetForm, UploadPhotoForm, SetApiForm, GenSignalForm


#================================================================import services
from app.services.service_gen_signal import GenSignalJson
from app.services.service_robot_1    import *
from app.services.service_sizer      import *
from app.services.service_utilities  import CommonFunctions
from app.services.service_follower   import Follower
from app.services.service_user_info  import UserInfo
from app.service_db.db_function      import DataBaseFunctions

from app.my_routes.routes_test       import *
from app.my_routes.routes_webhook     import *

web_title = "CATOBOT WEBHOOK 機器人 V0.01"

#===================================================== 註冊
@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        flash (f'你已經登入! 歡迎使用Catobot交易機器人!', category='info')
        print (f"\n 用戶已經登入: \n\n")
        return redirect(url_for('index'))
    form            = RegisterForm()

    if form.validate_on_submit():
        username, email, password = DataBaseFunctions.reg_new_user(form=form)
        flash('成功註冊', category='success')
        print (f"\n 成功註冊新的用戶: \n{username}, {email}, {password}\n")
    
        return redirect(url_for('index'))
    else:
        print (f"\n 註冊出現問題 \n")

    return render_template('register.html', form = form, title = web_title)
#===================================================== 註冊

#===================================================== 登入
@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        flash(f'你已經登入! 歡迎使用Catobot交易機器人!', category='info')
        print (f"\n 用戶已經登入: \n\n")
        return redirect(url_for('index'))

    form = LoginForm()
    if form.validate_on_submit():
        DataBaseFunctions.login(form=form)

    return render_template('login.html', form = form, title = web_title)
#===================================================== 登入

#===================================================== 登入react
@app.route("/login_re", methods=['GET', 'POST'])
def login_re():

    email = request.json["email"]
    password = request.json["password"]
    remember_me = request.json["remember_me"]

    if current_user.is_authenticated:
        return 'You are logged in already!'

    
    if email and password:
        DataBaseFunctions.login_re(email, password, remember_me)

        return current_user.username
        
    return 401
#===================================================== 登入react

#===================================================== 登出
@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('login'))
#===================================================== 登出

#===================================================== 忘記密碼
@app.route("/password_reset", methods=['GET', 'POST'])
def password_reset():

    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = PasswordResetForm()
    if form.validate_on_submit():
        DataBaseFunctions.reset_password(form)

    return render_template('password_reset.html', form = form)
#===================================================== 忘記密碼

#===================================================== 更改密碼
@app.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = ResetPasswordForm()
    if form.validate_on_submit():
        DataBaseFunctions.actually_change_password(form, token)

    return render_template('reset_password.html', form = form)
#===================================================== 更改密碼
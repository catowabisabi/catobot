#================================================================import flask function and basic app function
from app                             import app
from flask                           import flash, render_template, redirect, url_for
from flask_login                     import login_required, current_user
from app.forms                       import PostTweetForm, SetApiForm, UploadPhotoForm, EditProfileForm, GenSignalForm

from app.service_db.db_function      import DataBaseFunctions
from app.services.service_utilities  import CommonFunctions

user_db = DataBaseFunctions(current_user)
web_title                = "CATOBOT WEBHOOK 機器人 V0.01"
#===================================================關注
@app.route("/follow/<username>")
@login_required
def follow(username):
    user_db.follow_user(username)

#===================================================關注

#===================================================取消關注
@app.route("/unfollow/<username>")
@login_required
def unfollow(username):
    user_db.unfollow_user(username)
#===================================================取消關注    

#===================================================== 發送文字的form
@app.route("/msg", methods=['GET', 'POST'])
@login_required
def msg():
    form  = PostTweetForm()
    if form.validate_on_submit():
        if current_user.is_authenticated:
            user_db.send_msg(form)
            flash('新的文章已經加入', category = 'success')
        else:
            print(f"你沒有登入")
    
    return render_template('msg.html', title = web_title, form = form)
#===================================================== 發送文字的form

#===================================================修改用戶資料
@app.route("/edit_profile", methods=['GET', 'POST'])
@login_required
def edit_profile():
    form                = UploadPhotoForm()
    edit_profile_form   = EditProfileForm()

    if form.validate_on_submit():
       user_db.change_avatar(form)
        
    if edit_profile_form.validate_on_submit():
        user_db.edit_nickname(edit_profile_form)

    return render_template('edit_profile.html', form = form, form2 = edit_profile_form)

#===================================================修改用戶資料

#===================================================設定 API 資料
@app.route("/set_api", methods=['GET', 'POST'])
@login_required
def set_api():
    form = SetApiForm()
    if form.validate_on_submit():
        api  = CommonFunctions.create_api_obj(form)
        CommonFunctions.create_api_to_db(api)
        return redirect(url_for('index', username = current_user.username))
 
    return render_template('set_api.html', form = form)
#===================================================設定 API 資料

#===================================================Gen_Signal
@app.route("/gen_signal", methods=['GET', 'POST'])
@login_required
def gen_signal():
    description = None
    form        = GenSignalForm()
    if form.validate_on_submit():
        user_db.gen_api(form)
       
    return render_template('common_form.html', title = web_title, form = form, description = description)
#===================================================Gen_Signal


#================================================================測試
@app.route("/test_layout", methods=['GET', 'POST'])
@login_required
def test_layout():
    return render_template('test_bootsnipp.html')
#================================================================測試
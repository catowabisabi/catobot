import email
from flask_wtf              import FlaskForm, RecaptchaField
from wtforms                import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, FloatField, IntegerField
from flask_wtf.file         import FileField, FileRequired
from wtforms.validators     import DataRequired, Length, Email, EqualTo, ValidationError

from app.models.models      import User

class RegisterForm(FlaskForm):

    username    = StringField   ('用戶ID',      validators=[DataRequired(), Length(min=6, max=30)])
    email       = StringField   ('電郵',        validators=[DataRequired(), Email()])
    password    = PasswordField ('密碼',        validators=[DataRequired(), Length(min=6, max=30)])
    confirm     = PasswordField ('再次輸入密碼', validators=[DataRequired(), EqualTo('password')])
    #recaptcha   = RecaptchaField()
    submit      = SubmitField   ('注冊')

    def validate_username(self, username):
        user = User.query.filter_by(username= username.data).first()
        if user:
            raise ValidationError('用戶ID已經被使用了!')
    
    def validate_email(self, email):
        user = User.query.filter_by(email= email.data).first()
        if user:
            raise ValidationError('電郵已經被使用了!')

class LoginForm(FlaskForm):

    username    = StringField   ('用戶ID',      validators=[DataRequired(), Length(min=6, max=30)])
    password    = PasswordField ('密碼',        validators=[DataRequired(), Length(min=6, max=30)])
    remember_me = BooleanField  ('記住我')
    #recaptcha   = RecaptchaField()
    submit      = SubmitField   ('登入')

    
class PasswordResetForm(FlaskForm):
    email       = StringField   ('電郵',        validators=[DataRequired(), Email()])
    submit      = SubmitField   ('找回密碼')
    
    def validate_email(self, email):
        email = User.query.filter_by(email= email.data).first()
        if not email:
            raise ValidationError('沒有找到使用這電郵註冊的使用者。')


class ResetPasswordForm(FlaskForm):

    password    = PasswordField ('密碼',        validators=[DataRequired(), Length(min=6, max=30)])
    confirm     = PasswordField ('再次輸入密碼', validators=[DataRequired(), EqualTo('password')])

    submit      = SubmitField   ('重設密碼')


class PostTweetForm(FlaskForm):


    body        = TextAreaField   ('輸入內容',      validators=[DataRequired(), Length(min=1, max=140)])
    submit      = SubmitField     ('發送內容')



class UploadPhotoForm(FlaskForm):

    photo       = FileField         ('個人頭像', validators = [FileRequired()])
    submit      = SubmitField       ('更改個人頭像')

class EditProfileForm(FlaskForm):

    nickname    = StringField   ('用戶暱稱',      validators=[DataRequired(), Length(min=2, max=30)])
    submit      = SubmitField   ('更改')


class SetApiForm(FlaskForm):

    api_name        = StringField   ('API 名稱',                validators=[DataRequired(), Length(min=1, max=30)])
    exchange        = StringField   ('交易所',                  validators=[DataRequired(), Length(min=1, max=30)])
    api_key         = StringField   ('API KEY',                 validators=[DataRequired(), Length(min=6, max=120)])
    api_secret      = StringField   ('API SECRET',              validators=[DataRequired(), Length(min=6, max=120)])
    api_password    = StringField   ('API 密碼 (OKX專用)',       validators=[                Length(min=6, max=120)])
    signal_password = StringField   ('訊號自定密碼',              validators=[DataRequired(), Length(min=6, max=30)])
       
    
    #recaptcha   = RecaptchaField()
    submit          = SubmitField   ('提交')

    #def validate_username(self, username):
    #    user = User.query.filter_by(username= username.data).first()
    #    if user:
    #        raise ValidationError('用戶ID已經被使用了!')
    
    #def validate_email(self, email):
    #    user = User.query.filter_by(email= email.data).first()
    #    if user:
    #        raise ValidationError('電郵已經被使用了!')


class GenSignalForm(FlaskForm):

    strategy            = StringField   ('策略名字',                        validators=[DataRequired(), Length(min=2, max=20)])
    api_id              = IntegerField  ('選擇API',                         validators=[DataRequired()])
    use_perc_tp         = BooleanField  ('在下單時 使用 百份比止盈單 掛單',          )
    tp_perc             = StringField   ('止盈百份比, 1.0 = 1.0 %',             validators=[DataRequired()])
    use_perc_sl         = BooleanField  ('在下單時 使用 百份比止損單 掛單',          )
    sl_perc             = StringField   ('止損百份比, 1.0 = 1.0 %',             validators=[DataRequired()])
    tdMode              = StringField   ('逐倉/全倉',                           validators=[DataRequired()])
    lever               = IntegerField  ('下單槓桿倍數',                        validators=[DataRequired()])
    market_or_limit     = StringField   ('巿價/限價',                           validators=[DataRequired()])
    remarks             = StringField   ('策略注解',                               validators=[Length(max=100)])
    #recaptcha          = RecaptchaField()
    submit              = SubmitField   ('生産 Tradingview Webhook 訊號')
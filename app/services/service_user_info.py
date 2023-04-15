from app.models.models import Api



class UserInfo:
    def __init__(self, user):
        self.user = user
        self.APIs = Api.query.filter_by(user_id = user.id).order_by(Api.api_created_timestamp.desc()).all()

    def get_list_of_created_date_of_APIs(self):
        created_date = []
        for i in range (len(self.APIs)):
            created_date.append(self.APIs[i].api_created_timestamp)
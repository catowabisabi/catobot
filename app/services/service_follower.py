


class Follower:
    def __init__(self, user):
        self.user = user

    def get_number_of_followers(self):
        num_followers = len(self.user.followers)
        num_followed  = len(self.user.followed)
        return [num_followers, num_followed]
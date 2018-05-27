from django.db import models


class SubscribedUser(models.Model):
    user_psid = models.CharField(max_length=22, primary_key=True)


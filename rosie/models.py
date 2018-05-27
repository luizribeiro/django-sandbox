from django.db import models
from typing import List


class SubscribedUser(models.Model):
    user_psid = models.CharField(max_length=22, primary_key=True)

    @classmethod
    def get_all_subscribers(cls) -> List['SubscribedUser']:
        # pyre-fixme[16]: can't use .objects on Django models with pyre
        return cls.objects.all()


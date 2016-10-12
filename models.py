from django.db import models
from django.contrib.auth.models import User as DjUser
# Create your models here.

class User(models.Model):
    user=models.OneToOneField(DjUser)
    img=models.CharField(max_length = 600)


    def __str__(self):  # __unicode__ on Python 2
     return "%s" % (self.user)



class Update(models.Model):
    text=models.CharField(max_length=250)
    created_on=models.DateTimeField(auto_now_add=True)
    user=models.ForeignKey(User)
    #in_reply_to=models.ForeignKey("self",null=True)


class Follows(models.Model):
    user=models.ForeignKey(User,related_name="followsUser")
    follows=models.ForeignKey(User,related_name="followsFollows")

class Likes(models.Model):
    user=models.ForeignKey(User)
    update=models.ForeignKey(Update)
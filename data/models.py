from django.db import models
import uuid


class User(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, primary_key=True)
    name = models.CharField(max_length=200)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20)
    year = models.CharField(max_length=20)
    department = models.CharField(max_length=100, null=True)
    section = models.CharField(max_length=5, null=True)
    reg = models.CharField(max_length=100, null=True)
    college = models.CharField(null=True)
    admin_user = models.BooleanField(default=False)
    attendance = models.BooleanField(default=False)


class Payment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    email = models.EmailField(unique=True)
    is_paid = models.BooleanField(default=False)
    order_id = models.CharField(max_length=500, blank=True)
    payment_id = models.CharField(max_length=500, blank=True)
    instamojo_response = models.TextField(null=True, blank=True)


class UserEvents(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    email = models.EmailField(unique=True)
    event_status = models.CharField()


class TeamEvents(models.Model):
    event_name = models.CharField(max_length=100)
    team_name = models.CharField(max_length=200)
    team = models.ManyToManyField(User)
    team_key = models.CharField(max_length=30)

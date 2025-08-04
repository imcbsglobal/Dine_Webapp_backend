from django.db import models

class AccUsers(models.Model):
    id = models.CharField(max_length=30, primary_key=True)
    pass_field = models.CharField(max_length=100, db_column='pass')  # 'pass' is reserved in Python

    class Meta:
        db_table = 'acc_users'

    def __str__(self):
        return self.id

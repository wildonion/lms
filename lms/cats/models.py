from django.db import models



class Cat(models.Model):
    cat = models.CharField(max_length=200, unique=True)

    def __str__(self):
        return self.cat

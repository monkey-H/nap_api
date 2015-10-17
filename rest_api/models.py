from django.db import models


class Service(models.Model):
    '''
    model for users' service in nap
    '''
    created = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=100)
    origin_url = models.CharField(max_length=200)
    instance_num = models.PositiveSmallIntegerField(default=0)
    owner = models.ForeignKey('auth.User', related_name='services')

    class Meta:
        ordering = ('created',)

class App(models.Model):
    '''
    model for users' app in nap
    '''
    created = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=100)
    ip = models.GenericIPAddressField()
    port = models.PositiveSmallIntegerField(default=0)
    cat = models.TextField()
    state = models.CharField(max_length=100)
    sub = models.CharField(max_length=100)
    journal = models.TextField()
    owner = models.ForeignKey('auth.User', related_name='apps')
    service = models.ForeignKey(Service,related_name='app')

    class Meta:
        ordering = ('created',)

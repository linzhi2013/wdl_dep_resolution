from django.db import models
import os

# Create your models here.
def get_upload_path(instance, filename):
    # should not use settings.media_root in this join
    return os.path.join('repo', instance.name, filename)

class Package(models.Model):
    name = models.CharField(max_length=50)
    version = models.CharField(max_length=10)
    deps = models.CharField(max_length=1000)
    file = models.FileField(upload_to=get_upload_path)
    author = models.CharField(max_length=100)
    project_url = models.CharField(max_length=500)
    description = models.TextField()


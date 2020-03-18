from haystack import indexes
from pipeline.models import Package, PkgFile
import subprocess
import os
import glob

class PackageIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    name = indexes.CharField(model_attr='name')
    author = indexes.CharField(model_attr='author')
    description = indexes.CharField(model_attr='description')
    file = indexes.CharField(model_attr='file')

    def get_model(self):
        return Package

    def index_queryset(self, using=None):
        """Used when the entire index for model is updated."""
        return self.get_model().objects.all()



class PkgFileIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    file_path = indexes.CharField(model_attr='file_path')
    content = indexes.CharField(model_attr='content')

    def get_model(self):
        return PkgFile

    def index_queryset(self, using=None):
        """Used when the entire index for model is updated."""
        return self.get_model().objects.all()












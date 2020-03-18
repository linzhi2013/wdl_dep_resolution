from django.urls import path,include

from . import views

urlpatterns = [
    path('search/', include('haystack.urls'), name='search_view'),
    path('', views.index, name='index'),
    path('upload/', views.upload_file, name='upload'),
    path('<int:pkg_id>/', views.pkg_detail, name='pkg_detail'),
    path('download/<int:pkg_id>/', views.download_pkg, name='download_pkg'),
    path('metadata/', views.download_metadata_file, name='metadata_file'),
]
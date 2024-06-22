from django.contrib import admin
from django.urls import path, include
from .settings import DEBUG

urlpatterns = [
    path('admin/', admin.site.urls),
]

if DEBUG:
    urlpatterns += [
        path('debug/', include('debug_toolbar.urls')),
    ]

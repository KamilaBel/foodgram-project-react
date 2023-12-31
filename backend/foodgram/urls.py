from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('users.urls')),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),

    path('', include('recipes.urls')),
]

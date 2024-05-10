from django.conf.urls.static import static
from django.contrib import admin
from django.template.defaulttags import url
from django.urls import path, include

from diploma import settings

from my_cloud.views import issue_token, issue_link_generation, issue_link_download, front

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/logon', issue_token),
    path('api/link-generation', issue_link_generation),
    path('download/<uuid>', issue_link_download),
    path('api/', include('my_cloud.urls')),
    path("", front, name="front")
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


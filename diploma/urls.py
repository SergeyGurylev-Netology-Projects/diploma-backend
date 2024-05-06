from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView

from diploma import settings
# from rest_framework.routers import DefaultRouter

# from my_cloud.views import sample_controller, UserView, FileViewSet, issue_token, home_view, front
from my_cloud.views import issue_token, issue_link_generation, issue_link_download

# r = DefaultRouter()
# r.register('api/users', UserView.as_view())
# r.register('api/users/<pk>', UserView.as_view())
# r.register('files', FileViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    # path('', sample_controller),
    path('api/logon', issue_token),
    path('api/link-generation', issue_link_generation),
    path('download/<uuid>', issue_link_download),
    path('api/', include('my_cloud.urls')),
    # path('', include('my_cloud.urls')),
    # path('media/user_files/', file_download),
    # path('index/', include('frontend.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
# ] + r.urls

import logging

from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.http import HttpResponse
from rest_framework import status
from rest_framework.exceptions import PermissionDenied, ValidationError, AuthenticationFailed
from rest_framework.permissions import IsAuthenticated
from rest_framework.utils import json
from rest_framework.viewsets import ModelViewSet
from rest_framework.authtoken.models import Token

from .models import File, UserSettings
from .permissions import IsOwner, IsSuperuser, IsUserRegistration, IsUserUpdate
from .serializers import UserSerializer, FileSerializer, UserSettingsSerializer, IssueTokenRequestSerializer

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(message)s')
logger = logging.getLogger(__name__)


def log_request(func):
    def wrapper(self, request, *args, **kwargs):
        logger.debug(f"{request.user} {request.method} {request.get_full_path()}")

        try:
            result = func(self, request, *args, **kwargs)
            logger.info(f"{request.user} {request.method} {request.get_full_path()} OK")
            return result
        except (PermissionDenied, ValidationError) as e:
            logger.error(f'{e.status_code} | {e.detail}')
            return HttpResponse(json.dumps({'error': e.detail}, ensure_ascii=False),
                                status=e.status_code,
                                content_type='application/json')
        except (File.DoesNotExist, User.DoesNotExist) as e:
            logger.error(f'{status.HTTP_404_NOT_FOUND} | {e}')
            return HttpResponse(json.dumps({'error': str(e)}),
                                status=status.HTTP_404_NOT_FOUND,
                                content_type='application/json')
        except Exception as e:
            if hasattr(e, 'message'):
                message = e.message
            else:
                message = str(e);

            logger.error(f'{type(e)} {message}')
            return HttpResponse(json.dumps({'error': message}),
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                content_type='application/json')
    return wrapper


def log_issue_link(func):
    def wrapper(request, *callback_args, **callback_kwargs):
        logger.debug(f"{request.user} {request.method} {request.get_full_path()}")

        response = func(request, *callback_args, **callback_kwargs)

        if status.is_success(response.status_code):
            logger.info(f"{request.user} {request.method} {request.get_full_path()} OK")
        else:
            logger.error(f"{response.status_code}")

        return response

    return wrapper


def log_issue_set_request_user(func):
    def wrapper(request, *callback_args, **callback_kwargs):
        token = request.headers.get('Authorization', 'Token None').split()[1]
        if token == 'None':
            pass
            # user = 'AnonymousUser'
        else:
            try:
                token_obj = Token.objects.get(key=token)
                user = token_obj.user
            except Token.DoesNotExist:
                raise AuthenticationFailed("Invalid token")
            request.user = user

        return func(request, *callback_args, **callback_kwargs)

    return wrapper


class CheckInstanceFromDataPermission:

    def check_instance_from_data_permission(self, request, pk=None):
        if pk is not None:
            instance = self.queryset.get(pk=pk)
        else:
            instance = self.get_instance_from_data(request.data)
        if instance:
            self.check_object_permissions(request, instance)
        return instance

    def get_instance_from_data(self, data):
        ModelClass = self.serializer_class.Meta.model
        serializer = self.get_serializer(data=data)
        if serializer.is_valid():
            instance = ModelClass(**serializer.validated_data)
            instance.id = data.get('id')
            return instance
        return None


class UserView(ModelViewSet, CheckInstanceFromDataPermission):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated & IsSuperuser | IsAuthenticated & IsUserUpdate | IsUserRegistration]

    def get_queryset(self):
        request_user = self.request.user
        request_filter = {}

        pk = self.kwargs.get('pk', None)
        if pk is not None:
            request_filter['pk'] = pk

        queryset = self.queryset.filter(**request_filter)
        if not request_user.is_superuser:
            queryset = queryset & self.queryset.filter(id=request_user.id)

        return queryset

    @log_request
    def user_list(self, request, *args, **kwargs):
        return super(UserView, self).list(request, *args, **kwargs)

    @log_request
    def user_create(self, request, *args, **kwargs):
        self.check_instance_from_data_permission(request)
        return super(UserView, self).create(request, *args, **kwargs)

    @log_request
    def user_update(self, request, pk, **kwargs):
        self.check_instance_from_data_permission(request, pk)
        return super(UserView, self).partial_update(request, pk, **kwargs)

    @log_request
    def user_destroy(self, request, pk, **kwargs):
        self.check_instance_from_data_permission(request, pk)
        return super(UserView, self).destroy(request, pk, **kwargs)


class FileView(ModelViewSet, CheckInstanceFromDataPermission):
    queryset = File.objects.all()
    serializer_class = FileSerializer
    permission_classes = [IsAuthenticated, IsSuperuser | IsOwner]

    def get_queryset(self):
        file_id = self.request.GET.get('file_id', None)
        user_id = self.request.GET.get('user_id', None)

        request_user = self.request.user
        request_filter = {}

        if file_id is not None:
            request_filter['pk'] = int(file_id)
        elif user_id is not None:
            request_filter['user_id'] = int(user_id)

        queryset = self.queryset.filter(**request_filter)
        if not request_user.is_superuser:
            queryset = queryset & self.queryset.filter(user_id=request_user.id)

        return queryset

    @log_request
    def file_list(self, request, *args, **kwargs):
        return super(FileView, self).list(request, *args, **kwargs)

    @log_request
    def file_create(self, request, *args, **kwargs):
        self.check_instance_from_data_permission(request)
        return super(FileView, self).create(request, *args, **kwargs)

    @log_request
    def file_update(self, request, pk, **kwargs):
        self.check_instance_from_data_permission(request, pk)
        return super(FileView, self).partial_update(request, pk, **kwargs)

    @log_request
    def file_destroy(self, request, pk, **kwargs):
        self.check_instance_from_data_permission(request, pk)
        return super(FileView, self).destroy(request, pk, **kwargs)


class UserSettingsView(ModelViewSet, CheckInstanceFromDataPermission):
    queryset = UserSettings.objects.all()
    serializer_class = UserSettingsSerializer

    @log_request
    def settings_list(self, request, *args, **kwargs):
        instance = self.queryset.get(pk=self.request.user.id)
        from django.http import JsonResponse
        from django.forms import model_to_dict
        return JsonResponse(model_to_dict(instance))

    @log_request
    def settings_update(self, request, *args, **kwargs):
        from django.http import JsonResponse
        from django.forms import model_to_dict

        # queryset = self.queryset.filter(user_id=request.user.id)
        # request.data.update({"user": str(request.user.id)})
        # # request.data['user'] = request.user.id
        # print(request.data)
        #
        # if queryset.count() == 0:
        #     serializer = self.serializer_class(data=request.data)
        #     serializer.user = request.user
        #     serializer.is_valid(raise_exception=True)
        #     return JsonResponse(model_to_dict(serializer.validated_data))
        # else:
        #     queryset.update(**request.data)
        #     instance = self.queryset.get(user_id=request.user.id)
        #     return JsonResponse(model_to_dict(instance))

        # try:
        #     instance = self.queryset.get(user_id=request.user.id)
        # except UserSettings.DoesNotExist:
        #     instance = UserSettings.objects.create(user=request.user)
        # except:
        #     error = u'Token receipt error'
        #     status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        #
        self.queryset.filter(user_id=request.user.id).update(**request.data)
        instance = self.queryset.get(user_id=request.user.id)
        return JsonResponse(model_to_dict(instance))


def issue_token(request):
    logger.debug(f"{request.user} {request.method} {request.get_full_path()}")

    body_unicode = request.body.decode('utf-8')
    body = json.loads(body_unicode)
    serializer = IssueTokenRequestSerializer(data=body)
    if serializer.is_valid():
        authenticated_user = authenticate(**serializer.validated_data)
        if authenticated_user is None:
            error = u'Invalid username or password'
            status_code = status.HTTP_401_UNAUTHORIZED
        else:
            try:
                token = Token.objects.get(user=authenticated_user);
                status_code = status.HTTP_200_OK
            except Token.DoesNotExist:
                token = Token.objects.create(user=authenticated_user)
                status_code = status.HTTP_200_OK
            except:
                error = u'Token receipt error'
                status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

        if status_code == status.HTTP_200_OK:
            result = json.dumps({
                'id': authenticated_user.id,
                'username': authenticated_user.username,
                'first_name': authenticated_user.first_name,
                'last_name': authenticated_user.last_name,
                'email': authenticated_user.email,
                'is_superuser': authenticated_user.is_superuser,
                'token': token.key,
            })
            logger.info(f"{request.user} {request.method} {request.get_full_path()} OK")
        else:
            logger.error(f'{status_code} | {error}')
            result = json.dumps({'error': error}, ensure_ascii=False)

        return HttpResponse(result, status=status_code)
    else:
        logger.error(f'{status.HTTP_400_BAD_REQUEST} | {serializer.errors}')
        return HttpResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@log_issue_set_request_user
@log_issue_link
def issue_link_generation(request, *callback_args, **callback_kwargs):
    match request.method:
        case 'POST':
            body_unicode = request.body.decode('utf-8')
            body = json.loads(body_unicode)

            pk = body.get('id', None)

            if pk is None:
                return HttpResponse(status=status.HTTP_400_BAD_REQUEST)
            else:
                from django.db import utils
                from uuid import uuid4

                http_host = request.scheme + '://' + request.META['HTTP_HOST']

                try_count = 0
                while True:
                    try:
                        view = FileView()
                        file = view.queryset.get(pk=pk)
                        view.check_object_permissions(request, file)

                        url = http_host + '/download/' + str(uuid4())
                        file.url = url
                        file.save()
                        return HttpResponse(json.dumps({'url': url}),
                                            status=status.HTTP_200_OK,
                                            content_type='application/json')
                    except File.DoesNotExist:
                        return HttpResponse(status=status.HTTP_404_NOT_FOUND)
                    except utils.IntegrityError:
                        try_count += 1
                        if try_count >= 100:
                            return HttpResponse(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                    except:
                        return HttpResponse(status=status.HTTP_403_FORBIDDEN)

        case 'DELETE':
            body_unicode = request.body.decode('utf-8')
            body = json.loads(body_unicode)

            pk = body.get('id', None)

            if pk is None:
                return HttpResponse(status=status.HTTP_400_BAD_REQUEST)
            else:
                try:
                    view = FileView()
                    file = view.queryset.get(pk=pk)
                    view.check_object_permissions(request, file)

                    file = File.objects.get(pk=pk)
                    file.url = None
                    file.save()
                    return HttpResponse(status=status.HTTP_200_OK)
                except File.DoesNotExist:
                    return HttpResponse(status=status.HTTP_404_NOT_FOUND)
                except:
                    return HttpResponse(status=status.HTTP_403_FORBIDDEN)

    return HttpResponse(status=status.HTTP_405_METHOD_NOT_ALLOWED)


@log_issue_link
def issue_link_download(request, *callback_args, **callback_kwargs):
    match request.method:
        case 'GET':
            uuid = callback_kwargs.get('uuid', None)

            if uuid is None:
                return HttpResponse(status=status.HTTP_400_BAD_REQUEST)
            else:
                http_host = request.scheme + '://' + request.META['HTTP_HOST']
                url = http_host + '/download/' + uuid

                try:
                    from django.utils import timezone
                    import datetime

                    file = File.objects.get(url=url)
                    file.download_count = file.download_count + 1
                    file.download_at = datetime.datetime.now(tz=timezone.timezone.utc)
                    file.save()

                    response = HttpResponse(file.handle.read(),
                                            status=status.HTTP_200_OK,
                                            content_type='application/octet-stream')
                    response['Content-Disposition'] = f'attachment; filename={file.filename}'
                    return response
                except File.DoesNotExist:
                    return HttpResponse(status=status.HTTP_404_NOT_FOUND)
                # except:
                #     return HttpResponse(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

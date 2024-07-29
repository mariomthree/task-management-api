from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework import status, viewsets
from .serializers import TaskSerializer
from .models import Task


class TaskViewSet(viewsets.ModelViewSet):
    serializer_class = TaskSerializer
    queryset = Task.objects.all()

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)

            serializer.save()
            return Response({
                "code": "API_TASK_CREATE_SUCCESS",
                "message": "Task created successfully",
                "task": serializer.data
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({
                "code": "API_TASK_CREATE_ERROR",
                "message": "Failed to create task",
                "errors": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        try:
            task = Task.objects.get(id=pk)
            serializer = self.get_serializer(task, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)

            serializer.save()
            return Response({
                "code": "API_TASK_UPDATE_SUCCESS",
                "message": "Task updated successfully",
                "task": serializer.data
            }, status=status.HTTP_200_OK)
        except Task.DoesNotExist:
            return Response({
                "code": "API_TASK_NOT_FOUND",
                "message": "Task does not exist."
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                "code": "API_TASK_UPDATE_ERROR",
                "message": "Failed to update task",
                "errors": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, pk=None):
       pass

    def retrieve(self, request, pk=None):
        try:
            task = self.get_queryset().get(pk=pk)
            serializer = self.get_serializer(task)

            return Response({
                "code": "API_TASK_RETRIEVE_SUCCESS",
                "message": "Task retrieved successfully",
                "task": serializer.data
            }, status=status.HTTP_200_OK)
        except Task.DoesNotExist:
            return Response({
                "code": "API_TASK_NOT_FOUND",
                "message": "Task not found"
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                "code": "API_TASK_RETRIEVE_ERROR",
                "message": "Failed to retrieve task.",
                "error": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        try:
            task = self.get_queryset().get(pk=pk)
            task.delete()

            return Response({
                "code": "API_TASK_DELETE_SUCCESS",
                "message": "Task deleted successfully"
            }, status=status.HTTP_204_NO_CONTENT)
        except Task.DoesNotExist:
            return Response({
                "code": "API_TASK_NOT_FOUND",
                "message": "Task not found"
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                "code": "API_TASK_DELETE_ERROR",
                "message": "Failed to delete task.",
                "error": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

    def list(self, request):
        try:
            tasks = self.get_queryset()
            serializer = self.get_serializer(tasks, many=True)

            return Response({
                "code": "API_TASK_LIST_SUCCESS",
                "message": "Tasks retrieved successfully",
                "tasks": serializer.data
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "code": "API_TASK_LIST_ERROR",
                "message": "Failed to retrieve tasks.",
                "error": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)


from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import User, Group
from django.contrib.auth.hashers import make_password
from .serializers import UserSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request):
        email = request.data.get('email')
        if User.objects.filter(email=email).exists():
            return Response({
                "code": "API_USER_ALREADY_EXISTS",
                "message": "E-mail is already in use.",
                "errors": {"email": ["E-mail is already in use."]}
            }, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            groups = request.data.get('groups', [])
            if groups:
                user.groups.set(groups)
            Token.objects.create(user=user)

            return Response({
                "code": "API_USER_CREATE_SUCCESS",
                "message": "User created successfully",
                "user": serializer.data
            }, status=status.HTTP_201_CREATED)

        return Response({
            "code": "API_USER_CREATE_ERROR",
            "message": "Failed to create user",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        avatar = request.FILES.get('avatar')

        MAX_COVER_SIZE_MB = 2
        if avatar and avatar.size > MAX_COVER_SIZE_MB * 1024 * 1024:
            return Response({
                "code": "API_VIDEO_AVATAR_SIZE_ERROR",
                "message": "The file size must be equal to or less than 2 MB."
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(id=pk)
        except User.DoesNotExist:
            return Response({
                "code": "API_USER_NOT_FOUND",
                "message": "User does not exist."
            }, status=status.HTTP_404_NOT_FOUND)

        groups = request.data.get('groups', [])
        if not groups:
            return Response({
                "code": "API_GROUP_NOT_FOUND",
                "message": "Group does not exist.",
                "errors": {"groups": ["Group does not exist."]}
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            for group_id in groups:
                Group.objects.get(id=group_id)
        except Group.DoesNotExist:
            return Response({
                "code": "API_GROUP_NOT_FOUND",
                "message": "Group does not exist.",
                "errors": {"groups": ["Group does not exist."]}
            }, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            new_password = serializer.validated_data.get('password')
            if new_password:
                hashed_password = make_password(new_password)
                serializer.validated_data['password'] = hashed_password

            user = serializer.save()
            user.groups.clear()
            user.groups.set(groups)

            return Response({
                "code": "API_USER_UPDATE_SUCCESS",
                "message": "User updated successfully",
                "user": serializer.data
            })

        return Response({
            "code": "API_USER_UPDATE_ERROR",
            "message": "Failed to update user",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        try:
            user = self.get_queryset().get(pk=pk)
            serializer = self.get_serializer(user)
            return Response({
                "code": "API_USER_RETRIEVE_SUCCESS",
                "message": "User retrieved successfully",
                "user": serializer.data
            })
        except User.DoesNotExist:
            return Response({
                "code": "API_USER_RETRIEVE_ERROR",
                "message": "User not found"
            }, status=status.HTTP_404_NOT_FOUND)

    def destroy(self, request, pk=None):
        try:
            user = self.get_queryset().get(pk=pk)
            user.delete()
            return Response({
                "code": "API_USER_DELETE_SUCCESS",
                "message": "User deleted successfully"
            }, status=status.HTTP_204_NO_CONTENT)
        except User.DoesNotExist:
            return Response({
                "code": "API_USER_DELETE_ERROR",
                "message": "User not found"
            }, status=status.HTTP_404_NOT_FOUND)

    def list(self, request):
        users = self.get_queryset()
        serializer = self.get_serializer(users, many=True)
        return Response({
            "code": "API_USER_LIST_SUCCESS",
            "message": "Users retrieved successfully",
            "users": serializer.data
        })
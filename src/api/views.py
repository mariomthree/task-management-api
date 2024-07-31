from rest_framework.response import Response
from rest_framework import status, viewsets
from django.db import transaction
from django.contrib.auth.models import User, Group
from django.contrib.auth.hashers import make_password
from .serializers import TaskSerializer, UserSerializer
from .models import Task
from rest_framework.permissions import IsAuthenticated


class TaskViewSet(viewsets.ModelViewSet):
    serializer_class = TaskSerializer
    queryset = Task.objects.all()
    permission_classes = []

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)

            with transaction.atomic():
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
            serializer = self.get_serializer(task, data=request.data)
            serializer.is_valid(raise_exception=True)

            with transaction.atomic():
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
        try:
            task = Task.objects.get(id=pk)
            serializer = self.get_serializer(task, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)

            with transaction.atomic():
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
            with transaction.atomic():
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


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = []

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            with transaction.atomic():
                user = serializer.save()
                user.groups.set(request.data.get('groups', []))
            return Response({
                "code": "API_USER_CREATE_SUCCESS",
                "message": "User created successfully.",
                "user": serializer.data
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({
                "code": "API_USER_CREATE_ERROR",
                "message": "Failed to create user.",
                "errors": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        try:
            user = User.objects.get(id=pk)
            serializer = self.get_serializer(user, data=request.data)
            serializer.is_valid(raise_exception=True)

            new_password = serializer.validated_data.get('password')
            if new_password:
                serializer.validated_data['password'] = make_password(new_password)

            groups = request.data.get('groups')
            if groups is not None:
                for group_id in groups:
                    if not Group.objects.filter(id=group_id).exists():
                        raise Group.DoesNotExist

            with transaction.atomic():
                user = serializer.save()
                if groups is not None:
                    user.groups.set(groups)

            return Response({
                "code": "API_USER_UPDATE_SUCCESS",
                "message": "User updated successfully",
                "user": serializer.data
            })
        except User.DoesNotExist:
            return Response({
                "code": "API_USER_NOT_FOUND",
                "message": "User does not exist."
            }, status=status.HTTP_404_NOT_FOUND)
        except Group.DoesNotExist as e:
            return Response({
                "code": "API_GROUP_NOT_FOUND",
                "message": "One or more groups do not exist.",
                "errors": {"groups": ["One or more groups do not exist."]},
                "error": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                "code": "API_USER_UPDATE_ERROR",
                "message": "Failed to update user",
                "error": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, pk=None):
        try:
            user = User.objects.get(id=pk)
            serializer = self.get_serializer(user, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)

            new_password = serializer.validated_data.get('password')
            if new_password:
                serializer.validated_data['password'] = make_password(new_password)

            groups = request.data.get('groups')
            if groups is not None:
                for group_id in groups:
                    if not Group.objects.filter(id=group_id).exists():
                        raise Group.DoesNotExist

            with transaction.atomic():
                user = serializer.save()
                if groups is not None:
                    user.groups.set(groups)

            return Response({
                "code": "API_USER_UPDATE_SUCCESS",
                "message": "User updated successfully",
                "user": serializer.data
            })
        except User.DoesNotExist:
            return Response({
                "code": "API_USER_NOT_FOUND",
                "message": "User does not exist."
            }, status=status.HTTP_404_NOT_FOUND)
        except Group.DoesNotExist as e:
            return Response({
                "code": "API_GROUP_NOT_FOUND",
                "message": "One or more groups do not exist.",
                "errors": {"groups": ["One or more groups do not exist."]},
                "error": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                "code": "API_USER_UPDATE_ERROR",
                "message": "Failed to update user",
                "error": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        try:
            user = self.get_queryset().get(pk=pk)
            serializer = self.get_serializer(user)

            return Response({
                "code": "API_USER_RETRIEVE_SUCCESS",
                "message": "User retrieved successfully",
                "user": serializer.data
            }, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({
                "code": "API_USER_NOT_FOUND",
                "message": "User not found"
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                "code": "API_USER_RETRIEVE_ERROR",
                "message": "Failed to retrieve user.",
                "error": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        try:
            user = self.get_queryset().get(pk=pk)
            with transaction.atomic():
                user.delete()

            return Response({
                "code": "API_USER_DELETE_SUCCESS",
                "message": "User deleted successfully"
            }, status=status.HTTP_204_NO_CONTENT)
        except User.DoesNotExist:
            return Response({
                "code": "API_USER_NOT_FOUND",
                "message": "User not found"
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                "code": "API_USER_DELETE_ERROR",
                "message": "Failed to delete user.",
                "error": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

    def list(self, request):
        try:
            users = self.get_queryset()
            serializer = self.get_serializer(users, many=True)

            return Response({
                "code": "API_USER_LIST_SUCCESS",
                "message": "Users retrieved successfully",
                "users": serializer.data
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "code": "API_USER_LIST_ERROR",
                "message": "Failed to retrieve users.",
                "error": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

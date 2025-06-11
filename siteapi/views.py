from django.shortcuts import render

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from rest_framework.generics import ListCreateAPIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
# from rest_framework.mixins import ListModelMixin
from rest_framework.views import APIView


from django.shortcuts import get_object_or_404


from users.models import Community, Profile, Posts, User, Comments
from .serializers import CommunitiesSerializer, ProfileSerilizer, PostsSerializer, UserSerializer, PostCommentsSerializer
# Create your views here.
@api_view()
def hello_world_view(request: Request) -> Response:
    return Response({"message": "Hello World!"})


class CommunitiesListView(ListCreateAPIView):
    queryset = Community.objects.all()
    serializer_class = CommunitiesSerializer

class ProfileListView(ModelViewSet):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerilizer
    filter_backends = [
        SearchFilter,
        DjangoFilterBackend,
        OrderingFilter,
    ]
    search_fields = ['bio',]

    filterset_fields = [
        'user',
        'bio',
        'phone_number',
        'date_of_birth',
        'gender',
    ]

    ordering_fields = ['id', 'date_of_birth']



class PostsView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request: Request) -> Response:
        posts = Posts.objects.all()
        serialized = PostsSerializer(posts, many=True)
        return Response({'posts': serialized.data})

    def post(self, request):
        serializer = PostsSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.data, status=status.HTTP_400_BAD_REQUEST)

# class PostsView(ListCreateAPIView):
#     queryset = Posts.objects.all()
#     serializer_class = PostsSerializer


class UserPostsView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, requset: Request, user_id=None) -> Response:
        if user_id:
            user = get_object_or_404(User, pk=user_id)
            posts = Posts.objects.filter(user=user)
            serialized = PostsSerializer(posts, many=True)
            return Response(serialized.data, status=status.HTTP_200_OK)
        else:
            users = User.objects.all()
            serialized = UserSerializer(users, many=True)
            return Response(serialized.data, status=status.HTTP_200_OK)


class PostCommentsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request: Request, post_id) -> Response:
        post = get_object_or_404(Posts, pk=post_id)
        comments = Comments.objects.filter(post=post)
        serialized = PostCommentsSerializer(comments, many=True)
        return Response(serialized.data, status=status.HTTP_200_OK)

    def post(self, request: Request, post_id) -> Response:
        post = get_object_or_404(Posts, pk=post_id)
        serializer = PostCommentsSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user, post=post)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
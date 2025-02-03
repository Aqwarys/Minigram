from django.shortcuts import render

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.request import Request

from rest_framework.generics import ListCreateAPIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
# from rest_framework.mixins import ListModelMixin


from users.models import Community, Profile
from .serializers import CommunitiesSerializer, ProfileSerilizer
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

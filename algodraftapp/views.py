from django.shortcuts import render
from django.http import HttpResponse
from rest_framework.decorators import api_view
from django.contrib.auth.models import User, Group
from rest_framework import viewsets
from rest_framework.response import Response
from algodraftapp.serializers import UserSerializer, GroupSerializer

def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")
# Create your views here.

class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer


class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Group.objects.all()
    serializer_class = GroupSerializer



@api_view(['GET', 'POST'])
def dddraft(request):
    """
    List all code snippets, or create a new snippet.
    """
    if request.method == 'GET':
        # snippets = Snippet.objects.all()
        # serializer = SnippetSerializer(snippets, many=True)
        # 
        # queryset = Group.objects.all()
        # serializer_class = GroupSerializer
        # return Response(serializer.data)
        return Response({'hello':request.data})

    elif request.method == 'POST':
        # return Response({'nihao':'world'})
        print(request.data["qsdf"])
        return Response(request.data)
        # serializer = SnippetSerializer(data=request.data)
        # if serializer.is_valid():
        #     serializer.save()
        #     return Response(serializer.data, status=status.HTTP_201_CREATED)
        # return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



from django.shortcuts import render
from django.http import HttpResponse
from rest_framework.decorators import api_view
from django.contrib.auth.models import User, Group
from rest_framework import viewsets, status
from rest_framework.response import Response
from algodraftapp.serializers import UserSerializer, GroupSerializer
from algodraftapp.algodraft import algodraft


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
        # return Response(serializer.data) request.query_params['qsdf']
        print(123123,request.query_params, request.user)
        response = Response({'hello':str(request.user)})
        # response.headers.add('Access-Control-Allow-Origin', '*')
        return response

    elif request.method == 'POST':
        # return Response({'nihao':'world'}) request.data["qsdf"],
        print(456456,request, request.user, request.data)
        claimstext = request.data.get('claimstext','')
        if claimstext:
            r = algodraft(claimstext)
            # print(5555,r)
            return Response({'descriptionhtml':r}     )
        else:
            return Response({'hey':'you!'}, status=status.HTTP_400_BAD_REQUEST)
        # serializer = SnippetSerializer(data=request.data)
        # if serializer.is_valid():
        #     serializer.save()
        #     return Response(serializer.data, status=status.HTTP_201_CREATED)
        # return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



from django.shortcuts import render
from django.http import HttpResponse
from rest_framework.decorators import api_view
from django.contrib.auth.models import User, Group
from rest_framework import viewsets, status
from rest_framework.response import Response
from typometricsapp.serializers import UserSerializer, GroupSerializer
from typometricsapp.tsv2json import tsv2json, getoptions, gettypes


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
def typo(request):
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
        xty = request.data.get('xtype','')
        yty = request.data.get('ytype','')
        if xty:
            jsondata = tsv2json(
                xty, request.data.get('x',''),
                yty, request.data.get('y',''))
            # print(5555,r)
            return Response({'chartdata':jsondata}     )
        else:
            return Response({'hey':'you!'}, status=status.HTTP_400_BAD_REQUEST)
        # serializer = SnippetSerializer(data=request.data)
        # if serializer.is_valid():
        #     serializer.save()
        #     return Response(serializer.data, status=status.HTTP_201_CREATED)
        # return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



@api_view(['POST'])
def typoptions(request):
    """
    for a given type get the options (columns of tsv)
    """

    if request.method == 'POST':
        # print(90909,request, request.user, request.data)
        ty = request.data.get('type','')
        opts = getoptions(ty)
        # print('___',opts)
        if opts:
            return Response({'options':opts}     )
        else:
            return Response({'hey':'you!'}, status=status.HTTP_400_BAD_REQUEST)
 

@api_view(['GET'])
def types(request):
    """
    get possible types of analysis
    """
    if request.method == 'GET':
        # print(111190909,request, request.user, request.data)
        
        return Response({'types':gettypes()}     )
        # else:
        #     return Response({'hey':'you!'}, status=status.HTTP_400_BAD_REQUEST)
 
           

from rest_framework import status
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
import commands

from rest_api.models import Service,App
from rest_api.serializers import ServiceSerializer,AppSerializer
from rest_api.transact import AppTransac



@api_view(['GET', 'POST'])
@authentication_classes((TokenAuthentication,))
@permission_classes((IsAuthenticated,))
def project_list(request, format=None):
    '''
    list all servie or create a service
    '''
    poj_trsc = AppTransac('monkey', 'monkey')

    if request.method == 'GET':
        ret_data = {}
        #get paras from get request
        try:
            username = request.GET['username']
            begin_index = int(request.GET['start'])
            length = int(request.GET['limit'])
        except:
            return Response({},status=status.HTTP_400_BAD_REQUEST)

        poj_list = poj_trsc.project_list(begin_index, length)

        #get all service name
        ret_data['success'] = "true"
        ret_data['total'] = len(poj_list)
        ret_data['items'] = poj_list
        return Response(ret_data)

    elif request.method == 'POST':
        ret_data = {}
        try:
            username = request.POST['username']
            projname = request.POST['projname']
            projurl = request.POST['projurl']
        except:
            return Response({},status=status.HTTP_400_BAD_REQUEST)
        
        status, log = poj_trsc.create_project(projname, projurl)

        return Response({'log':log})


@api_view(['GET'])
@authentication_classes((TokenAuthentication,))
@permission_classes((IsAuthenticated,))
def service_list(request, format=None):
    '''
    list services of a project
    '''
    ret_data = {}
    srv_t = AppTransac('monkey', 'monkey')

    try:
        project_name = request.GET['project']
    except:
        return Response({},status=status.HTTP_400_BAD_REQUEST)

    services = srv_t.service_list(project_name)

    ret_data['success'] = 'true'
    ret_data['total'] = len(services)
    ret_data['services'] = services
    return Response(ret_data)


@api_view(('GET',))
def api_root(request, format=None):
    return Response({
        'services': reverse('services', request=request, format=None),
        'projects': reverse('projects', request=request, format=None)
    })

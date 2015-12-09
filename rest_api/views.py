# coding: utf-8
from rest_framework import status
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import authenticate
from rest_framework.decorators import (
        api_view, 
        authentication_classes, 
        permission_classes
)

from rest_api.models import Service,App
from compose.database import database
from compose.restful import create_project


@api_view(['GET', 'POST'])
@authentication_classes((TokenAuthentication,))
@permission_classes((IsAuthenticated,))
def project_list(request, format=None):
    '''
    list all servie or create a service
    '''
    poj_trsc = database('monkey', 'monkey')

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

        sts, log = create_project('monkey', 'monkey', projname, projurl)

        return Response({'log':log})


@api_view(['DELETE', 'GET'])
@authentication_classes((TokenAuthentication,))
@permission_classes((IsAuthenticated,))
def project(request, project, format=None):
    poj_trsc = database('monkey', 'monkey')
    
    if request.method == 'DELETE':
        sts, log = poj_trsc.destroy_project(project)
        return Response({'Delete': sts, 'log':log})

    elif request.method == 'GET':
        services = poj_trsc.service_list(project)
        ret_data = {}
        ret_data['success'] = 'true'
        ret_data['total'] = len(services)
        ret_data['services'] = services
        return Response(ret_data)


@api_view(['GET'])
@authentication_classes((TokenAuthentication,))
@permission_classes((IsAuthenticated,))
def shellbox(request, format=None):
    shell_trsc = database('monkey', 'monkey')

    if request.method == 'GET':
        try:
            project = request.GET['project']
            service = request.GET['service']
        except:
            return Response({}, status=status.HTTP_400_BAD_REQUEST)
        
        addr = shell_trsc.get_shellinabox(project, service)

        return Response({"address":addr})


@api_view(['GET'])
@authentication_classes((TokenAuthentication,))
@permission_classes((IsAuthenticated,))
def service_list(request, format=None):
    '''
    list services of a project
    '''
    ret_data = {}
    srv_t = database('monkey', 'monkey')

    try:
        project_name = request.GET['project']
    except:
        return Response({},status=status.HTTP_400_BAD_REQUEST)

    services = srv_t.service_list(project_name)

    ret_data['success'] = 'true'
    ret_data['total'] = len(services)
    ret_data['services'] = services
    return Response(ret_data)


@api_view(['GET'])
@authentication_classes((TokenAuthentication,))
@permission_classes((IsAuthenticated,))
def log(request, format=None):
    '''
    get logs of a specific service
    '''
    ret_data = {}
    log_tsc = database('monkey', 'monkey')

    try:
        project_name = request.GET['project']
        service_name = request.GET['service']
    except:
        print "here"
        return Response({}, status = status.HTTP_400_BAD_REQUEST)
    
    log = log_tsc.get_logs(project_name, service_name)
    ret_data['success'] = 'true'
    ret_data['logs'] = log
    
    return Response(ret_data)


@api_view(('GET',))
def api_root(request, format=None):
    return Response({
        'services': reverse('project', request=request, format=None),
        'projects': reverse('projects', request=request, format=None)
    })

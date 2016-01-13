# coding: utf-8
from rest_framework import status
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import authenticate
import ast

from rest_framework.decorators import (
        api_view, 
        authentication_classes, 
        permission_classes
)

# from compose import app_info, project_create
from orchestration.nap_api import app_info, project_create


@api_view(['GET', 'POST'])
@authentication_classes((TokenAuthentication,))
@permission_classes((IsAuthenticated,))
def project_list(request, format=None):
    """
    list all servie or create a service
    """
    username,passwd = str(request.user), str(request.user)

    if request.method == 'GET':
        ret_data = {}
        # get paras from get request
        try:
            begin_index = int(request.GET['start'])
            length = int(request.GET['limit'])
        except:
            return Response({},status=status.HTTP_400_BAD_REQUEST)

        poj_list = app_info.project_list(username, passwd, begin_index, length)

        # get all service name
        ret_data['success'] = "true"
        ret_data['total'] = len(poj_list)
        ret_data['items'] = poj_list
        return Response(ret_data)

    elif request.method == 'POST':
        try:
            projname = request.POST['projname']
            cmd = request.POST['cmd']
        except:
            return Response({}, status=status.HTTP_400_BAD_REQUEST)

        # create project from github url
        if cmd == 'url':
            try:
                projurl = request.POST['projurl']
            except:
                return Response({}, status=status.HTTP_400_BAD_REQUEST)

            sts, msg = project_create.create_project_from_url(username, passwd, projname, projurl)
            if sts == 'Argv':
                return Response({'paras': 'true', 'argv': msg})
            else:
                return Response({'paras': 'false', 'log': msg})

        # create proejct from filebrowser
        elif cmd == 'file':
            sts, msg = project_create.create_project_from_file(username, passwd, projname)
            if sts == 'Argv':
                return Response({'paras': 'true', 'argv': msg})
            else:
                return Response({'paras': 'false', 'log': msg})

        # create from given params and filepath
        elif cmd == 'paras':
            try:
                argv = request.POST['paras']
            except:
                return Response({}, status=status.HTTP_400_BAD_REQUEST)
            argv_dict = ast.literal_eval(argv)
            sts, msg = project_create.replace_argv(username, passwd, projname, argv_dict)
            return Response({'log': msg})


@api_view(['DELETE', 'GET'])
@authentication_classes((TokenAuthentication,))
@permission_classes((IsAuthenticated,))
def project(request, project, format=None):
    """
    delete a project, or get services from a project
    """
    username, passwd = str(request.user), str(request.user)

    if request.method == 'DELETE':
        sts, logs = app_info.destroy_project(username, passwd, project)
        return Response({'Delete': sts, 'log': logs})

    elif request.method == 'GET':
        services = app_info.service_list(username, passwd, project)
        ret_data = {}
        ret_data['success'] = 'true'
        ret_data['total'] = len(services)
        ret_data['services'] = services
        return Response(ret_data)


@api_view(['GET'])
@authentication_classes((TokenAuthentication,))
@permission_classes((IsAuthenticated,))
def service_list(request, format=None):
    """
    list services of a project
    """
    ret_data = {}
    username,passwd = str(request.user), str(request.user)

    try:
        project_name = request.GET['project']
    except:
        return Response({}, status=status.HTTP_400_BAD_REQUEST)

    services = app_info.service_list(username, passwd, project_name)

    ret_data['success'] = 'true'
    ret_data['total'] = len(services)
    ret_data['services'] = services
    return Response(ret_data)


@api_view(['GET'])
@authentication_classes((TokenAuthentication,))
@permission_classes((IsAuthenticated,))
def log(request, format=None):
    """
    get logs of a specific service
    """
    ret_data = {}
    username,passwd = str(request.user), str(request.user)

    try:
        project_name = request.GET['project']
        service_name = request.GET['service']
    except:
        print "here"
        return Response({}, status = status.HTTP_400_BAD_REQUEST)
    
    logs = app_info.get_logs(username, passwd, project_name, service_name)
    ret_data['success'] = 'true'
    ret_data['logs'] = logs
    
    return Response(ret_data)


@api_view(('GET',))
def api_root(request, format=None):
    return Response({
        'services': reverse('project', request=request, format=None),
        'projects': reverse('projects', request=request, format=None)
    })

# coding: utf-8
from rest_framework import status
from rest_framework.response import Response
from rest_framework.reverse import reverse
# from rest_framework.authentication import TokenAuthentication
# from rest_framework.permissions import IsAuthenticated
import ast

from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes
)

# from compose import app_info, project_create
from orchestration.nap_api import app_info
from orchestration.nap_api import project_create

username = 'test'

@api_view(['GET', 'POST', 'PUT'])
# @authentication_classes((TokenAuthentication,))
# @permission_classes((IsAuthenticated,))
def project_list(request, format=None):
    """
    list all servie or create a service
    """
    # username = str(request.user)

    if request.method == 'GET':
        ret_data = {}
        # get paras from get request
        try:
            begin_index = int(request.GET['start'])
            length = int(request.GET['limit'])
        except:
            return Response({}, status=status.HTTP_400_BAD_REQUEST)

        poj_list = app_info.project_list(username, begin_index, length)

        # get all service name
        ret_data['success'] = "true"
        ret_data['total'] = len(poj_list)
        ret_data['items'] = poj_list
        return Response(ret_data)

    elif request.method == 'PUT':
        try:
            cmd = request.data['cmd']
            project_name = request.data['project_name']
        except:
            return Response({}, status=status.HTTP_400_BAD_REQUEST)

        # kill project
        if cmd == 'kill':
            # sts, msg = app_info.kill_project(username, project_name)
            # return Response({'success': sts, 'log': msg})
            app_info.kill_project(username, project_name)
            return Response({'success': 'success', 'log': 'log'})
        elif cmd == 'restart':
            print username, project_name
            # sts, msg = app_info.restart_project(username, project_name)
            # return Response({'success': sts, 'log': msg})
            app_info.restart_project(username, project_name)
            return Response({'success': 'success', 'log': 'log'})

    elif request.method == 'POST':
        try:
            project_name = request.POST['project_name']
            cmd = request.POST['cmd']
        except:
            return Response({}, status=status.HTTP_400_BAD_REQUEST)

        # create project from github url
        if cmd == 'url':
            try:
                project_url = request.POST['url']
            except:
                return Response({}, status=status.HTTP_400_BAD_REQUEST)

            sts, msg = project_create.create_project_from_url(username, project_name, project_url)
            if sts == 'Argv':
                return Response({'paras': 'true', 'argv': msg})
            else:
                return Response({'paras': 'false', 'log': msg})

        # create proejct from filebrowser
        elif cmd == 'file':
            sts, msg = project_create.create_project_from_file(username, project_name)
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
            sts, msg = project_create.replace_argv(username, project_name, argv_dict)
            return Response({'log': msg})


@api_view(['DELETE', 'GET'])
# @authentication_classes((TokenAuthentication,))
# @permission_classes((IsAuthenticated,))
def project(request, pro, format=None):
    """
    delete a project, or get services from a project
    """
    # username = str(request.user)

    if request.method == 'DELETE':
        sts, logs = app_info.destroy_project(username, pro)
        return Response({'Delete': sts, 'log': logs})

    elif request.method == 'GET':
        item = app_info.get_project(username, pro)
        ret_data = {'success': 'true', 'total': 1, 'item': item}
        return Response(ret_data)


@api_view(['GET'])
def service(request, format=None):
    """
    get a service
    """

    # username = str(request.user)

    project_name = request.GET['project']
    service_name = request.GET['service']

    if request.method == 'GET':
        item = app_info.get_service(username, project_name, service_name)
        ret_data = {'success': 'true', 'total': 1, 'item': item}
        return Response(ret_data)

@api_view(['GET'])
# @authentication_classes((TokenAuthentication,))
# @permission_classes((IsAuthenticated,))
def service_list(request, format=None):
    """
    list services of a project
    """
    ret_data = {}
    # username = str(request.user)

    try:
        project_name = request.GET['project']
    except:
        return Response({}, status=status.HTTP_400_BAD_REQUEST)

    print project_name

    services = app_info.service_list(username, project_name)

    ret_data['success'] = 'true'
    ret_data['total'] = len(services)
    ret_data['services'] = services
    return Response(ret_data)


@api_view(['GET'])
# @authentication_classes((TokenAuthentication,))
# @permission_classes((IsAuthenticated,))
def log(request, format=None):
    """
    get logs of a specific service
    """
    ret_data = {}
    # username = str(request.user)

    print 'log before'
    try:
        project_name = request.GET['project_name']
        service_name = request.GET['service_name']
    except:
        return Response({}, status=status.HTTP_400_BAD_REQUEST)

    logs = app_info.get_logs(username, project_name, service_name)
    ret_data['success'] = 'true'
    ret_data['logs'] = logs

    return Response(ret_data)


@api_view(('GET',))
def api_root(request, format=None):
    return Response({
        'services': reverse('project', request=request, format=None),
        'projects': reverse('projects', request=request, format=None)
    })


@api_view(['GET'])
def monitor(request, format=None):
    """
    get monitor info about machine or container
    """
    try:
        cmd = request.GET['cmd']
    except:
        return Response({}, status=status.HTTP_400_BAD_REQUEST)

    if cmd == 'machine':
        dic = app_info.machine_monitor()

        return Response({'dic': dic})

    elif cmd == 'container':
        project_name = request.GET['project_name']
        service_name = request.GET['service_name']
        print "here"
        dic = app_info.container_monitor(username, project_name, service_name)

        ret_data = {'success': 'true', 'dic': dic}

        return Response(ret_data)

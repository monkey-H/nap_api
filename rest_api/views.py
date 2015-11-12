from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_api.models import Service,App
from rest_api.serializers import ServiceSerializer,AppSerializer
from rest_framework.reverse import reverse
import commands

from rest_api.utils import parse_service_content,parse_app_content
from django.contrib.auth import authenticate


@api_view(['GET', 'POST'])
def service_list(request, format=None):
    '''
    list all servie or create a service
    '''
    if request.method == 'GET':
        ret_data = {}
        #get paras from get request
        try:
            username = request.GET['username']
            start_index = int(request.GET['start'])
            length = int(request.GET['length'])
        except:
            return Response({},status=status.HTTP_400_BAD_REQUEST)
        #get all service name
        statuses,output = commands.getstatusoutput("nap list_services %s" % username)
        if len(output) == 0:
            ret_data['success'] = "true"
            ret_data['total'] = 0
            ret_data['items'] = []
        else:
            #get service detail as array
            service_arr = parse_service_content(output)
            ret_data['success'] = "true"
            ret_data['total'] = len(service_arr)
            ret_data['items'] = service_arr[start_index:start_index+length]
        return Response(ret_data)
    elif request.method == 'POST':
        pass

@api_view(['GET', 'POST'])
def app_list(request, format=None):
    '''
    list apps of specific service
    '''
    if request.method == 'GET':
        ret_data = {}
        #get paras from get request
        try:
            username = request.GET['username']
            service_name = request.GET['service']
        except:
            return Response({},status=status.HTTP_400_BAD_REQUEST)
        statuses,output = commands.getstatusoutput("nap list_instances %s_%s" % (username,service_name))
        instances = parse_app_content(output)
        ret_data['success'] = "true"
        ret_data['items'] = instances
        return Response(ret_data)
    elif request.method == 'POST':
        pass

@api_view(['POST'])
def user_authent(request):
    '''
    authenticate users
    '''
    if request.method == 'POST':
        try:
            username = request.POST['username']
            password = request.POST['password']
        except:
            return Response({},status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(username=username,password=password)
        if user is not None and user.is_active:
            return Response({'login':'ok'})
        else:
            return Response({'login':'fail'})


@api_view(('GET',))
def api_root(request, format=None):
    return Response({
        'services': reverse('services', request=request, format=None),
        'instances': reverse('instances', request=request, format=None)
    })

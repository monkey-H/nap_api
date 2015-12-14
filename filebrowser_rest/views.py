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

from filebrowser_rest.utils import(
        download,
        dirToJson,
        splitPath,
        getFsFromKey,
)

# Create your views here.
@api_view(['GET', 'POST', 'PUT', 'DELETE'])
#@authentication_classes((TokenAuthentication,))
#@permission_classes((IsAuthenticated,))
def file_operate(request, format=None):
    if request.method == 'GET':                 #请求文件，查看或下载
        root, path = splitPath(request.GET['node'])
        cmd = request.GET['cmd']

        if cmd not in ['view', 'download']:
            return Response({}, status = status.HTTP_400_BAD_REQUEST)

        if root:
            cur_fs = getFsFromKey(root)
            if not cur_fs: 
                return Response({}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({}, status=status.HTTP_400_BAD_REQUEST)

        attachment = True if cmd == 'download' else False
        return download(cur_fs, path, attachment)

    if request.method == 'POST':                #修改或上传文件
        upload(request)

    if request.method == 'PUT':                 #修改文件名字
        root1, path1 = splitPath(request.data['oldname'])
        root2, path2 = splitPath(request.data['newname'])
        if root1 != root2 or not root1 or not root2:
            return Response({}, status = status.HTTP_400_BAD_REQUEST)
        cur_fs = getFsFromKey(root1)

        if not cur_fs.exists(path1):
            return Response({'log':'no such file'}, status = status.HTTP_404_NOT_FOUND)

        try:
            cur_fs.rename(path1, path2)
            return Response({'reRname':'success', 'path':path2})
        except:
            return Response({}, status = status.HTTP_400_BAD_REQUEST)

    if request.method == 'DELETE':              #删除一个文件
        try:
            filepath = request.data['node']
        except:
            return Response({}, status = status.HTTP_400_BAD_REQUEST)

        root, path = splitPath(request.data['node'])
        if root:
            cur_fs = getFsFromKey(root)
            if not cur_fs:
                return Response({}, status = status.HTTP_404_NOT_FOUND)
        else:
            return Response({}, status = status.HTTP_400_BAD_REQUEST)

        if not cur_fs.exists(path):
            return Response({'log':'no such file'}, status = status.HTTP_404_NOT_FOUND)

        cur_fs.remove(path)
        return Response({'delete':'suceess', 'file':path})


@api_view(['GET', 'POST', 'PUT'])
#@authentication_classes((TokenAuthentication,))
#@permission_classes((IsAuthenticated,))
def dir_operate(request, format=None):
    if request.method == 'GET':
        root, path = splitPath(request.GET['node'])
    else:
        root, path = splitPath(request.data['node'])

    if root:
        cur_fs = getFsFromKey(root)
        if not cur_fs:
            return Response({}, status = status.HTTP_400_BAD_REQUEST)
    else:
        return Response({}, status = status.HTTP_400_BAD_REQUEST)
    
    if request.method == 'GET':
        if not cur_fs.exists(path):
            return Response({}, status = status.HTTP_404_NOT_FOUND)
        data = dirToJson(cur_fs, path, recursive = False)
        return Response(data)

    if request.method == 'POST':
        if cur_fs.exists(path):
            return Response({'newdir':'fail', 'log':'directory already exists!!'})
        cur_fs.makedir(path, recursive=True)
        return Response({'newdir':'success', 'directory':'path'})
    
    if request.method == 'DELETE':
        if not cur_fs.exists(path):
            return Response({'delete':'fail', 'log':'no such directory'}, 
                    status = status.HTTP_400_BAD_REQUEST)
        cur_fs.removedir(path)
        return Response({'delete':'success', 'directory':path})

    if request.method == 'PUT':
        root2, path2 = splitPath(request.data['newname'])
        if not root2 or not root == root2:
            return Response({}, status = status.HTTP_400_BAD_REQUEST)
        try:
            cur_fs.rename(path, path2)
            return Response({'rename':'success'})
        except:
            return Response({'log':'something wrong in renaming directory'}, status = status.HTTP_400_BAD_REQUEST)


def upload(request):
    file_list = []

    #设置文件类型限制
    #allowed_extensions = 'jpg,jpeg,gif,png,pdf,swf,doc,docx,xls,\
            #log,xlsx,ppt,pptx,txt,c,py,cpp,go,class,java'.split(',')

    #使用xmlhttpRequest进行请求
    if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
        path = request.META.get('HTTP_X_FILE_NAME')
        if not path:
            return Response({}, status = status.HTTP_400_BAD_REQUEST)

        root, path = splitPath( path.decode('UTF-8') )
        cur_fs = getFsFromKey( root )
        if not cur_fs:
            raise Response({}, status = status.HTTP_404_NOT_FOUND)

        data = request.body
        '''
        fName = path
        if not fName[fName.rfind('.')+1:].lower() in allowed_extensions:
            print 'FORBIDDEN FILE : %s ' % fName
            raise Exception('extension not allowed %s' % fName)
        '''
        f = cur_fs.open( path, 'wb')
        f.write(data)
        f.close()
        file_list.append(path)

    #使用一般的post请求
    else:
        root, path = splitPath(request.POST['node'].decode('UTF-8'))
        cur_fs = getFsFromKey(root)
        if not cur_fs: 
            raise Response({}, status = status.HTTP_404_NOT_FOUND)

        for key in request.FILES.keys():
            upload = request.FILES[key]
            fName = upload.name
            '''
            if not fName[fName.rfind('.')+1:].lower() in allowed_extensions:
                # todo : log + mail
                print 'FORBIDDEN FILE : %s ' % fName.encode('UTF-8')
                raise Exception('extension not allowed %s' % fName.encode('UTF-8'))
            '''
            f = cur_fs.open( path + '/' + fName, 'wb')
            for chunk in upload.chunks():
                f.write(chunk)
            f.close()
            file_list.append(fName)

    return Response({'success':True, 'file':file_list})

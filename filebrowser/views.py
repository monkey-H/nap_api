# coding: UTF-8
from django.conf import settings
from django.http import HttpResponse, Http404, JsonResponse, HttpResponseBadRequest
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
import os
import datetime
from filebrowser import decorators
from settings import sources

def test_hello(request):
    '''
    测试uploader模块
    '''
    return render(request, 'filebrowser/index.html')

def dirToJson(inFs, path = '/', recursive = False):
    '''
    将一个指定文件夹目录树返回,json格式数据
    '''
    data = []
    if not inFs.exists(path) or not inFs.isdir(path):
        return data
    for item in inFs.listdir(path = path ):
        fPath =  os.path.join(path, item )
        infos = inFs.getinfo( fPath )
        isLeaf = not inFs.isdir( fPath )
        iconCls = not isLeaf and 'icon-folder' or 'icon-file-%s' % item[item.rfind('.')+1:]
        row = {
            'text':item
            ,'size':infos.get('size', 0)
            ,'modified_time':infos.get('modified_time', datetime.datetime.now()).isoformat()
            ,'created_time':infos.get('created_time', datetime.datetime.now()).isoformat()
            ,'leaf':isLeaf
            ,'filetype':iconCls
            ,'items':[]
            ,'id': 'localfolder/' + fPath
        }
        # recursive and isdir ?
        if not isLeaf and recursive:
            row['items'] = dirToJson(inFs, path = fPath, recursive = recursive )

        data.append(row)
    return data


def splitPath(inPath):
    '''
    将参数传递的数据进行分割，path格式为 "key/subpath",其中key对应的是字典sources的key,
    value包括文件系统类型以及对应类型的pyfilesystem的参数,详见settings.py
    '''
    if not inPath:
        return None, None
    if inPath[0] == '/':
        inPath = inPath[1:]
    root = inPath.split('/')[0]
    path = '/'.join(inPath.split('/')[1:])
    return root, path


def getFsFromKey(key):
    if key in sources.keys():
        source = sources[key]
        cur_fs = source['cls']( **source['params'] )
        return cur_fs
    else:
        return None

@decorators.ajax_request
@csrf_exempt
def api(request):
    cmd = request.POST.get('cmd', request.GET.get('cmd'))
    if not cmd: raise Http404

    # todo: remove these special cases
    if cmd in ['view', 'download']:
        root, path = splitPath( request.GET['file'] )
    elif cmd == 'rename':
        root, path = splitPath( request.POST['oldname'] )
    elif cmd in ['newdir', 'get', 'delete']:
        root, path = splitPath( request.POST['node'] )
    else:
        return HttpResponseBadRequest("400 bad request")

    if root:
        cur_fs = getFsFromKey(root)
        if not cur_fs: raise Http404
    else:
        return HttpResponseBadRequest("400 bad request")

    if cmd == 'get':
        data = dirToJson(cur_fs, path, recursive = False)
        return JsonResponse(data, safe=False)

    elif cmd == 'newdir':
        if cur_fs.exists(path):
            return HttpResponseBadRequest("directory already exists")
        cur_fs.makedir(path, recursive=True)
        return JsonResponse({'success':True})

    elif cmd == 'rename':
        # todo : handle FS level moves
        root2, path2 = splitPath( request.POST['newname'] )
        if not root2:
            return HttpResponseBadRequest("400 bad request")
        if root == root2:
            # same FS
            try:
                cur_fs.rename(path, path2)
            except:
                return HttpResponseBadRequest("400 bad request")
        else:
            # different FS
            cur_fs2 = getFsFromKey(root2)
            if not cur_fs2: raise Http404
            inFile = cur_fs.open( path, 'rb' )
            outFile = cur_fs2.open( path2, 'wb' )
            outFile.write(inFile.read())
            outFile.close()
        return JsonResponse({'success':True})

    elif cmd == 'delete':
        if not cur_fs.exists(path): raise Http404
        if cur_fs.isdir(path):
            cur_fs.removedir( path )
        else:
            cur_fs.remove(path)
        return JsonResponse({'success':True})

    elif cmd == 'view':
        # todo redir to APACHE or OTHER
        return download(cur_fs,path)

    elif cmd == 'download':
        # todo redir to APACHE or OTHER
        return download(cur_fs,path,attachment = True)

    return {'success':False, 'msg':'Error'}


def download( py_fs, path, attachment = False ):
    '''
    下载或查看文件
    '''
    if py_fs.isdir(path): return HttpResponseBadRequest("400 bad request")
    if not py_fs.exists(path): raise Http404
    file = py_fs.open(path,'rb')
    import mimetypes
    inFileName = path.split('/')[-1]
    mt = mimetypes.guess_type(inFileName)
    response = HttpResponse(content_type=mt)
    if attachment:
        response['Content-Disposition'] = 'attachment; filename=%s' % inFileName
    response.write(file.read())
    return response


#@decorators.swfupload_cookies_auth
@decorators.ajax_request
@csrf_exempt

def upload(request):

    file_list = []

    #设置文件类型限制
    #allowed_extensions = 'jpg,jpeg,gif,png,pdf,swf,doc,docx,xls,\
    #log,xlsx,ppt,pptx,txt,c,py,cpp,go,class,java'.split(',')
    
    #使用xmlhttpRequest进行请求
    if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
        path = request.META.get('HTTP_X_FILE_NAME')
        if not path: return HttpResponseBadRequest("400 bad request")
        root, path = splitPath( path.decode('UTF-8') )
        cur_fs = getFsFromKey( root )
        if not cur_fs: raise Http404
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
        if not cur_fs: raise Http404
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

    return JsonResponse({'success':True, 'file':file_list})

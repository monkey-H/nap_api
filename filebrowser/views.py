from django.conf import settings
from django.http import HttpResponse, Http404, JsonResponse, HttpResponseBadRequest
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
import os
import datetime
from filebrowser import decorators
from settings import sources

def test_hello(request):
#    return HttpResponse("hello world")
    return render(request, 'filebrowser/index.html')

def dirToJson( inFs, path = '/', recursive = False):
    data = []
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
            ,'iconCls':iconCls
            ,'items':[]
        }
        # recursive and isdir ?
        if not isLeaf and recursive:
            row['items'] = dirToJson(inFs, path = fPath, recursive = recursive )

        data.append( row )
    return JsonResponse(data,safe=False)

def example( request ):
    d = { }
    return utils.renderWithContext(request, 'example.html', d )

def splitPath( inPath ):
    if not inPath:
        return None, None
    if inPath[0] == '/':
        inPath = inPath[1:]
    root = inPath.split('/')[0]
    path = '/'.join(inPath.split('/')[1:])
    return root, path

def getFsFromKey( key ):
    if key in sources.keys():
        source = sources[key]
        cur_fs = source['cls']( **source['params'] )
        return cur_fs
    else:
        return None

@decorators.ajax_request
@csrf_exempt
def api( request ):
    cmd = request.POST.get('cmd', request.GET.get('cmd'))
    if not cmd: raise Http404

    # todo: remove these special cases
    if cmd == 'delete':
        root, path = splitPath( request.POST['file'] )
    elif cmd in ['view', 'download']:
        root, path = splitPath( request.GET['file'] )
    elif cmd == 'rename':
        root, path = splitPath( request.POST['oldname'] )
    elif cmd in ['newdir', 'get']:
        root, path = splitPath( request.POST['path'] )
    else:
        return HttpResponseBadRequest("400 bad request")

    if root:
        cur_fs = getFsFromKey(root)
        if not cur_fs: raise Http404
    else:
        return HttpResponseBadRequest("400 bad request")

    if cmd == 'get':
        return dirToJson(cur_fs, path, recursive = False)

    elif cmd == 'newdir':
        if cur_fs.exists(path):
            return HttpResponseBadRequest("directory already exists")
        cur_fs.makedir(path)
        return JsonResponse({'success':True})

    elif cmd == 'rename':
        # todo : handle FS level moves
        root2, path2 = splitPath( request.POST['newname'] )
        if not root2:
            return HttpResponseBadRequest("400 bad request")
        if root == root2:
            # same FS
            if not cur_fs.exists(path): raise Http404
            cur_fs.rename(path, path2)
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
        if not cur_fs.exists(path): raise Http404
        file = cur_fs.open(path, 'rb')
        return download( path, file)

    elif cmd == 'download':
        # todo redir to APACHE or OTHER
        if not cur_fs.exists(path): raise Http404
        file = cur_fs.open(path,'rb' )
        return download( path, file, attachment = True)

    return {'success':False, 'msg':'Erreur'}

def download( inFilePath, inFileObj, attachment = False ):
    import mimetypes
    inFileName = inFilePath.split('/')[-1]
    mt = mimetypes.guess_type(inFileName)
    response = HttpResponse(content_type=mt)
    if attachment:
        response['Content-Disposition'] = 'attachment; filename=%s' % inFileName
    response.write(inFileObj.read())
    return response


#@decorators.swfupload_cookies_auth
@decorators.ajax_request
@csrf_exempt
def upload(request):
    path = request.META.get('HTTP_X_FILE_NAME')
    print path

    file_list = []

    #allowed_extensions = 'jpg,jpeg,gif,png,pdf,swf,doc,docx,xls,\
    #log,xlsx,ppt,pptx,txt,c,py,cpp,go,class,java'.split(',')
    
    if path and request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
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

    else:
        root, path = splitPath( request.POST['path'].decode('UTF-8') )
        cur_fs = getFsFromKey( root )
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

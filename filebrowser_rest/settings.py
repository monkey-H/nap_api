#
# add your datasources to the 'sources' variable
#
#   *  cls parameter is the PyFilesystem type (see http://packages.python.org/fs/filesystems.html)
#   *  set custom PyFilesystem parameters in the 'params' dictionnary.
#

from fs.osfs import OSFS

sources = {
    'localfolder':{
        'cls':OSFS
        ,'params':{
            'root_path':r'/home/monkey/Documents/filebrowser/monkey'
            #,'encoding':
        }
    }
    ,'NAP':{
        'cls':OSFS
        ,'params':{
            'root_path':r'/home/monkey/cshuo/fs/test2'
            #,'encoding':
        }
    }

}

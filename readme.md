author: cshuo
restful api for nap application 

rest_api: 应用的状态信息

filebrowser:访问主机文件系统

### api类型:
1. 请求一个文件夹下的目录树  
  --方法: POST  
  --url: /fs/filebrowser/api/  
  --参数:   
	* cmd="get" 
    * path="key/path" (key 为配置文件中主机提供的文件系统的根目录,目前只有localfolder可选,path为请求的路径)
  --返回值: json格式数据  

2. 新建目录
  --方法: POST  
  --url: fs/filebrowser/api/   
  --参数:  
    * cmd="newdir"
	* path="key/path" (允许递归构建目录)
  --返回值:  
    参数正确时,返回数据{'success':True},否则根据情况返回400,404  

3. 重命名
  --方法: POST  
  --url: fs/filebrowser/api/  
  --参数:  
    * cmd="rename"
	* oldname="key/path"
	* newname="key/path"
  --返回值:  
    参数正确时,返回{'success': True},错误时返回400    

4. 删除文件或文件夹  
  --方法: POST  
  --url: fs/filebrowser/api/  
  --参数:  
    * cmd="delete"
	* path="key/path"
  --返回值:  
    参数正确时,返回{'success': True},错误时返回404  

5. 查看文件:
  --方法: GET  
  --url: fs/filebrowser/api/  
  --参数:  
    * cmd="view"
	* file="key/path"
  --返回值:  
    参数正确时,返回文件的内容,错误时返回404  
    
6. 下载文件:
  --方法: GET  
  --url: fs/filebrowser/api/  
  --参数:   
    * cmd="download"
	* file="key/path"
  --返回值:   
    参数正确时,下载文件,错误时返回404  
    

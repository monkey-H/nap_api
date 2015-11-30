import MySQLdb
import sys
import commands
import os
import shutil
from docker import Client

class AppTransac(object):	

	def deal_data(self,db_tuple):
		ret_data = []
		for item in db_tuple:
			ret_data.append(item[0])
		return ret_data
			
	def __init__(self, user, password):
		self.user = user
		self.password = password
		self.db = MySQLdb.connect('192.168.56.105', user, password, user)
		self.cursor = self.db.cursor()

	def service_list(self, project_name):
		srv_list = []
		self.cursor.execute("select name from service where project='%s'" % project_name)
		data = self.cursor.fetchall()
		name_list = self.deal_data(data)
		for name in name_list:
			srv_dic = {}
			srv_dic['name'] = name
			srv_dic['ip'] = self.machine_ip(name)
			srv_dic['status'] = self.get_status(name)
			ports = self.get_port(name)
			if not len(ports):
				srv_dic['port'] = '-'
			else:
				expose_port = []
				for _, val in ports:
					expose_port.append(val[0]['HostPort'])
				srv_dic['port'] = expose_port
			srv_list.append(srv_dic)
		return srv_list
			
	
	def project_list(self, begin, length):
		self.cursor.execute("select name, url from project limit %s,%s" % (begin, length))
		data = self.cursor.fetchall()
		return data

	def machine_ip(self, service_name):
		self.cursor.execute("select machine from service where name='%s'" % service_name)
                data = self.cursor.fetchone()
                self.cursor.execute("select ip from machine where id=%s" % data)
                data = self.cursor.fetchone()
                return data

	def get_net(self):
		self.cursor.execute("select net from info where name='%s'" % self.user)
                data = self.cursor.fetchone()
		return data[0]
	
	def get_volume(self):
		self.cursor.execute("select volume from info where name = '%s'" % self.user)
		data = self.cursor.fetchone()
		return data[0]

	#judge if project exist in mysql, return false
	def create_project(self, name, url):
		self.cursor.execute("select name from project where name='%s'" % name)
		data = self.cursor.fetchone()
		if data != None:
			return False, "project already exsit ! try another name !"
		if os.path.exists('/home/monkey/app/%s' % name):
			shutil.rmtree('/home/monkey/app/%s' % name)
		os.mkdir('/home/monkey/app/%s' % name)
		old = sys.stdout
		f = open(os.devnull, 'w')
		sys.stdout = f
		a,b = commands.getstatusoutput('git clone %s /home/monkey/app/%s && cd /home/monkey/app/%s && docker-compose up -d' % (url, name, name))
		sys.stdout = old
                self.cursor.execute("insert into project(name, url) values('%s', '%s')" % (name, url))
                self.db.commit()
		if not a:
			return True, "create project success"
		return True, "something happened when create project "

	#return 0 success, else false
	def destroy_project(self, name):
		old = sys.stdout
		f = open(os.devnull, 'w')
		sys.stdout = f
		a,b = commands.getstatusoutput('cd /home/monkey/app/%s && docker-compose stop && docker-compose rm' % (name))
		print b;
		print a;
		if os.path.exists('/home/monkey/app/%s' % name):
			shutil.rmtree('/home/monkey/app/%s' % name)
                self.cursor.execute("delete from service where project = '%s'" % name)
                self.cursor.execute("delete from project where name = '%s'" % name)
                self.db.commit()
		sys.stdout = old
		if not a:
			return True
		return False 

	def get_logs(self, name):
		cip = self.machine_ip(name)
		print cip[0]
		cli = Client(base_url=cip[0], version='1.21')
		logs = cli.logs(container=name)
		return logs
	
	def get_status(self, name):
		cip = self.machine_ip(name)
		cli = Client(base_url=cip[0], version='1.21')
		detail = cli.inspect_container(name)
		return detail['State']['Status']

	def get_port(self, name):
		cip = self.machine_ip(name)
		cli = Client(base_url=cip[0], version='1.21')
		detail = cli.inspect_container(name)
		return detail['HostConfig']['PortBindings']

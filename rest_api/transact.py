import MySQLdb
import sys
import commands
from docker import Client

class AppTransac(object):
	def __init__(self, ip, user, password, database):
		self.ip = ip
		self.user = user
		self.password = password
		self.database = database
		self.db = MySQLdb.connect(ip, user, password, database)
		self.cursor = self.db.cursor()

	def service_list(self, project_name):
		srv_list = []
		self.cursor.execute("select name from service where project='%s'" % project_name)
		data = self.cursor.fetchall()
		name_list = self.deal_data(data)
		for name in name_list:
			srv_dic = {}
			srv_dic['name'] = name
			srv_dic['ip'] = self.machine_ip(name).split(':')[0]
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


	def project_list(self):
		poj_list = []
		self.cursor.execute("select * from project")
		data = self.cursor.fetchall()
		for d in data:
			poj_dic = {}
			poj_dic['name'] = d[0]
			poj_dic['url'] = d[1]
			poj_list.append(poj_dic)
		return poj_list


	def machine_ip(self, service_name):
		self.cursor.execute("select machine from service where name='%s'" % service_name)
                data = self.cursor.fetchone()
                self.cursor.execute("select ip from machine where id=%d" % data)
                data = self.cursor.fetchone()
                return data[0]

	def get_net(self):
		self.cursor.execute("select net from info where name='%s'" % self.user)
                data = self.cursor.fetchone()
		return data[0]

	def get_volume(self):
		self.cursor.execute("select volume from info where name = '%s'" % self.user)
		data = self.cursor.fetchone()
		return data[0]

	def create_project(self, name, url):
		a = commands.getoutput('cd /home/monkey/app && mkdir %s &&  git clone %s %s && cd %s && docker-compose up' % (name, url, name, name))
		print a
                self.cursor.execute("insert into project values('%s', '%s')" % (name, url))
                self.db.commit()

	def get_logs(self, name):
		cip = self.machine_ip(name)
		cli = Client(base_url=cip, version='1.21')
		logs = cli.logs(container=name)
		return logs

	def get_status(self, name):
		cip = self.machine_ip(name)
		cli = Client(base_url=cip, version='1.21')
		detail = cli.inspect_container(name)
		return detail['State']['Status']

	def get_port(self, name):
		cip = self.machine_ip(name)
		cli = Client(base_url=cip, version='1.21')
		detail = cli.inspect_container(name)
		return detail['HostConfig']['PortBindings']

	def deal_data(self,db_tuple):
		ret_data = []
		for item in db_tuple:
			ret_data.append(item[0])
		return ret_data

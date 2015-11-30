import MySQLdb
import sys
import commands
import os
import shutil
from docker import Client

database_url = '192.168.56.105'
client_list = ['192.168.56.105:2376', '192.168.56.106:2376']


class AppTransac(object):
    @staticmethod
    def deal_data(db_tuple):
        ret_data = []
        for item in db_tuple:
            ret_data.append(item[0])
        return ret_data

    def __init__(self, user, password):
        self.user = user
        self.password = password

    @classmethod 
    def create_user(cls, new_user, new_password):
	# if user exsits, return false, else create
        new_db = MySQLdb.connect(database_url, 'root', 'monkey')
        new_cursor = new_db.cursor()
        new_cursor.execute("show databases;")
        database_list = new_cursor.fetchall()
        datbase_l = cls.deal_data(database_list)
        for item in datbase_l:
            if item == new_user:
                return [False, "user already exist"]

        new_cursor.execute("create database %s;" % new_user)
        new_cursor.execute("create user '%s'@'%s' identified by '%s';" % (new_user, '%', new_password))
        new_cursor.execute("grant all on %s.* to '%s'@'%s';" % (new_user, new_user, '%'))
        new_db.commit()
        new_db.close()

        # create some tables for this user
        user_db = MySQLdb.connect(database_url, new_user, new_password, new_user)
        user_cursor = user_db.cursor()
        user_cursor.execute("create table info(name char(50) not null, net char(50), volume char(50));")
        user_cursor.execute("create table machine(id int unsigned not null, ip char(50));")
        user_cursor.execute(
            "create table project(id int unsigned not null auto_increment primary key, name char(50), url char(50));")
        user_cursor.execute("create table service(name char(50), machine int unsigned, project char(50));")
        user_cursor.execute("insert into info values('%s', '%s', '%s_volume');" % (new_user, new_user, new_user))
        client_id = 0
        for client in client_list:
            user_cursor.execute("insert into machine values(%d, '%s');" % (client_id, client))
            client_id += 1
        # user_cursor.execute("insert into machine values(0, '192.168.56.105:2376');")
        # user_cursor.execute("insert into machine values(1, '192.168.56.106:2376');")
        user_db.commit()
        user_db.close()

        # something else need, net volume_from and soon
        for client in client_list:
            commands.getstatusoutput("ssh monkey@%s 'cd /volume_data && sudo mkdir %s'" % (client.split(":")[0], new_user))
            # still need mfsmount
            commands.getstatusoutput("ssh monkey@%s 'docker run -d --name %s -v /volume_data/%s:/data busybox'" % (client.split(":")[0], new_user+"_volume", new_user))

        return [True, "create user success"]

    def service_list(self, project_name):
        db = MySQLdb.connect(database_url, self.user, self.password, self.user)
        cursor = db.cursor()
        srv_list = []
        cursor.execute("select name from service where project='%s'" % project_name)
        data = cursor.fetchall()
        db.close()
        name_list = self.deal_data(data)
        for name in name_list:
            srv_dic = {}
            srv_dic['name'] = name
            srv_dic['ip'] = str(self.machine_ip(name)).split(":")[0]
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
        db = MySQLdb.connect(database_url, self.user, self.password, self.user)
        cursor = db.cursor()
        cursor.execute("select name, url from project limit %s,%s" % (begin, length))
        db.close()
        data = cursor.fetchall()
        return data

    def machine_ip(self, service_name):
        db = MySQLdb.connect(database_url, self.user, self.password, self.user)
        cursor = db.cursor()
        cursor.execute("select machine from service where name='%s'" % service_name)
        data = cursor.fetchone()
        cursor.execute("select ip from machine where id=%s" % data[0])
        data = cursor.fetchone()
        db.close()
        return data[0]

    def get_net(self):
        db = MySQLdb.connect(database_url, self.user, self.password, self.user)
        cursor = db.cursor()
        cursor.execute("select net from info where name='%s'" % self.user)
        data = cursor.fetchone()
        db.close()
        return data[0]

    def get_volume(self):
        db = MySQLdb.connect(database_url, self.user, self.password, self.user)
        cursor = db.cursor()
        cursor.execute("select volume from info where name = '%s'" % self.user)
        data = cursor.fetchone()
        db.close()
        return data

    # judge if project exist in mysql, return false
    def create_project(self, name, url):
        db = MySQLdb.connect(database_url, self.user, self.password, self.user)
        cursor = db.cursor()
        cursor.execute("select name from project where name='%s'" % name)
        data = cursor.fetchone()
        if data != None:
            return False, "project already exsit ! try another name !"
        if os.path.exists('/home/monkey/app/%s' % name):
            shutil.rmtree('/home/monkey/app/%s' % name)
        os.mkdir('/home/monkey/app/%s' % name)
        old = sys.stdout
        f = open(os.devnull, 'w')
        #sys.stdout = f
        a, b = commands.getstatusoutput(
            'git clone %s /home/monkey/app/%s && cd /home/monkey/app/%s && docker-compose up -d %s %s' % (url, name, name, self.user, self.password))
        sys.stdout = old
        cursor.execute("insert into project(name, url) values('%s', '%s')" % (name, url))
        db.commit()
        db.close()
        if not a:
            return True, "create project success"
        return True, "something happened when create project "

    # return 0 success, else false
    def destroy_project(self, name):
        # old = sys.stdout
        # f = open(os.devnull, 'w')
        # sys.stdout = f
        # a,b = commands.getstatusoutput('cd /home/monkey/app/%s && docker-compose stop && docker-compose rm' % (name))
        if os.path.exists('/home/monkey/app/%s' % name):
            shutil.rmtree('/home/monkey/app/%s' % name)

        # stop and rm container
        data = self.service_list(name)
        for item in data:
            url = str(item['ip']) + ':2376'
            cli = Client(base_url=url, version='1.21')
            cli.stop(container=item['name'])
            cli.remove_container(container=item['name'])

        db = MySQLdb.connect(database_url, self.user, self.password, self.user)
        cursor = db.cursor()
        cursor.execute("delete from service where project = '%s'" % name)
        cursor.execute("delete from project where name = '%s'" % name)
        db.commit()
        db.close()
        # sys.stdout = old

        return True

    def create_service(self, srv_name, srv_id, srv_project):
        db = MySQLdb.connect(database_url, self.user, self.password, self.user)
        cursor = db.cursor()
        cursor.execute("insert into service values('%s', %d,'%s')" % (srv_name, srv_id, srv_project))
        db.commit()
        db.close()

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

    def get_machine(self):
        db = MySQLdb.connect(database_url, self.user, self.password, self.user)
        cursor = db.cursor()
        cursor.execute("select ip from machine")
        data = cursor.fetchall()
        db.close()
        return self.deal_data(data)

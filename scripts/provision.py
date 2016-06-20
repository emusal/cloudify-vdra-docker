from cloudify import ctx
from cloudify.state import ctx_parameters as p
import urllib2
import json
import sys
import paramiko
import sys
import os
import os.path
"""
from kazoo.client import KazooClient
from kazoo.exceptions import NoNodeError 
from kazoo.exceptions import NodeExistsError
"""

def do_rsh(em_host, zookeeper_host,yaml_filename, target_type,hosts):

	user = 'udraapp'
	passwd = 'udra'
	localfile = '/tmp/zk_rsh'
	remotefile = '/home/udraapp/HOME/bin/zk_rsh'

	jinjaname = '/home/udraapp/HOME/data/blueprint/gen.py' 
	filename = '/home/udraapp/HOME/data/blueprint/' + yaml_filename	
	zk_data =  json.dumps({"yaml":filename,"hosts":hosts, "jinja":jinjaname})

	zk_buffer =  '/home/udraapp/HOME/bin/zookeeper/bin/zkCli.sh -server ' + zookeeper_host + ' << END\nset /nfv_configure/tks/provisioning/uem1/' + target_type + ' \'' + zk_data + '\'\nEND'

	with open(localfile,"wb") as f:
		f.write(zk_buffer)

	ssh = paramiko.SSHClient()
	ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
	print em_host, user, passwd
	ssh.connect(em_host, username=user, password=passwd)

	sftp = ssh.open_sftp()
	sftp.put(localfile, remotefile)
	sftp.close()
	command = 'sh ' + remotefile
	print "ftp connect success ", command
	ssh.exec_command(command)

	"""
	x = stdout.readlines()
	for line in x:
		print line
	"""

	ssh.close()




def do_zookeeper(hostip,zk_key,yaml_filename, hosts):


	#zk_key="/nfv_configure/tks/provisioning/uem1/peer_config"

	jinjaname = '/home/udraapp/HOME/data/blueprint/gen.py' 
	filename = '/home/udraapp/HOME/data/blueprint/' + yaml_filename	
	zk_data =  json.dumps({"yaml":filename,"hosts":hosts, "jinja":jinjaname})

"""
	host = hostip + ':2181'
	zk = KazooClient(hosts=host)
	zk.start()
	    
	try :
		print zk.exists(zk_key)
		stat = zk.set(zk_key, zk_data)
		print("Version: %s, data: %s" % (stat.version, zk_data.decode("utf-8")))
	except (NoNodeError, NodeExistsError):
		print "zk error"

"""



def do_ftp(hostip, ftp_user, ftp_passwd, localpath, remotepath):

	ssh = paramiko.SSHClient()
	ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
	ssh.connect(hostip, username=ftp_user, password=ftp_passwd)
	sftp = ssh.open_sftp()
	sftp.put(localpath, remotepath)
	sftp.close()
	ssh.close()


def do_wget(url):

	file_name = url.split('/')[-1]
	file_path = '/tmp/' + url.split('/')[-1]

	u = urllib2.urlopen(url)

	f = open(file_path, 'wb')
	meta = u.info()
	file_size = int(meta.getheaders("Content-Length")[0])

#	print "Downloading: %s Bytes: %s" % (file_name, file_size)

	file_size_dl = 0
	block_sz = 8192
	while True:
		buffer = u.read(block_sz)
		if not buffer:
			break

		file_size_dl += len(buffer)
		f.write(buffer)
		status = r"%10d  [%3.2f%%]" % (file_size_dl, file_size_dl * 100. / file_size)
		status = status + chr(8)*(len(status)+1)
#		print status,
	f.close()
	localpath = '/tmp/' + file_name
	remotepath = '/home/udraapp/HOME/data/blueprint/' + file_name
	return file_name, localpath, remotepath


def get_hostip(hostname, user, passwd):
	ssh = paramiko.SSHClient()
	ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
	ssh.connect('localhost', username=user, password=passwd)
	command = 'docker inspect --format \'{{ .NetworkSettings.IPAddress }}\' ' + hostname
	stdin, stdout, stderr = ssh.exec_command(command)
	x = stdout.readlines()
	for line in x:
		# delete new line
		line = line[:-1]
		return line


def get_configure(data):
	if data == None:
		filename = os.getcwd() + '/' + 'input.json' 
		f = open(filename, 'r')
		data = f.read()

	if data.startswith('\'') == True:
		data = data[1:-1]


	try :
		decoded = json.loads(data)

		source_yaml = decoded['yaml']
		target = decoded['target']
	except (ValueError, KeyError, TypeError):
		print "JSON format error"
		return None, None, None
	return source_yaml, target


#em_value = '{"yaml":"http://192.168.3.38:8888/blueprints/test/abnormal.yaml", "yaml_path":"data/blueprint/blueprint123.yaml", "target_type":"peer_config", "hosts":["udra1","udra2"]}'
#source_yaml, target_type, hosts = get_configure(em_value)

ctx.instance.runtime_properties['provision'] = p.em_value
source_yaml, target = get_configure(p.em_value)

if source_yaml == None:
	sys.stderr.write("\nExiting error on get_configure \n")
	sys.exit(0)

zookeeper_host = get_hostip('nfvdev-zookeeper1', 'vagrant', 'vagrant')
em_host = get_hostip('nfvdev-vem1', 'vagrant', 'vagrant')

if len(zookeeper_host) < 1 or len(em_host) < 1: 
	sys.stderr.write("\nExiting error on Docker inspect ip address \n")
	sys.exit(0)

yaml_filename, localpath, remotepath = do_wget(source_yaml)
do_ftp(em_host, 'udraapp', 'udra', localpath, remotepath)

for target_val in target:
	target_type = target_val['target_type']
	hosts = target_val['hosts']
	do_rsh(em_host, zookeeper_host,yaml_filename, target_type,hosts)

"""
zk_key='/nfv_configure/tks/provisioning/uem1/' + target_type
print zk_key
do_zookeeper(zookeeper_host, zk_key, yaml_filename, hosts)
"""






#!/usr/bin/env python
from __future__ import print_function
from xml.dom.minidom import parse
import xml.dom.minidom
import datetime
import os
import sys
from poolrate import poolrate

def writelog(data,cfg,filename):
	## write XML log file
	logdir = cfg['General']['log_dir']
	print('Fetching pool hashrate data ... ',end="")
	sys.stdout.flush()
	sum_pool_rate, pool_rate = poolrate(cfg)
	print('Done.')
	print('Logging into ' + logdir + filename + ' ... ',end="")
	sys.stdout.flush()
	log = '<?xml version="1.0"?>\n'
	time = filename.strip("log-").strip(".xml")
	log += "<data>\n\t<time>" + time + "</time>\n"
	log += "\t<SumPoolRate>" +sum_pool_rate + "</SumPoolRate>\n"
	log += "\t<WorkerPoolRate>" + pool_rate + "</WorkerPoolRate>\n"
	for miner in data:
		log += "\t<miner>\n"
		log += "\t\t<IP>" + miner[0] + "</IP>\n"
		log += "\t\t<Status>" + miner[1] + "</Status>\n"
		log += "\t\t<Elapsed>" + miner[2] + "</Elapsed>\n"
		log += "\t\t<TotalMH>" + miner[3] + "</TotalMH>\n"
		for dev_stat in miner[4]:
			log += "\t\t<dev>\n"
			log += "\t\t\t<DeviceElapsed>" + dev_stat[0] + "</DeviceElapsed>\n"
			log += "\t\t\t<TotalMH>" + dev_stat[1] + "</TotalMH>\n"
			log += "\t\t\t<MaxTemperature>" + dev_stat[2] + "</MaxTemperature>\n"
			log += "\t\t\t<ModuleNumber>" + str(dev_stat[3]) + "</ModuleNumber>\n"
			for temp in dev_stat[4]:
				log += "\t\t\t<Temperature>" + temp + "</Temperature>\n"
			for fan in dev_stat[5]:
				log += "\t\t\t<FanSpeed>" + fan + "</FanSpeed>\n"
			log += "\t\t</dev>\n"
		for pool_stat in miner[5]:
			log += "\t\t<pool>\n"
			log += "\t\t\t<URL>" + pool_stat[0] + "</URL>\n"
			log += "\t\t\t<Status>" + pool_stat[1] + "</Status>\n"
			log += "\t\t</pool>\n"
		log += "\t\t<MHS15min>" + miner[6] + "</MHS15min>\n"
		log += "\t\t<Error>" + miner[7] + "</Error>\n"
		log += "\t</miner>\n"
	log += "</data>"

	logfile = open(logdir + filename, 'w')
	logfile.write(log)
	logfile.close()
	print('Done.')

def readlog(logdir,filename):
	## read XML log file
	data=[]
	DOMTree = xml.dom.minidom.parse( logdir + filename )
	log = DOMTree.documentElement
	time = datetime.datetime.strptime(log.getElementsByTagName("time")[0].childNodes[0].data,"%Y_%m_%d_%H_%M")
	try: sum_pool_rate = log.getElementsByTagName("SumPoolRate")[0].childNodes[0].data
	except IndexError: sum_pool_rate = '0'
	try : pool_rate = log.getElementsByTagName("WorkerPoolRate")[0].childNodes[0].data
	except IndexError: pool_rate = '0'
	for minerXML in log.getElementsByTagName("miner"):
		miner=[]
		dev=[]
		pool=[]
		miner.append(minerXML.getElementsByTagName("IP")[0].childNodes[0].data)
		miner.append(minerXML.getElementsByTagName("Status")[0].childNodes[0].data)
		miner.append(minerXML.getElementsByTagName("Elapsed")[0].childNodes[0].data)
		miner.append(minerXML.getElementsByTagName("TotalMH")[0].childNodes[0].data)
		for dev_statXML in minerXML.getElementsByTagName("dev"):
			dev_stat=[]
			dev_stat.append(dev_statXML.getElementsByTagName("DeviceElapsed")[0].childNodes[0].data)
			dev_stat.append(dev_statXML.getElementsByTagName("TotalMH")[0].childNodes[0].data)
			dev_stat.append(dev_statXML.getElementsByTagName("MaxTemperature")[0].childNodes[0].data)
			dev_stat.append(dev_statXML.getElementsByTagName("ModuleNumber")[0].childNodes[0].data)
			temp=[]
			for tempXML in dev_statXML.getElementsByTagName("Temperature"):
				temp.append(tempXML.childNodes[0].data)
			dev_stat.append(temp)
			fan=[]
			for fanXML in dev_statXML.getElementsByTagName("FanSpeed"):
				fan.append(fanXML.childNodes[0].data)
			dev_stat.append(fan)
			dev.append(dev_stat)
		for pool_statXML in minerXML.getElementsByTagName("pool"):
			pool_stat=[]
			pool_stat.append(pool_statXML.getElementsByTagName("URL")[0].childNodes[0].data)
			pool_stat.append(pool_statXML.getElementsByTagName("Status")[0].childNodes[0].data)
			pool.append(pool_stat)
		miner.append(dev)
		miner.append(pool)
		try:
			miner.append(minerXML.getElementsByTagName("MHS15min")[0].childNodes[0].data)
		except:
			miner.append('0')
		try:
			miner.append(minerXML.getElementsByTagName("Error")[0].childNodes[0].data)
		except:
			miner.append('0')
		data.append(miner)

	return (data,time,sum_pool_rate,pool_rate)

if __name__ == '__main__':
	logdir = './log/'
	logname = 'log-example.xml'
	(data,time) = readlog(logdir,logname)

	for miner in data:
		print(miner[0] + ': ' + miner[1] + ' ' + miner[2] + ' ' + miner[3])
		i = 1
		for dev_stat in miner[4]:
			print('\tModule #' + str(i) + ':')
			print('\t\tDevice Elapsed: ' + dev_stat[0])
			print('\t\tTotal MH: ' + dev_stat[1])
			print('\t\tTemperature: ' + dev_stat[2])
			print('\t\tModules Number: ' + str(dev_stat[3]))
			print('\t\tTemperature List: ' + ','.join(dev_stat[4]))
			print('\t\tFan Speed List: ' + ','.join(dev_stat[5]))
			i += 1

		i = 1
		for pool_stat in miner[5]:
			print('\tPool #' + str(i) + ':')
			print('\t\tURL: ' + pool_stat[0])
			print('\t\tStatus: ' + pool_stat[1])
			i += 1
		print("------------------------------------------------------------------------------")


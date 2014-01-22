#-*- coding: UTF-8 -*-

import datetime
import time

def unixTimeStamp():
	return int(time.mktime(datetime.datetime.now().timetuple()))

def timestamp2datetime(timestamp):
	return datetime.datetime.fromtimestamp(int(timestamp)).strftime('%Y-%m-%d %H:%M:%S')

def __test():
	print unixTimeStamp()
	print timestamp2datetime(1389411900)

if __name__ == '__main__':
	__test()
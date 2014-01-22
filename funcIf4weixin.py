# -*- coding: UTF-8 -*-

import xml.etree.ElementTree as ET
import timeHelper


RESPONSE_TEXT_TEMPLATE = '''
<xml>
<ToUserName><![CDATA[{TO_USER}]]></ToUserName>
<FromUserName><![CDATA[{FROM_USER}]]></FromUserName>
<CreateTime>{TIME_STEMP}</CreateTime>
<MsgType><![CDATA[text]]></MsgType>
<Content><![CDATA[{RESPONSE_CONTENT}]]></Content>
</xml>
'''  

class msgHandler:
    def __init__(self, data):
        self.data = data
        self.dict = self._xmlToDict(self.data)
        if self.dict['MsgType'] == 'event':
            self.worker = eventHandler(self.dict['FromUserName'],self.dict['Event'])
        else:
            self.worker = txtmsgHandler(self.dict['FromUserName'],self.dict['Content'])

    def response(self):
        responseDict = self.responseDict()
        text = self.responseXML(responseDict)
        return text
    
    
    def _xmlToDict(self, xmlText):
        xmlDict = {}
        itemlist = ET.fromstring(xmlText)
        for child in itemlist:
            xmlDict[child.tag] = child.text
        print xmlDict
        return xmlDict
    
    def responseXML(self, dataDict):
        if dataDict:
            text = RESPONSE_TEXT_TEMPLATE 
            for key, value in dataDict.items():
                parameter = '{%s}' % key
                text = text.replace(parameter, value)
            print text
        else:
            text = ''
        return text
    
    def responseDict(self):
        responseDict = {}
        try:
            responseDict['RESPONSE_CONTENT'] = self.worker.response.encode('UTF-8')
            responseDict['TO_USER'] = self.dict['FromUserName']
            responseDict['FROM_USER'] = self.dict['ToUserName']
            responseDict['TIME_STEMP'] = str(timeHelper.unixTimeStamp())
        except:
            pass
        return responseDict
    
    
class eventHandler:
    MSG_WELCOME = u'欢迎您关注我，想了解我，就请发送“帮助”或“？”'
    def __init__(self, user, event):
        if event == 'subscribe':
            self.response = self.MSG_WELCOME


class txtmsgHandler:
    MSG_HELP = u'''我会记录您对我说的除“查询”和“帮助”以外的所有的话，“查询”会得到您最后一次对我说的话
'''
    MSG_SUCCESS = [u'存储完成', u'我存好了，随时来查哦',u'搞定，收工']

    def __init__(self, user, reqMsg):
        self.req = reqMsg.lower()
        self.db = simpledb(user)
        self.response = self.MSG_HELP
        self._handle_req()            

    def _handle_req(self):
        if self.req in ['help', '帮助', '?', u'？']: return
        if self.req in ['cx', '查询']: return self.chaxun()
        else: return self.jilu() 

    def chaxun(self):
        timepoint, content = self.db.chaxun()
        self.response = u'您在{}说过：{}'.format(timepoint, content)
        pass
    
    def jilu(self):
        self.db.jilu(self.req)
        self.response = self._get_success_response()
    
    def _get_success_response(self):
        import random
        return self.MSG_SUCCESS[random.randint(0,len(self.MSG_SUCCESS)-1)]

import os
import sqlite3
import timeHelper
class simpledb:
    def __init__(self, dbName):
        dbPath = os.path.join(os.getcwd(), 'DB')
        if not os.path.isdir(dbPath):
            os.mkdir(dbPath) 
        name = os.path.join(dbPath, dbName+'.db')
        print name
        createNeeded = False
        if not os.path.isfile(name):
            print "First Time Store, Create DB"
            createNeeded = True
        self.conn = sqlite3.connect(name)
        self.c = self.conn.cursor()
        if createNeeded:
            self._create_db()  
            
    def __del__(self):
        #本来想实现数据库文件可以手动删除的，但是因为sqlite的bug，close之后文件也没关闭，所以这个代码就浪费了。理想是好的，仍然保留在这里
        self.conn.close()
        
    def _create_db(self):
        self.c.execute('''CREATE TABLE yulu
             (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, timestamp INTEGER, content text)''')
        self.c.execute('''CREATE INDEX dateIndex ON yulu(timestamp)''')
        self.conn.commit()

    def jilu(self, content):
        timestamp = timeHelper.unixTimeStamp()
        self.c.execute('''INSERT INTO yulu (timestamp, content) VALUES({},'{}')'''.format(timestamp,content))
        self.conn.commit()
            
    def chaxun(self):
        self.c.execute('''SELECT * from yulu ORDER BY id DESC LIMIT 1''')
        try:
            id,timestamp,content = self.c.fetchone()
            timepoint = timeHelper.timestamp2datetime(timestamp)
        except:
            timepoint = '-'
            content = '-'
        return timepoint, content

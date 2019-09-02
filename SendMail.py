#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
    @file   SendMail.py
    @date   2014/01/08
    @author 조용규  (dydrb422@naver.com)
    @brief  메일송신에 사용할 클래스를 정의해놓은 스크립트파일.
    @section    수정사항
        - 2014/01/08    최초작성 (use mutt or use smtplib)
        - 2014/01/10    여러 SMTP서버를 사용하도록 클래스 수정. 파일전송시 한글파일명 송신되도록 수정(RFC 2047적용)
        - 2014/09/02    인증필요없는 inmail.gabia.com 사용가능하도록 기능추가. SetLogin 정보 미사용시 미인증처리
'''

'''
    @Memo
        base        port 25
        STARTTLS    port 587
        SSL         port 465
'''
from subprocess import Popen, PIPE
import smtplib
import sys
import os
import copy
#from stdio import GLogging

#smtp 사용을 위한 import
import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText
from email import Encoders
from email import Utils
from email.header import Header

import base64    #base64 encoding decoding
import urllib    #url encoding decoding

'''
    @class    SendMail
    @date    2014/01/08
    @brief    mutt 클라이언트를 이용한 메일송신과 python smtp 를 이용한 메일송신 두가지모드를 제공
            smtp는 google의 smtp 사용. 구글 gmail의 계정 및 비밀번호 필요함
            여러파일첨부 가능, 단 지금은 한글파일명은 파일이 깨지므로 영어파일만 가능함.(14/01/08)
            한글파일명 가능. naver, nate, gmail, gabia 등에서 수신 테스트완료(14/01/10)

            현재는 사용을 위해서 SendMail object 내 smtp host 변수에 smtp 서버를 설정해야 한다.
'''
class SendMail:
    __str_logdir = './'
    __str_from = ''
    __str_to = ''
    __str_passwd = ''
    __list_to = []
    __list_file = []
    __str_title = ''
    __str_text = ''
    __use_smtp = True
    __use_auth = False
    __smtp_host = 'smtp.google.com'
    __smtp_port = 587
    __charset = 'utf-8'

    # @brief    생성자?함수
    def __init__(self, logdir ='./'):
        self.SetLogDir(logdir)

    def __del__(self):
        self.Clear()

    # @brief    모든값을 삭제
    def Clear(self):
        self.__str_from = ''
        self.__str_passwd = ''
        self.__str_to = ''
        emlist = []
        self.__list_to = copy.deepcopy(emlist)
        emlist2 = []
        self.__list_file = copy.deepcopy(emlist2)
        self.__str_title = ''
        self.__str_text = ''
        self.__str_file = ''
        self.__use_smtp = True
        self.__use_auth = False
        self.__smtp_host = 'smtp.google.com'
        self.__smtp_port = 587
        self.__charset = 'utf-8'

    # @brief    제목,내용,첨부파일등만 초기화.
    def ClearText(self):
        emlist = []
        self.__list_to = copy.deepcopy(emlist)
        emlist2 = []
        self.__list_file = copy.deepcopy(emlist2)
        self.__str_title = ''
        self.__str_text = ''
        self.__str_file = ''

    def SetLogDir(self, str_logdir):
        getlen = len(str_logdir)
        if getlen > 0:
            if str_logdir[getlen-1] == '/':
                self.__str_logdir = str_logdir[:getlen-1]
            else:
                self.__str_logdir = str_logdir
            #self.__logger = GLogging("INFO", "%s/SendMail.log" %(self.__str_logdir))

    #def WriteLog(self, str_log):
        #self.__logger.WriteLog(str_log)

    '''
        @breif    SMTP를 사용하여 메일을 송신하는 설정. 해당함수 미호출시 mutt이용
                사용할 SMTP서버의 호스트와 포트입력
                기본값은 구글의 gmail
    '''
    def SetUseSmtp(self, host='smtp.google.com', port=587):
        self.__use_smtp = True
        self.__smtp_host = host
        self.__smtp_port = port

    # @brief    SMTP 송신을 위한 계정계정정보 
    def SetSmtpLogin(self, login, passwd):
        self.__use_auth = True
        self.__str_from = copy.deepcopy(login)
        self.__str_passwd = copy.deepcopy(passwd)

    # @brief    SMTP 송신 메일정보 설정
    #           inmail일경우 로그인필요없으므로 송신정보만 set
    def SetSmtpFrom(self, mfrom):
        self.__str_from = copy.deepcopy(mfrom)

    # @brief    메일송신을 위한 캐릭터셋 설정
    def SetCharset(self, charset):
        self.__charset = charset

    # @brief    메일의 내용을 추가함.
    def SetTitle(self, str_title):
        self.__str_title = str_title
    
    def SetText(self, str_text):
        self.__str_text = str_text
        self.__str_text += "<br>"
    
    # @brief    메일의 내용을 추가함. 호출시마다 내용추가
    def AddText(self, str_text):
        self.__str_text += str_text
        self.__str_text += "<br>"

    # @brief    메일을 받을 메일주소를 추가함. 연속적으로 호출하면 계속추가된다.
    def AddTargetMail(self, str_to):
        self.__list_to.append(str_to)

    def AddTargetMailList(self, list_to):
        self.__list_to += list_to

    # @brief    메일에 첨부할 파일을 추가함. 연속적으로 호출하면 파일이 계속추가된다.
    def AddSendFile(self, str_file):
        if os.path.isfile(str_file):
            self.__list_file.append(str_file)
        else:
            raise Exception(-1, 'unknown file (filename : '+str_file+')')

    '''
        @brief    mutt 클라리언트를 이용하여 메일을 송신하기위한 커맨드라인 명령어를 문자열로 받는다.
                메일 송신정보가 미리 저장되어있지 않은경우(수신메일주소, 내용등) Exception 발생
    '''
    def GetSendString(self):
        if len(self.__list_to) == 0:
            raise Exception(-1, 'empty target mail list')
        elif len(self.__str_title) == 0:
            raise Exception(-1, 'empty title of mail')
        elif len(self.__str_text) == 0:
            raise Exception(-1, 'empty text of mail')
        else:
            str_targetlist = ''
            for target in self.__list_to:
                str_targetlist += target
                str_targetlist += ' '
            str_cmd = 'echo "'+self.__str_text+'" | mutt -s "'+self.__str_title+'" '+str_targetlist+' '
            str_filelist = ''
            if len(self.__list_file) > 0:
                for target_file in self.__list_file:
                    str_filelist += target_file
                    str_filelist += ' '
                str_cmd += ' -a '
                str_cmd += str_filelist
            return str_cmd

    '''
        @brief    클래스에 저장된 정보를 이용하여 메일을 송신한다.
                이전에 SetUseSmtp가 호출되었으면 smtp 를 이용하여 메일을 송신하고
                그렇지 않을경우 리눅스의 mutt 클라이언트를 이용하여 메일을 송신한다.
    '''
    def Send(self):
        if self.__use_smtp == False:
            self.__SendByMutt()
        else:
            self.__SendBySmtp()

    '''
        @brief    linux mutt 메일클라이언트를 이용한 커맨드라인 메일송신함수
    '''
    def __SendByMutt(self):
        str_send = self.GetSendString()
        #gLogger.WriteLog(str_send)
        p = Popen(str_send, shell=True, stdout=PIPE, stderr=PIPE)

    '''
        @brief    메일송신을 위한 MIME 정의
    '''
    def __SetBySmtp(self):
        if len(self.__charset) == 0:
            raise Exception(-1, "empty Character Set of SendMail")
        COMMASPACE = ", "
        msg = MIMEMultipart("alternative")
        msg["From"] = self.__str_from
        msg["To"] = COMMASPACE.join(self.__list_to)
        msg["Subject"] = Header(s=self.__str_title, charset=self.__charset)
        msg["Date"] = Utils.formatdate(localtime = 1)
        msg.attach(MIMEText(self.__str_text, "html", _charset=self.__charset))
        if len(self.__list_file) > 0 :
            for target in self.__list_file:
                part = MIMEBase("application", "octet-stream")
                part.set_payload(open(target, "rb").read())
                Encoders.encode_base64(part)

                # RFC 2047 방식을 이용한 한글파일명 파일전송
                file_target = '=?utf-8?b?'+base64.b64encode(os.path.basename(target))+'?='
                part.add_header("Content-Disposition", "attachment; filename=\"%s\"" % file_target)
                msg.attach(part)
            
                # RFC 2231 방식. 추후개발.(현재 오류있음)
                '''
                file_target = "UTF-8''\""+urllib.quote(os.path.basename(target))+"\""
                #part.add_header("Content-Transfer-Encoding", "base64")
                part.add_header("Content-Disposition", "attachment; filename*=%s" % file_target)
                msg.attach(part)
                '''
        return msg

    '''
        @brief    메일송신용으로 만든 message 를 SMTP 서버를 이용하여 송신한다.
                STARTTLS 사용.
        @warning    
            * python smtplib 사용할때 주의할점
             사용할 SMTP서버의 인증방식이 PLAIN, LOGIN, DIGEST-MD5, CRAM-MD5 중  CRAM-MD5 일경우
             smtplib의 기본이므로 그대로 사용하면 되나 다른 인증방식을 사용하는 SMTP서버를 사용해야 할 경우
             smtplib 상속하여 변경후 사용해야 한다.
                    
    '''
    def __SendBySmtp(self):
        msg = self.__SetBySmtp()
        server = smtplib.SMTP("%s:%d"%(self.__smtp_host, self.__smtp_port))
        #server.helo()
        server.ehlo()
        if self.__use_auth:
            server.starttls()
        server.ehlo()
        try:
            if self.__use_auth:
                server.login(self.__str_from, self.__str_passwd)
            result = server.sendmail(self.__str_from, self.__list_to, msg.as_string())
            server.close()
            self.__SendLog()
        except smtplib.SMTPAuthenticationError, e:
            raise Exception(str(e))
            #self.WriteLog(u"Error : %s 계정 로그인 실패"%(self.__str_from))
            #self.WriteLog(e)
            


    '''
        @brief    현재 메일에 세팅된 내용에 대해 SendMail 로그로 출력한다.
                보통 메일송신 완료후 출력하도록 한다.
    '''
    def __SendLog(self):
        cc = ''
        for tc in self.__list_to:
            cc += tc
            cc += '    '
        addf = ''
        for tf in self.__list_file:
            addf += tf
            addf += '    '
        string = "\n"\
                 "From : %s\n"\
                 "To : %s\n"\
                 "Title : %s\n"\
                 "Text : %s\n"\
                 "File : %s\n"\
                 %(self.__str_from, cc, self.__str_title, self.__str_text, addf)
        #self.WriteLog(string)


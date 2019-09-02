#!/usr/bin/env python
#-*-coding:utf-8-*-

# 아래 설정은 해외망에 대해 geoip 를 사용하며 국내망만 krisp 로 한번더 검색에 사용하므로
# 해외망 데이터베이스를 받을 필요가 없을 경우 True
_ONLY_KR = True
# krisp csv 파일을 다운로드할 경로
_KRISP_FILEURL = ""
# gz 파일명
_TARGET_GZ = ""
# csv 파일명
_TARGET_CSV = ""
# csv to dat 파일변환할 실행명령 (scheme 파일참조)
_CREATE_CMD = ""
if _ONLY_KR:
    _KRISP_FILEURL = "http://mirror.oops.org/pub/oops/libkrisp/data/v2/krisp.csv.gz"
    _TARGET_GZ = "./krisp.csv.gz"
    _TARGET_CSV = "./krisp.csv"
    _CREATE_CMD = "sqlite3 krisp.dat < ./schemeKR"
else:
    _KRISP_FILEURL = "http://mirror.oops.org/pub/oops/libkrisp/data/v2/krisp-geoip.csv.gz"
    _TARGET_GZ = "./krisp-geoip.csv.gz"
    _TARGET_CSV = "./krisp-geoip.csv"
    _CREATE_CMD = "sqlite3 krisp.dat < ./scheme"

"""
    다음의 변수는 서버설정에 맞게 바꿔주어야한다.
    @params 
        _DIR_KRISPDATA      krisp.dat 파일이 저장될 경로
        _MY_IDCNAME         메일발송시 idc 구분할 문자
        _UPDATE_CYCLE       krisp dbfile을 업데이트 할 주기 (krisp-geoip 파일은 1달에 한번 업데이트되나 
                                                            1주일주기로 체크하기로 한다.)

"""

_DIR_KRISPDATA = "./database/"
_MY_IDCNAME = "Test"
_UPDATE_CYCLE = 300


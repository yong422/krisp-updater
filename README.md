KRISP database updater
======================

# Description

KRISP 사용을 위한 database 파일 다운로드 및 sqlite3 database 파일 생성 스크립트 데몬

# Requirement

Python 2.7 <

# Usage

- 해당 프로젝트를 실행할 디렉토리에 전체 디렉토리로 추가
- krisp_updater_conf.py 설정파일내 값을 수정하며 파일내 comment 참조
- krisp_updater 스크립트 파일내 업데이트 기록 수신 메일 변경

```bash
# 스크립트 데몬 시작
./krisp_updater --start
```

# TODO

- admin mail 등의 config 변경
- 컨벤션 적용

# config.py
from pathlib import Path

# DB 연결 설정
DB_CONFIG = {
    "host": "localhost",
    "user": "your_username",
    "password": "your_password",
    "dbname": "postgres",
    "port": 54321
}

# 기타 고정 설정값이 있다면 여기에 추가
DEFAULT_SEARCH_DIRS = ['.', './data', './source']
LOG_FILE_PATH = "insert_errors.log"

# 상태 및 진행률 변수
status_var = None
progress_var = None

# 경로 관련 변수
file_path_var = None
destination_path = None
filename_list_path = None
#base_path = None
base_path = Path("F:/SAMPLE/")

# 파일 복사 관련 변수
tags = None
conn = None
cur = None
update_copy = None
error_log = []
filename_entry = None
filename_list = None
copy_tag_mode = None
<<<<<<< HEAD
batch_size = 1000
=======
copy_file_mode = None
batch_size = 1000
select_csv = None
dir_count = None

# DB 쿼리 관련 변수
select_query = None
select_options = None
checkboxoption = 0
select_results = []
>>>>>>> 1a8b8f7 (update)

# db_utils.py
import psycopg2
import config
import shutil
from tkinter import messagebox
from pathlib import Path
from datetime import datetime
<<<<<<< HEAD
=======
from psycopg2.extras import execute_values
import csv
from tkinter import simpledialog, filedialog
import config
>>>>>>> 1a8b8f7 (update)

# ------------------------- DB 연결 -------------------------
def connect_to_db(host_entry, user_entry, password_entry):
    host = host_entry.get()
    user = user_entry.get()
    password = password_entry.get()

    if not host or not user or not password:
        #messagebox.showwarning("입력 오류", "모든 필드를 입력하세요.")
        config.status_var.set("❌ DB 연결 실패: 모든 필드를 입력하세요.")
        return None

    try:
        config.conn = psycopg2.connect(
            host=host,
            dbname="postgres",
            user=user,
            password=password,
            port=54321
        )
        #messagebox.showinfo("DB 연결 성공", "DB에 성공적으로 연결되었습니다.")
        config.status_var.set("✅ DB 연결 성공!")
        config.cur = config.conn.cursor()
        #return config.conn
    except Exception as e:
        #messagebox.showerror("DB 연결 실패", str(e))
        config.status_var.set(f"❌ DB 연결 실패: {e}")
        print(f"[오류] DB 연결 실패: {e}")
        return None
<<<<<<< HEAD
    
# ------------------------- CSV 데이터 -> DB 업데이트 -------------------------
def insert_fileinfo_record(row, user_tags):
=======
# ------------------------- DB 연결 해제 -------------------------
def disconnect_from_db():
    if config.conn:
        try:
            config.cur.close()
            config.conn.close()
            #messagebox.showinfo("DB 연결 해제", "DB 연결이 해제되었습니다.")
            config.status_var.set("✅ DB 연결 해제")
        except Exception as e:
            #messagebox.showerror("DB 연결 해제 실패", str(e))
            config.status_var.set(f"❌ DB 연결 해제 실패: {e}")
            print(f"[오류] DB 연결 해제 실패: {e}")
    else:
        #messagebox.showwarning("DB 연결 상태", "현재 DB에 연결되어 있지 않습니다.")
        config.status_var.set("❌ 현재 DB에 연결되어 있지 않습니다.")

# ------------------------- CSV 데이터 -> DB 조회 -------------------------
def execute_and_display_query(query, tag_check):

    conditions = None
    if tag_check == 0:
        if query == "":
            conditions = (f"1=1 LIMIT 10")
        else: 
            conditions = query
    elif tag_check == 1:
        conditions = (f"tag && ARRAY['{query}']")

    full_query = f"SELECT * FROM fileinfo WHERE {conditions}"

    if tag_check == 1:
        if query == "":
            full_query = "SELECT DISTINCT unnest(tag) AS Unique_Tag FROM fileinfo WHERE tag IS NOT NULL;"

    print(f"Executing query: {full_query}")
    config.status_var.set("DB 조회 중...")
    config.select_results = select_fileinfo_records(full_query) 
    
    return config.select_results

def select_fileinfo_records(query):
    if not config.conn:
        #messagebox.showwarning("DB 연결 상태", "현재 DB에 연결되어 있지 않습니다.")
        config.status_var.set("❌ 현재 DB에 연결되어 있지 않습니다.")
        return []

    try:
        config.cur.execute(query)
        rows = config.cur.fetchall()  # ⚡ 수정: fetchmany로 변경하여 limit 적용
        column_names = [desc[0] for desc in config.cur.description]
        if not rows:
            #messagebox.showinfo("조회 결과", "조회된 데이터가 없습니다.")
            config.status_var.set("❌ 조회된 데이터가 없습니다.")
            return []
        return rows, column_names
    except Exception as e:
        print(f"[오류] DB 조회 실패: {e}")
        #messagebox.showerror("DB 조회 실패", str(e))
        config.status_var.set(f"❌ DB 조회 실패")
        config.conn.rollback()
        return []

# ------------------------- CSV 데이터 -> DB 삽입 -------------------------
def insert_fileinfo_records(rows, user_tags, batch_size=5000):
>>>>>>> 1a8b8f7 (update)
    now = datetime.now()
    config.base_path = Path(r"\\192.168.2.22\SAMPLE")

    try:
        file_name = row.get('fileName')
        prefix = file_name[:3] if file_name else 'UNK'
        full_path = str(config.base_path / prefix / (file_name or 'unknown'))

        # CSV 파일 내의 tags와 user_tags 병합
        csv_tags = row.get('tags', [])
        if isinstance(csv_tags, str):
            csv_tags = [csv_tags]  # 문자열일 경우 리스트로 변환
        combined_tags = list(set(csv_tags + (user_tags if isinstance(user_tags, list) else [user_tags] if user_tags else [])))

        config.cur.execute("""
            INSERT INTO fileinfo (
                sha256, 
                originalFilename, 
                fileName, 
                path, 
                fileSize, 
                mimeType, 
                extension, 
                tag, 
                createdTime, 
                lastModifyTime
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (sha256) DO UPDATE SET
                tag = (
                    SELECT ARRAY(
                        SELECT DISTINCT trim(t)
                        FROM unnest(
                            COALESCE(fileinfo.tag, ARRAY[]::TEXT[]) ||
                            COALESCE(EXCLUDED.tag, ARRAY[]::TEXT[])
                        ) AS t
                        WHERE trim(t) <> ''
                    )
                ),
                originalFilename = CASE
                    WHEN is_empty_or_placeholder(fileinfo.originalFilename)
                    THEN EXCLUDED.originalFilename
                    ELSE fileinfo.originalFilename
                END,
                fileName = CASE
                    WHEN is_empty_or_placeholder(fileinfo.fileName)
                    THEN EXCLUDED.fileName
                    ELSE fileinfo.fileName
                END,
                path = CASE
                    WHEN is_empty_or_placeholder(fileinfo.path)
                    THEN EXCLUDED.path
                    ELSE fileinfo.path
                END,
                fileSize = CASE
                    WHEN fileinfo.fileSize IS NULL
                    THEN EXCLUDED.fileSize
                    ELSE fileinfo.fileSize
                END,
                mimeType = CASE
                    WHEN is_empty_or_placeholder(fileinfo.mimeType)
                    THEN EXCLUDED.mimeType
                    ELSE fileinfo.mimeType
                END,
                extension = CASE
                    WHEN is_empty_or_placeholder(fileinfo.extension)
                    THEN EXCLUDED.extension
                    ELSE fileinfo.extension
                END,
                lastModifyTime = EXCLUDED.lastModifyTime;
        """, (
            row.get('sha256'),
            row.get('originalFilename'),
            file_name,
            full_path,
            row.get('size'),
            row.get('mimeType'),
            row.get('detectedExtension'),
            combined_tags,  # 병합된 태그 사용
            now,
            now
        ))
        return True

    except Exception as e:
        print(f"[ERROR] {row.get('fileName', 'unknown')} 처리 실패: {e}")
        print(f"[DETAIL] row: {row}")
        config.error_log.append(f"{row.get('fileName', 'unknown')} 처리 실패: {e}")
        return False
    
# ------------------------- DB 업데이트 후 파일 이동 (미사용용) -------------------------
def move_file_to_destination(file, sha256, base_path):
    try:
        if '.' in file:
            fileName, extension = file.rsplit('.', 1)
        else:
            fileName, extension = file, ''
        dest_path = Path(base_path) / sha256[:3] / f"{sha256}.{extension}"
        dest_path.parent.mkdir(parents=True, exist_ok=True)

        Path(file).rename(dest_path)
        print(f"[INFO] {file} -> {dest_path}")
        #messagebox.showinfo("파일 이동 완료", f"{file} -> {dest_path}")
        config.status_var.set(f"✅ 파일 이동 완료: {file} -> {dest_path}")
    except Exception as e:
        print(f"[ERROR] 파일 이동 실패: {e}")
        #messagebox.showerror("파일 이동 실패", f"{file} 이동 실패: {e}")
        config.status_var.set(f"❌ 파일 이동 실패: {file} 이동 실패: {e}")
        config.error_log.append(f"{file} 이동 실패: {e}")
# ------------------------- DB 내의 Name 검색 후 Path Return -------------------------
<<<<<<< HEAD
def copy_file_from_db(input_type, data, dest_dir, mode="OR"):
    print(f"{input_type} {data} {dest_dir} {mode}")

    if not config.conn:
        config.status_var.set("경고 - DB에 연결되어 있지 않습니다.")
        return
    
    if not dest_dir:
        config.status_var.set("경고 - 이동할 경로가 지정되지 않았습니다.")
        return
    
    try:
        if input_type == 'file':
            # CSV 또는 TXT 파일 열기
            if not Path(data).exists():
                print(f"[ERROR] 입력 파일 경로가 존재하지 않습니다: {data}")
                return False

            with open(data, 'r', encoding='utf-8-sig') as f:
                content = f.read()

            filenames = [name.strip() for name in content.split(',') if name.strip()]

            if not filenames:
                print(f"[ERROR] 파일에 파일명이 없습니다.")
                return False

            for filename in filenames:
                config.cur.execute("SELECT path FROM fileinfo WHERE fileName = %s", (filename,))
                result = config.cur.fetchone()

                if result:
                    file_path = Path(result[0])
                    if file_path.exists():
                        shutil.copy2(file_path, Path(dest_dir))
                        print(f"[INFO] 복사 완료: {file_path}")
                    else:
                        print(f"[WARN] 파일이 존재하지 않습니다: {file_path}")
                else:
                    print(f"[WARN] DB에 해당 파일명이 없습니다: {filename}")

        if input_type == 'tag':
            if isinstance(data, list):
                if mode == 'OR':
                    query = "SELECT path FROM fileinfo WHERE tag && %s"
                elif mode == 'AND':    
                    query = "SELECT path FROM fileinfo WHERE tag @> %s"
                else:
                    raise ValueError("mode는 'or' 또는 'and'여야 합니다.")
                config.cur.execute(query, (data,))

            else:
                config.cur.execute("SELECT path FROM fileinfo WHERE %s = Any(tag)", (data,))
        
            result = config.cur.fetchall()
            print(f"[INFO] 검색된 파일 수: {len(result)}")

            if not result or len(result) == 0: 
                print(f"[INFO] '{data}'에 대한 검색 결과가 없습니다.")
                return None
            
            success = False
        
            for row in result:
                print(f"[INFO] 파일 '{data}'의 경로: {row[0]}")
                file_path = Path(row[0])
                if file_path.exists():
                    shutil.copy2(file_path, Path(dest_dir))
                    success = True
                else:
                    print(f"[WARN] 파일이 존재하지 않습니다: {file_path}")
            
=======
def copy_file_from_db():

    if not config.conn:
        #messagebox.showwarning("DB 연결 상태", "현재 DB에 연결되어 있지 않습니다.")
        config.status_var.set("❌ 현재 DB에 연결되어 있지 않습니다.")
        return 
    
    rows, columns = config.select_results
    if 'path' not in columns:
        config.status_var.set("❌ Path 경로가 조회되지 않습니다. ")
        return 

    dest_dir = filedialog.askdirectory()
    print(dest_dir)
    if dest_dir == "":
        return 
    
    dest_dir = Path(dest_dir)
    
    dir_count = simpledialog.askstring("입력 요청","경로 내의 파일 개수 설정")
    if dir_count == '':
        dir_count = 0
    elif dir_count == None:
        return

    dict_rows = [dict(zip(columns, row)) for row in rows]
    data = [
        {
            k: row_dict[k] for k in ['path']
        } for row_dict in dict_rows
    ]
    import time
    #print(f"[DEBUG] 호출 정보: input_type={input_type}, data={data}, dest_dir={dest_dir}, mode={mode}")
    success = False
    config.status_var.set(f"복사 중...")
    failed_files = []  # 🔥 복사 실패 파일 리스트 추가
    
    try:
        for file_path in data:
            print(file_path['path'])
            if dir_count != 0:
                while len([f for f in dest_dir.iterdir() if f.is_file()]) >= int(dir_count):
                    print(f"도착 경로의 파일 개수 {dir_count}개 초과 하였습니다.")
                    time.sleep(5)
            if Path(file_path['path']).exists():
                shutil.copy2(Path(file_path['path']), Path(dest_dir))
                print(f"[INFO] 복사 완료: {file_path['path']}")
                #config.status_var.set(f"✅ 복사 완료: {file_path}")
                success = True
            else:
                print(f"[WARN] 파일이 존재하지 않습니다: {file_path['path']}")
                #config.status_var.set(f"❌ 파일이 존재하지 않습니다: {file_path}")
                failed_files.append((file_path['path'], "파일 없음"))
            
        # 🔥 복사 실패 파일 CSV로 저장
        if failed_files:
            save_failed_files(dest_dir, failed_files)

        config.status_var.set(f"복사가 완료하였습니다.")

>>>>>>> 1a8b8f7 (update)
        return success
        
    except Exception as e:
        print(f"[ERROR] DB 검색 실패: {e}")
        return None
# gui_main.py
import tkinter as tk
import csv
from tkinter import filedialog, ttk
from db_utils import connect_to_db, copy_file_from_db, execute_and_display_query 
from file_utils import  run_csv_insertion, tree_view, export_tree_to_csv
import config

# ------------------------- 기본 설정 -------------------------
root = tk.Tk()
root.title("FileInfo DB GUI")
#root.geometry("600x600")
root.resizable(False, False)

config.progress_var = tk.DoubleVar(value=0)
config.status_var = tk.StringVar(value="💤 대기 중입니다...")

config.select_query = tk.StringVar()
config.select_csv = tk.StringVar()
config.file_path_var = tk.StringVar()
config.destination_path = tk.StringVar()
config.filename_list_path = tk.StringVar()
config.tags = tk.StringVar()
config.filename_entry = tk.StringVar()
config.filename_list = tk.StringVar()
config.cur = tk.StringVar()
config.select_options = tk.StringVar(value="None")
config.logic_operator = tk.StringVar(value="AND")
config.extra_filter = tk.StringVar()
config.dir_count = tk.StringVar()

# ------------------------- 노트북 탭 구성 -------------------------
notebook = ttk.Notebook(root)
notebook.pack(fill="both", expand=True)

tab_db = ttk.Frame(notebook)
tab_select = ttk.Frame(notebook)
tab_update = ttk.Frame(notebook)

notebook.add(tab_db, text="DB 접속")
notebook.add(tab_select, text="DB 조회")
notebook.add(tab_update, text="DB 업데이트")

# ------------------------- DB 접속 탭 -------------------------
db_frame = tk.LabelFrame(tab_db, text="[DB 접속 정보]", padx=10, pady=10)
db_frame.pack(padx=10, pady=10, fill="x")

tk.Label(db_frame, text="DB IP:").grid(row=0, column=0, padx=10, pady=5, sticky="e")
host_entry = tk.Entry(db_frame, width=30)
host_entry.grid(row=0, column=1)

tk.Label(db_frame, text="사용자:").grid(row=1, column=0, padx=10, sticky="e")
user_entry = tk.Entry(db_frame, width=30)
user_entry.grid(row=1, column=1)

tk.Label(db_frame, text="비밀번호:").grid(row=2, column=0, padx=10, sticky="e")
password_entry = tk.Entry(db_frame, width=30, show="*")
password_entry.grid(row=2, column=1)

tk.Button(db_frame, text="Connect", command=lambda: connect_to_db(host_entry, user_entry, password_entry)).grid(row=3, column=1, padx=5, pady=10, sticky="w")
# ------------------------- DB 조회 탭 -------------------------
def on_tree_click(event):
    row_id = tree.identify_row(event.y)
    column_id = tree.identify_column(event.x)

    if not row_id or not column_id:
        return

    cell_value = tree.set(row_id, column_id)
    print(f"선택된 셀 값: {cell_value}")

    # 클립보드에 복사
    tree.clipboard_clear()
    tree.clipboard_append(cell_value)


select_frame = tk.LabelFrame(tab_select, text="[DB 조회]")
select_frame.pack_propagate(False)  # 고정된 크기 유지
select_frame.pack(padx=10, pady=10, fill="x")

select_frame.grid_rowconfigure(0, minsize=10)
select_frame.grid_rowconfigure(1, minsize=10)

select_frame.grid_columnconfigure(0, minsize=10)
select_frame.grid_columnconfigure(1, minsize=200, weight=10)
select_frame.grid_columnconfigure(2, minsize=50)

tk.Label(select_frame, text="Query:").grid(row=0, column=0, padx=(5,0), pady=5, sticky="w")
select_query_entry = tk.Entry(select_frame, textvariable=config.select_query, width=50)
select_query_entry.grid(row=0, column=1, padx=(0,0), pady=5, sticky="we")

config.checkboxoption = tk.IntVar()
tk.Checkbutton(select_frame, text="tag", variable=config.checkboxoption, onvalue=1, offvalue=0, width=5).grid(row=0, column=2)

tree_container = tk.Frame(select_frame, width=500, height=200)
tree_container.grid(row=3, column=0, columnspan=3, padx=5, pady=5, sticky="nsew")
tree_container.grid_propagate(False)  # 고정된 크기 유지
tree_container.grid_rowconfigure(0, weight=1)
tree_container.grid_columnconfigure(0, weight=1)

tree = ttk.Treeview(tree_container, show="headings", height=10)
tree.grid(row=0, column=0, sticky="nsew")
tree.bind("<Control-c>", on_tree_click)

select_x_scrollbar = ttk.Scrollbar(tree_container, orient="horizontal", command=tree.xview)
select_x_scrollbar.grid(row=1, column=0, sticky="ew")
select_y_scrollbar = ttk.Scrollbar(tree_container, orient="vertical", command=tree.yview)
select_y_scrollbar.grid(row=0, column=1, sticky="ns")   

tree.configure(xscrollcommand=select_x_scrollbar.set, yscrollcommand=select_y_scrollbar.set)

# 선택된 조건에 따라 드롭다운 메뉴 업데이트
select_options_frame = tk.Frame(select_frame)
select_options_frame.grid(row=1, column=1, padx=(0,0), pady=5, sticky="w")

tk.Button(select_options_frame, text="조회", width=10,
          command=lambda: tree_view(execute_and_display_query(select_query_entry.get(),config.checkboxoption.get()),tree)
          ).pack(side="left", padx=(0,2))

tk.Button(select_options_frame, text="Copy", width=10, 
          command=lambda: copy_file_from_db()
          ).pack(side="left", padx=(0,2))

tk.Button(select_options_frame, text="Export", width=10, bg="#4CAF50", fg="white", font=("맑은 고딕", 9, "bold"),
          command=lambda: export_tree_to_csv(tree)
          ).pack(side="left", padx=(0,2))

# ------------------------- DB 업데이트 탭 -------------------------
input_frame = tk.LabelFrame(tab_update, text="[DB 업데이트]")
input_frame.pack(fill="x", padx=10, pady=10, ipady=5)

# 파일 경로 입력
tk.Label(input_frame, text="파일 경로:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
tk.Entry(input_frame, textvariable=config.filename_list_path, width=40).grid(row=0, column=1, padx=5, pady=5, sticky="w")
tk.Button(input_frame, text="찾기", 
          command=lambda: config.filename_list_path.set(
                filedialog.askopenfilename(
                    filetypes=[("Text/CSV Files", "*.csv;*.txt")]
                    )
                )
        ).grid(row=0, column=2, padx=5, pady=5)

# 태그 입력
tk.Label(input_frame, text="태그 입력:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
tk.Entry(input_frame, textvariable=config.tags, width=30).grid(row=1, column=1, columnspan=2, padx=5, pady=5, sticky="w")

# 버튼 라인
insert_btn = tk.Button(input_frame, text="입력", width=20, command=lambda: run_csv_insertion(config.progress_var, insert_btn, config.batch_size))
insert_btn.grid(row=2, column=1, padx=5, pady=10, sticky="w")
# ------------------------- 상태바 -------------------------
status_frame = ttk.Frame(root)
status_frame.pack(fill="x", padx=10, pady=10, ipady=5)

status_label = tk.Label(status_frame, textvariable=config.status_var, anchor="w", relief="sunken")
status_label.grid(row=4, column=0, columnspan=3, sticky="we", padx=5, pady=(0, 5))

progress_bar = ttk.Progressbar(status_frame, variable=config.progress_var, maximum=100)
progress_bar.grid(row=3, column=0, columnspan=3, padx=5, pady=(0, 5), sticky="we")
config.progress_bar = progress_bar

root.mainloop()
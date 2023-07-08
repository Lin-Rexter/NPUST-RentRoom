# coding=utf-8
import os
import re
import json
import time
import random
import numpy as np
import textwrap
from datetime import timedelta
from functools import reduce
from bson import json_util
import asyncio

# 讀取.env檔
from dotenv import load_dotenv, find_dotenv

# 輸出詳細錯誤信息
import traceback

# 引入MongoDB CRUD模組
from db import Mongodb, connect, disconnect, run, pp

connect()  # 連線Mongodb

# 非同步服務器
# import uvicorn

# 非同步服務器
# from hypercorn.config import Config
# from hypercorn.asyncio import serve

# WSGI轉ASGI
# from asgiref.wsgi import WsgiToAsgi

# 提供非同步編程
# from gevent.pywsgi import WSGIServer
# 提供熱重載
# import werkzeug.serving


# Quart(ASGI版本的Flask): https://github.com/pallets/quart#relationship-with-flask
# Flask遷移至Quart步驟(簡單): https://quart.palletsprojects.com/en/latest/how_to_guides/flask_migration.html
from flask import (
    Flask,
    request,
    Response,
    make_response,
    abort,
    render_template,
    redirect,
    url_for,
    flash,
    jsonify,
    session,
)

# Websocket連線(聊天用)
from flask_socketio import SocketIO, emit, send, join_room, leave_room

# 異常處理
from werkzeug import exceptions


app = Flask(__name__)
# Flask flash需要Session，因此需使用密鑰，防止CSRF。
app.secret_key = os.getenv("SECRET_KEY") or None
# 設置session有效期限
app.permanent_session_lifetime = timedelta(days=365)

# Websocket
socketio = SocketIO(app)

# 從.env載入環境變數
env_path = find_dotenv(raise_error_if_not_found=True)
load_dotenv(env_path)

# 開發者登入密碼
Developer_Pwd = os.getenv("DEV_PASSWORD") or None

if Developer_Pwd is None:
    raise ValueError(".env檔尚未設置密碼!")

# 開發模式
is_dev = True

# 當開發模式啟用時，啟用開發者登入授權
if is_dev:
    # 檢查登入狀態
    @app.before_request
    async def is_login():
        if request.path == "/dev_login":
            return

        if session.get("is_login") != True:
            return redirect(url_for("dev_login"))
        else:
            return

    # = = = 授權(開發者登入頁面)= = =
    @app.route("/dev_login", methods=["GET", "POST"])
    async def dev_login():
        if session.get("is_login") == True:
            return redirect("/")

        if request.method == "POST":
            password = request.form.get("password")
            if password == Developer_Pwd:
                session.permanent = True
                session["is_login"] = True
                return redirect("/")
            else:
                flash("登入失敗!")
                return redirect("/dev_login")
        else:
            return render_template("./Auth/dev_login.html")


# = = = 授權(登入/註冊頁面)= = =
@app.route("/login&signup", methods=["GET", "POST"])
async def login_signup():
    return render_template("./Auth/login&signup.html")


# = = = 聊天 = = =
@socketio.on("join", namespace="/chat")
def join(message):
    room = session.get("chatroom")
    join_room(room)
    emit("status", {"msg": f'{session.get("username")}已進入聊天室'}, room=room)


@socketio.on("send")
def chat(data):
    emit("get", data)


# 🌟🌟🌟首頁🌟🌟🌟
@app.route("/", methods=["GET", "POST"])
async def home():
    imgs = [
        "basic_data.png",
        "private_chat.png",
        "question_report.png",
        "recommend_give_you.png",
        "search_house.png",
        "sign_up_login.png",
    ]
    return render_template("home.html", imgs=imgs)


# 房屋搜尋
@app.route("/house_search", methods=["GET", "POST"])
async def house_search():
    """
    if request.method == "POST":
        checkbox = request.form.get("checkbox")
        search = request.form.get("search")
        print("box:", checkbox)
        print("search:", search)
    """

    filter_info = [
        {"filter_name": "坪數", "options": ["3坪", "4坪", "5坪", "6坪"]},
        {"filter_name": "房型", "options": ["套房", "雅房", "整棟", "出租"]},
        {
            "filter_name": "租金",
            "options": ["2000-3000/月", "3000-4000/月", "4000-5000/月", "5000-6000/月"],
        },
        {"filter_name": "其他條件", "options": ["可養寵物", "有電梯", "有管理員", "台電計費"]},
    ]

    # 房客租屋資訊(測試用)
    tenants_info = [
        {
            "house_pic": "https://img2.591.com.tw/house/2016/04/20/146113765929754508.jpg!fit.1000x.water2.jpg",
            "tenant_name": f"小明",
            "house_name": f"屏科國際學苑-精緻單人大套房_{i}",
            "house_type": "分租套房",
            "ping": 6,
            "house_location": "內埔鄉農專街55巷61號",
            "rental_time": "2022-05-10",
            "leave_time": "2023-05-12",
            "tenant_phone": "0912345678",
            "rent": 4467,
            "deposit": 6000,
            "status": "已退租",
        }
        for i in range(20)
    ]

    # 找到的資料數
    info_length = len(tenants_info)

    # 將資料各分5組
    group_info = [tenants_info[i : i + 5] for i in range(0, info_length, 5)]

    # 搜尋的頁數
    if request.method == "POST":
        search_index = request.form.get("page")
    else:
        search_index = 1

    print("page:", search_index)

    # 取得資料第幾組
    result_info = (
        group_info[int(search_index) - 1] if search_index is not None else group_info[0]
    )

    return render_template(
        "house_search.html",
        filter_info=filter_info,
        tenants_info=result_info,
        data_length=len(group_info),
        now_index=search_index,
    )


# 個人檔案(房東/房客)(建置中)
@app.route("/profile", methods=["GET", "POST"])
async def profile():
    """
    if request.method == "POST":
        identity = request.form.get("identity")
        username = request.form.get("username")
        phone = request.form.get("phone")
        Email = request.form.get("Email")
        bDate = request.form.get("bDate")

        # 判斷是否已有使用者ID
        has_id = False
        if session.get("user_ID") is not None:
            global user_ID
            user_ID = session.get("user_ID")
            has_id = True

        is_tenant = True # 儲存是否為房客
        if user_ID ==

        # 防止生成重複ID，不斷迴圈
        while 1:
            # 判斷選擇的身分是否為房客去設定專屬ID，並選擇要查找的資料表
            if identity == "房客":
                user_ID = f"@TEN{random_str(6)}"
                collection = "Tenant"
                data_id_key = "tId"
            else:
                user_ID = f"@LAN{random_str(6)}"
                collection = "Landlord"
                data_id_key = "lId"
                is_tenant = False

            # 依照身分查找特定資料表
            sProfile = Mongodb(database="屏科租屋網", collection=collection)

            # 查詢ID是否已存在
            total = run(sProfile.count(filter = {data_id_key: user_ID}))

            if total is None:
                break

        if is_tenant:
            data = [
                    {
                        "tId": user_ID,
                        "headshot": "./picture/wang.png",
                        "tName": username,
                        "phone": phone,
                        "Email": Email,
                        "bDate": bDate
                    }
                ]
        else:
            data = [
                    {
                    "lId": user_ID,
                    "headshot": "../static/images/llimg.png",
                    "lName": username,
                    "phone": phone,
                    "Email": Email,
                    "cInfo": "https//line.me/ti/p/asds56",
                    "bDate": bDate,
                    "IDNum": "N125478535",
                    "extra file": "./info.pdf"
                    }
                ]

        search_id = None
        if total is not None:
            result = run(sProfile.insert(document=data))
        else:
            if is_tenant == 1:
                search_id = "tId"
            elif is_tenant == 2:
                search_id = "lId"

            if search_id is not None:
                result = run(sProfile.update(filter={search_id: user_ID}, update=data))
            else:
                result = None
    """

    return render_template("profile.html")


# = = = 管理(房東管理房客租屋資料) = = =
@app.route("/tenant_managed", methods=["GET", "POST"])
async def tenant_managed():
    # 房客租屋資訊(測試用)
    tenants_info = [
        {
            "house_pic": "https://img2.591.com.tw/house/2016/04/20/146113765929754508.jpg!fit.1000x.water2.jpg",
            "tenant_name": "小明",
            "house_name": "屏科國際學苑-精緻單人大套房",
            "house_type": "分租套房",
            "ping": 6,
            "house_location": "內埔鄉農專街55巷61號",
            "rental_time": "2022-05-10",
            "leave_time": "2023-05-12",
            "tenant_phone": "0912345678",
            "rent": 4467,
            "deposit": 6000,
            "status": "已退租",
        },
        {
            "house_pic": "https://img2.591.com.tw/house/2022/05/26/165355431069292481.jpg!fit.1000x.water2.jpg",
            "tenant_name": "小美",
            "house_name": "內埔溫馨獨立套房",
            "house_type": "獨立套房",
            "ping": 7,
            "house_location": "內埔鄉光華街41號",
            "rental time": "2022-07-15",
            "lease_time": None,
            "tenant_phone": "0987654321",
            "rent": 6200,
            "deposit": 12400,
            "status": "入住中",
        },
        {
            "house_pic": "https://img1.591.com.tw/house/2016/04/20/146113868381620105.jpg!fit.1000x.water2.jpg",
            "tenant_name": "小華",
            "house_name": "精緻雙人豪華大套房-最靠近屏科大",
            "house_type": "分租套房",
            "ping": 7.2,
            "house_location": "內埔鄉農專街55巷61號",
            "rental time": "2022-08-21",
            "lease_time": None,
            "tenant_phone": "0987650650",
            "rent": 5634,
            "deposit": 8000,
            "status": "入住中",
        },
    ]
    return render_template("./managed/tenant_managed.html", tenants_info=tenants_info)


# = = = 管理(房東管理登記的房屋) = = =
@app.route("/house_managed", methods=["GET", "POST"])
async def house_managed():
    house = Mongodb(database="屏科租屋網", collection="Houseinfo")
    tenant = Mongodb(database="屏科租屋網", collection="tenant_managed")

    # 取得房屋資料(hId, house_pic, house_name, ping, rent)
    t_house_info = run(
        house.find(
            projection={
                "_id": 0,
                "hId": 1,
                "house_pic": 1,
                "house_name": 1,
                "ping": 1,
                "rent": 1,
            }
        )
    )
    """
    bson_print(t_house_info)
    """

    # 取得所有房屋資料hId
    hId_list = []
    for items in t_house_info:
        hId_list.append(items["hId"])

    # 取得所有指定hId(hId_list)的房客租屋狀態(status), hId
    t_tenant_info = run(
        tenant.find(
            query={"hId": {"$in": hId_list}},
            projection={"_id": 0, "hId": 1, "status": 1},
        )
    )
    """
    bson_print(t_tenant_info)
    """
    # disconnect()

    # 將房屋資料與房客資料合併
    house_info = []
    for item_a in t_house_info:
        for item_b in t_tenant_info:
            if item_a["hId"] == item_b["hId"]:
                merged_item = {**item_a, **item_b}
                house_info.append(merged_item)
                break

    """
    bson_print(merged_list)
    """

    return render_template("./managed/house_managed.html", house_info=house_info)


# = = = 檢舉/回報頁面(撰寫) = = =
@app.route("/Report&Feedback", methods=["GET", "POST"])
async def Report_Feedback():
    return render_template("./Report&Feedback/report&feedback.html")


# = = = 檢舉/回報頁面(編輯) = = =
@app.route("/edit_Report&Feedback", methods=["GET", "POST"])
async def edit_Report_Feedback():
    return render_template("./Report&Feedback/edit_report&feedback.html")


# = = = 追蹤(房屋) = = =
@app.route("/track_house", methods=["GET", "POST"])
async def track_house():
    house_list = [
        {
            "house_id": f"@{random_str(10)}",
            "content": {
                "house_pic": "https://img2.591.com.tw/house/2016/04/20/146113765929754508.jpg!fit.1000x.water2.jpg",
                "house_name": "屏科國際學苑-精緻單人大套房",
                "house_type": "分租套房",
                "ping": 7.2,
                "house_location": "內埔鄉農專街55巷61號",
                "rent": f"${4467}",
                "deposit": f"${8000}",
            },
        }
        for _ in range(random.randint(5, 20))
    ]
    return render_template("./track/track_house.html", house_list=house_list)


# = = = 追蹤(房東) = = =
@app.route("/track_landlord", methods=["GET", "POST"])
async def track_landlord():
    # 房東的消息(測試用)
    notify_list = [
        {
            "user": f"@{random_str(10)}",
            "content": [
                {
                    "title": f"訊息{i+1}",
                    "time": random_date(
                        "1/1/2023 00:00 AM", "12/1/2023 23:59 PM", random.random()
                    ),
                    "message": random_str(300),
                }
                for i in range(random.randint(5, 20))
            ],
        }
        for _ in range(random.randint(10, 20))
    ]
    return render_template("./track/track_landlord.html", notify_list=notify_list)


# = = = 資訊查看(房屋) = = =
@app.route("/house_info", methods=["GET", "POST"])
async def house_info():
    return render_template("./info/house_info.html")


# = = = 資訊查看(房東) = = =
@app.route("/landlord_info", methods=["GET", "POST"])
async def landlord_info():
    return render_template("./info/landlord_info.html")


# = = = 後台(黑名單) = = =
@app.route("/block", methods=["GET", "POST"])
async def block():
    return render_template("./engineer/block_list.html")


# = = = 後台(管理各種資料) = = =
@app.route("/system_Managed", methods=["GET", "POST"])
async def system_Managed():
    tenant_info = [
        {
            "user_id": f"@{random_str(10)}",
            "name": random_str(5, "abcdefghijklmnopqrstuvwxyz"),
            "phone": f"09{random_str(8, '0123456789')}",
            "email": f"{random_str(8)}@gmail.com",
            "social": f"https://line.me/ti/p/{random_str(10)}",
            "birthday": random_date(
                "1/1/2023 00:00 AM", "6/20/2023 23:59 PM", random.random()
            ),
            "ID_number": f"{random_str(1, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ')}{random_str(1, '12')}{random_str(8, '0123456789')}",
        }
        for _ in range(random.randint(5, 20))
    ]

    # = = =管理評價資料= = =
    review = [
        {
            "level": "5",
            "content": "便宜又優惠",
            "Time": "2023/05/01",
            "rId": "105",
            "hId": "101",
            "tId": "@MbWON0GUhb",
        }
        for _ in range(random.randint(5, 20))
    ]

    # = = = 管理檢舉資料 = = =
    report = [
        {
            "rId": "1",
            "rContent": "偏激言論",
            "reporter_id": "@MbWON0GUhb",
            "Time": "2023/07/01 16:09",
            "name": f"@{random_str(9)}",
            "hId": {"$numberInt": "101"},
        }
        for _ in range(random.randint(5, 20))
    ]

    # = = = 管理回報資料 = = =
    feedback = [
        {
            "fId": "0",
            "tId": "@MbWON0GUhb",
            "lId": "@MbWON0GUhb",
            "content": "there's an bug :(",
            "fTime": "05/12/2023 12:52",
        }
        for _ in range(random.randint(5, 20))
    ]

    return render_template(
        "./engineer/system_Managed.html",
        tenant_info=tenant_info,
        review=review,
        report=report,
        feedback=feedback,
    )


# = = = 房東私聊 = = =
@app.route("/private_chat", methods=["GET", "POST"])
async def private_chat():
    return render_template("./private_chat.html")


# 當發生404錯誤時所顯示的頁面
@app.errorhandler(404)
def page_not_found(e):
    print("[ERROR]: ", e)
    return render_template("404.html"), 404


# 隨機生成字串(測試用)
def random_str(length: int, filter=None, warp=None) -> str:
    result = ""
    if filter is not None:
        chars = filter
    else:
        chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"

    for _ in range(length):
        result += chars[random.randint(0, len(chars) - 1)]

    if warp is not None:
        # 拆解字串並換行
        result_wrap = "\n".join(
            i for i in textwrap.wrap(result, width=random.randint(50, 150))
        )

        result = result_wrap

    return result


# 隨機日期(測試用)
def str_time_prop(start, end, time_format, prop):
    stime = time.mktime(time.strptime(start, time_format))
    etime = time.mktime(time.strptime(end, time_format))
    ptime = stime + prop * (etime - stime)
    return time.strftime(time_format, time.localtime(ptime))


# 指定範圍內的隨機日期(測試用)
def random_date(start, end, prop):
    return str_time_prop(start, end, "%m/%d/%Y %H:%M %p", prop)


# 格式化bson格式的資料
def bson_print(bson, indent=4, en_ascii=False):
    print(json_util.dumps(bson, indent=indent, ensure_ascii=en_ascii))


# 新增字典
def dict_add(name, key, values):
    name.setdefault(key, values)  # 使用setdefault優點，自動新增預設值


# WSGI轉ASGI
# asgi_app = WsgiToAsgi(app)

"""
# 熱重載包裝器
@werkzeug.serving.run_simple(hostname="127.0.0.1", port=5000, application=app, use_reloader=True)
def runServer():
    app.debug = True

    # gevent: 非同步包裝
    http_server = WSGIServer(("127.0.0.1", 5000), app)
    http_server.serve_forever()

runServer()
"""


if __name__ == "__main__":
    # app.run(debug=True, port=5000)
    socketio.run(app=app, debug=True, host="127.0.0.1", port=5000)
    # Flask熱重載功能
    # app.jinja_env.auto_reload = True
    # app.config['TEMPLATES_AUTO_RELOAD'] = True

    # config = Config()
    # config.bind = ["127.0.0.1:5000"]
    # config.use_reloader = True

    # asyncio.run(serve(app, config))

    # uvicorn.run("app:app", host="127.0.0.1", port=5000, log_level="info", reload=True)


# 改為使用hypercorn運行: poetry run hypercorn app:app --debug --reload -b 127.0.0.1:5000

# coding=utf-8
import os
import re
import json
import time
from functools import reduce

# 輸出詳細錯誤信息
import traceback

# Flask
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
    session
)

# 異常處理
from werkzeug import exceptions

app = Flask(__name__)

# Flask flash需要Session，因此需生成密鑰，防止CSRF。
app.secret_key = os.urandom(16)


@app.route("/")
def home():
    return render_template("home.html")


# 當發生404錯誤時所顯示的頁面
@app.errorhandler(404)
def page_not_found(e):
    print("[ERROR]: ", e)
    return render_template("404.html"), 404


if __name__ == "__main__":
    app.run(debug=True, port=5000)

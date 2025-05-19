# app.py
import os
import urllib.parse
from flask import Flask, request
from Crypto.Cipher import AES
import redis

HASH_KEY = b'RQzLomrVtOybbo9NfgBM94A3xmmuPMyW'
HASH_IV = b'P4DIJ7O6Qo1BuMDC'

app = Flask(__name__)
r = redis.Redis(host='your-redis-host', port=6379, password='yourpass', decode_responses=True)

def unpad(data):
    padding_len = data[-1]
    return data[:-padding_len]

def decrypt_trade_info(trade_info_hex):
    cipher = AES.new(HASH_KEY, AES.MODE_CBC, HASH_IV)
    decrypted = cipher.decrypt(bytes.fromhex(trade_info_hex))
    unpadded = unpad(decrypted)
    data_str = unpadded.decode("utf-8")
    return urllib.parse.parse_qs(data_str)

@app.route("/notify", methods=["POST"])
def notify():
    trade_info = request.form.get("TradeInfo")
    if not trade_info:
        return "NO DATA"
    
    data = decrypt_trade_info(trade_info)
    order_no = data.get("MerchantOrderNo", [""])[0]
    code = data.get("CodeNo", [""])[0]
    store = data.get("StoreType", [""])[0]

    # 儲存到 Redis，格式 key = 訂單編號, value = 代碼|超商
    if order_no and code:
        r.setex(order_no, 3600, f"{store}|{code}")
        print(f"[Notify] 儲存成功：{order_no} = {store} | {code}")

    return "OK"

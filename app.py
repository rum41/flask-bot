from flask import Flask, request
from Crypto.Cipher import AES
import urllib.parse

app = Flask(__name__)

HASH_KEY = '你的HashKey'
HASH_IV = '你的HashIV'

def unpad(data):
    padding_len = data[-1]
    return data[:-padding_len]

def decrypt_trade_info(trade_info_hex):
    data = bytes.fromhex(trade_info_hex)
    cipher = AES.new(HASH_KEY.encode(), AES.MODE_CBC, HASH_IV.encode())
    decrypted = cipher.decrypt(data)
    unpadded = unpad(decrypted).decode("utf-8")
    return urllib.parse.parse_qs(unpadded)

@app.route("/notify", methods=["POST"])
def notify():
    trade_info = request.form.get("TradeInfo")
    if not trade_info:
        return "No data"
    data = decrypt_trade_info(trade_info)
    print("[Notify] NewebPay 回傳資料：", data)
    return "OK"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)

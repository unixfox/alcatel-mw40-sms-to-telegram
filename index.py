import requests, os, json

api_url = "https://api.telegram.org/bot{token}/{method}".format
host = "bbox.nomad"
username = "admin"
password = "admin"
endpoint = "http://192.168.78.1"
TELEGRAM_ACCESS_TOKEN = os.environ.get("TELEGRAM_ACCESS_TOKEN", None)
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", None)
TCLREQUESTVERIFICATIONKEY = os.environ.get("TCLREQUESTVERIFICATIONKEY", None)

# found the sdk.js and then converted from js to python
def encrypt(s):
    if s == "" or s is None:
        return ""

    key = "e5dl12XYVggihggafXWf0f2YSf2Xngd1"
    str1 = []
    encry_str = ""

    for i in range(len(s)):
        char_i = s[i]
        num_char_i = ord(char_i)
        key_char = ord(key[i % len(key)])
        str1.append((key_char & 0xF0) | ((num_char_i & 0xF) ^ (key_char & 0xF)))
        str1.append((key_char & 0xF0) | ((num_char_i >> 4) ^ (key_char & 0xF)))

    for i in range(len(str1)):
        encry_str += chr(str1[i])

    return encry_str


def telegram_command(name, data):
    url = api_url(token=TELEGRAM_ACCESS_TOKEN, method=name)
    return requests.post(url=url, json=data)


def telegram_sendMessage(text: str, chat_id: str, notify=True):
    return telegram_command(
        "sendMessage",
        {
            "text": text,
            "chat_id": chat_id,
            "parse_mode": "markdown",
            "disable_notification": not notify,
        },
    )


headers = {
    "_TclRequestVerificationKey": TCLREQUESTVERIFICATIONKEY,
    "user-agent": "User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:129.0) Gecko/20100101 Firefox/129.0",
    "Referer": "http://" + host + "/index.html",
    "host": host,
}

check_new_sms = {
    "jsonrpc": "2.0",
    "method": "GetSMSStorageState",
    "id": "6.4",
}

check_new_sms_reply = requests.post(
    endpoint + "/jrd/webapi?api=GetSMSStorageState",
    json=check_new_sms,
    headers=headers,
)

check_new_sms_reply_json = check_new_sms_reply.json()

if check_new_sms_reply_json["result"]["UnreadSMSCount"] >= 1:

    auth_json = {
        "jsonrpc": "2.0",
        "method": "Login",
        "id": "1.1",
        "params": {"UserName": encrypt(username), "Password": encrypt(password)},
    }

    auth_reply = requests.post(
        endpoint + "/jrd/webapi", json=auth_json, headers=headers
    )
    auth_reply_json = auth_reply.json()
    token = auth_reply_json["result"]["token"]
    headers["_TclRequestVerificationToken"] = encrypt(str(token))

    sms_contact_read_json = {
        "jsonrpc": "2.0",
        "method": "GetSMSContactList",
        "params": {"Page": 0},
        "id": "6.2",
    }

    sms_contact_read_reply = requests.post(
        endpoint + "/jrd/webapi?api=GetSMSContactList",
        json=sms_contact_read_json,
        headers=headers,
    )

    sms_contact_read_reply_json = sms_contact_read_reply.json()

    for sms_contact in sms_contact_read_reply_json["result"]["SMSContactList"]:
        sms_read_json = {
            "jsonrpc": "2.0",
            "method": "GetSMSContentList",
            "params": {"Page": 0, "ContactId": sms_contact["ContactId"]},
            "id": "6.3",
        }
        sms_read_reply = requests.post(
            endpoint + "/jrd/webapi?api=GetSMSContentList",
            json=sms_read_json,
            headers=headers,
        )
        sms_read_reply_json = sms_read_reply.json()
        for sms in sms_read_reply_json["result"]["SMSContentList"]:
            telegram_sendMessage(
                "New SMS from alcatel: \n"
                + "PhoneNumber: "
                + sms_contact["PhoneNumber"][0]
                + "\n"
                + "SMSContent: \n"
                + "```\n"
                + sms["SMSContent"]
                + "\n```"
                + "SMSTime: "
                + sms["SMSTime"]
                + "\n",
                TELEGRAM_CHAT_ID,
            )
            sms_delete_json = {
                "jsonrpc": "2.0",
                "method": "DeleteSMS",
                "params": {
                    "DelFlag": 2,
                    "ContactId": sms_contact["ContactId"],
                    "SMSId": sms["SMSId"],
                },
                "id": "6.5",
            }
            requests.post(
                endpoint + "/jrd/webapi?api=DeleteSMS",
                json=sms_delete_json,
                headers=headers,
            )

# Check for new SMS on Alcatel MW40 LinkZone (Bouygues telecom) then send them to telegram

1. Setup a telegram bot, get the token and the chat ID
2. Find the _TclRequestVerificationKey through the requests done on the web interface
3. Launch with:

```
export TELEGRAM_ACCESS_TOKEN=mytoken
export TELEGRAM_CHAT_ID=chatid
export TCLREQUESTVERIFICATIONKEY=thekey
python index.py
```
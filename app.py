'''

整體功能描述

'''

'''

Application 主架構

'''
# 引用psycopg2
import os
import psycopg2

# 引用Web Server套件
from flask import Flask, request, abort

# 從linebot 套件包裡引用 LineBotApi 與 WebhookHandler 類別
from linebot import (
    LineBotApi, WebhookHandler
)

# 引用無效簽章錯誤
from linebot.exceptions import (
    InvalidSignatureError
)

# 載入json處理套件
import json

# 載入基礎設定檔
secretFileContentJson=json.load(open("./line_secret_key",'r',encoding='utf8'))
server_url=secretFileContentJson.get("server_url")

# 設定Server啟用細節
app = Flask(__name__,static_url_path = "/material" , static_folder = "./material/")

# 生成實體物件
line_bot_api = LineBotApi(secretFileContentJson.get("channel_access_token"))
handler = WebhookHandler(secretFileContentJson.get("secret_key"))

# 啟動server對外接口，使Line能丟消息進來
@app.route("/", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    
    print(body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

'''

消息判斷器

讀取指定的json檔案後，把json解析成不同格式的SendMessage

讀取檔案，
把內容轉換成json
將json轉換成消息
放回array中，並把array傳出。

'''

# 引用會用到的套件
from linebot.models import (
    ImagemapSendMessage,TextSendMessage,ImageSendMessage,LocationSendMessage,FlexSendMessage,VideoSendMessage
)

from linebot.models.template import (
    ButtonsTemplate,CarouselTemplate,ConfirmTemplate,ImageCarouselTemplate
    
)

from linebot.models.template import *

def detect_json_array_to_new_message_array(fileName):
    
    #開啟檔案，轉成json
    with open(fileName) as f:
        jsonArray = json.load(f)
    
    # 解析json
    returnArray = []
    for jsonObject in jsonArray:

        # 讀取其用來判斷的元件
        message_type = jsonObject.get('type')
        
        # 轉換
        if message_type == 'text':
            returnArray.append(TextSendMessage.new_from_json_dict(jsonObject))
        elif message_type == 'imagemap':
            returnArray.append(ImagemapSendMessage.new_from_json_dict(jsonObject))
        elif message_type == 'template':
            returnArray.append(TemplateSendMessage.new_from_json_dict(jsonObject))
        elif message_type == 'image':
            returnArray.append(ImageSendMessage.new_from_json_dict(jsonObject))
        elif message_type == 'sticker':
            returnArray.append(StickerSendMessage.new_from_json_dict(jsonObject))  
        elif message_type == 'audio':
            returnArray.append(AudioSendMessage.new_from_json_dict(jsonObject))  
        elif message_type == 'location':
            returnArray.append(LocationSendMessage.new_from_json_dict(jsonObject))
        elif message_type == 'flex':
            returnArray.append(FlexSendMessage.new_from_json_dict(jsonObject))  
        elif message_type == 'video':
            returnArray.append(FlexSendMessage.new_from_json_dict(jsonObject))    


    # 回傳
    return returnArray

'''

handler處理關注消息

用戶關注時，讀取 素材 -> 關注 -> reply.json

將其轉換成可寄發的消息，傳回給Line

'''

# 引用套件
from linebot.models import (
    FollowEvent
)
replyJsonPath = "material/Restart/reply.json"
follow_message_array = detect_json_array_to_new_message_array(replyJsonPath)


# 關注事件處理
@handler.add(FollowEvent)
def process_follow_event(event):
    # 取出消息內User的資料
    
    user_profile = line_bot_api.get_profile(event.source.user_id)
    quiz()
    lineRichMenuId = 'richmenu-0198dfbfdd5ce050e3e5874b1a2c4b27'
    user_id = user_profile.user_id
    print(user_id)
    line_bot_api.link_rich_menu_to_user(user_id, lineRichMenuId)
    #linkResult = line_bot_api.link_rich_menu_to_user(secretFileContentJson["self_user_id"], lineRichMenuId)
    # 將用戶資訊存在檔案內
    # with open("./users.txt", "a") as myfile:
    #     myfile.write(json.dumps(vars(user_profile),sort_keys=True))
    #     myfile.write('\r\n')
    
        
    # 消息發送
    line_bot_api.reply_message(
        event.reply_token,
        follow_message_array
    )

confirmJsonPath = "material/confirm/reply.json"
confirm_template_array = detect_json_array_to_new_message_array(replyJsonPath)


'''

handler處理文字消息

收到用戶回應的文字消息，
按文字消息內容，往素材資料夾中，找尋以該內容命名的資料夾，讀取裡面的reply.json

轉譯json後，將消息回傳給用戶

'''

# 引用套件
from linebot.models import (
    MessageEvent, TextMessage, MessageAction
)
from string import digits
from random import randint, choice


#有相同數字檢查函式
def hasSameDigit(sameNum):
    for i in range(len(sameNum)):
        if (sameNum[0] == sameNum[1]) or (sameNum[0] == sameNum[2]) or (sameNum[0] == sameNum[3]) or (
                sameNum[1] == sameNum[2]) or (sameNum[1] == sameNum[3]) or (sameNum[2] == sameNum[3]):
            return True
    return False

# 局數
count = 0

def quiz():
    numStr = '0123456789'
    global randNum
    randNum = ''
    for i in range(4):
        n = choice(numStr)
        randNum = randNum + n
        numStr = numStr.replace(n, '')
    print(randNum)
    return randNum

# 之後會使用到的矩陣
userNums = []
results = []
user_return_list = []
result_message_array = []

Winner = 0

# 數字輸入偵測錯誤
num = []
number = 0



@handler.add(MessageEvent,message=TextMessage)
def process_text_message(event):

    # 讀取本地檔案，並轉譯成消息
    message = event.message.text
    global number, count, Winner, result_message_array
    if (message == 'Restart'):
        replyJsonPath = "material/" + message + "/reply.json"
        result_message_array = detect_json_array_to_new_message_array(replyJsonPath)
        line_bot_api.reply_message(event.reply_token, result_message_array)
        count = 0
        number = 0
        num.clear()
        user_return_list.clear()
        userNums.clear()
        results.clear()
        quiz()
    while (number == 0):
        # num = message
        if (message.isdigit() == False):
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text='錯誤： 請輸入不同數字，請重新輸入'))
        elif (len(message) != 4):
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text='錯誤： 超過四位數字，請重新輸入'))
        elif (hasSameDigit(message) == True):
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text='錯誤： 有重複數字，請重新輸入'))
        else:
            userNum = message
            userNums.append(userNum)
            seatA = 0
            seatB = 0
            count += 1
            for i in range(4):
                if userNum[i] in randNum:
                    if i == randNum.find(userNum[i]):
                        seatA += 1
                    else:
                        seatB += 1
                if seatA == 4:
                    line_bot_api.reply_message(event.reply_token,
                                               TextSendMessage(text='恭喜!! You win!! 總回合數: %d 回合 \n 輸入 \'Restart\' 重新遊玩' %count))
                    #當勝利時要怎麼跳出並且如何結束
                    # line_bot_api.reply_message(event.reply_token, confirm_template_array)
                    number = 1
                    break
                    #跳出一個確定模板確定是否要重來一局

                else:
                    exit
                result = '%dA%dB' % (seatA, seatB)
            results.append(result)
            # 螢幕顯示所有局
            str_n = '\n'
            user_return = str(count) + '------' + userNum + '/' + result
            user_return_list.append(user_return)
            if len(user_return_list) > 1:
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text=str_n.join(user_return_list)))
            else:
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text=user_return_list[0]))

            for i in range(count):
                print('(%d)/%s/%s' % (i + 1, userNums[i], results[i]))
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text='(%d)/%s/%s' % (i + 1, userNums[i], results[i])))

            # replyJsonPath = "material/"+ message +"/reply.json"
            # result_message_array = detect_json_array_to_new_message_array(replyJsonPath)

    # # 發送
    # line_bot_api.reply_message(
    #     event.reply_token,
    #     result_message_array
    # )



'''

Application 運行（開發版）

'''
# if __name__ == "__main__":
#     app.run(host='0.0.0.0')

'''

Application 運行（heroku版）

'''

import os
if __name__ == "__main__":
    app.run(host='0.0.0.0',port=os.environ['PORT'])
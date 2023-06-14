import slack_sdk
from time import sleep
import re
from datetime import date, timedelta
from time import mktime
import requests
import http
from datetime import datetime
from datetime import date, timedelta
import datetime as dt

regexForReport = "traffic.light:.?(:large_green_circle:|:large_yellow_circle:|:red_circle:|🔴|🟢|🟡)\ntarget.spend.\(budget\):.?([+-]?([0-9]*[.])?[0-9]+)\nactual.spend:.?([+-]?([0-9]*[.])?[0-9]+)\ntarget.cpa:.?([+-]?([0-9]*[.])?[0-9]+)\nactual.cpa:.?([+-]?([0-9]*[.])?[0-9]+)\n#accounts:.?([+-]?([0-9]*[.])?[0-9]+)\n"
#getting day of the week
print(datetime.today().weekday())

DayofWeek = datetime.today().weekday()

# getting last week's UNIX timestamp
current_date = date.today().isoformat()   
days_before = (date.today()-timedelta(days=7))

print("\nCurrent Date: ",current_date)
UNIXTime = mktime(days_before.timetuple())
print("7 days before current date: ",UNIXTime)

CHANNEL = "C031N1UCGUS"
MESSAGES_PER_PAGE = 200
MAX_MESSAGES = 1000
averageReplyTime = float(0)
numMessagesAverage= 0

testerLinks = {}
mainLinks = {}

# mainLinks = []

# init web client
client = slack_sdk.WebClient()


ReminderMessage = "Hi team,\nThe bot will collect all the  client statuses tomorrow.\nMake sure every channel is updated with the client status by then.\n\nGuidelines:\n1. Should be in the main channel, NOT a thread.\n2. Should be in this format: 'Client Status: 🟢'"

def get_replies(messages_all, i):
    for message_dumpp in messages_all:
        try:
            if message_dumpp["thread_ts"] and message_dumpp["ts"]>UNIXTime:
                response = client.conversations_replies(channel=channel_ID_list[i], ts=message_dumpp['ts'])
                getTimeDifference(response, int(float(message_dumpp['ts'])))
                
        except:
            pass

def getTimeDifference(message_response, ts):
    temp = ts
    for messageinLoop in message_response["messages"]:
        global averageReplyTime
        global numMessagesAverage
        unix_timestamp = int(float(messageinLoop["ts"]))
        # print(unix_timestamp)
        print(dt.datetime.fromtimestamp(int(unix_timestamp)).strftime('%Y-%m-%d %H:%M:%S'))
        minsBtwReply = float((unix_timestamp-temp)/(60))
        if minsBtwReply!=0:
            averageReplyTime+=minsBtwReply
            print(minsBtwReply)
            print(averageReplyTime)
            numMessagesAverage+=1
            print(numMessagesAverage)
            
        temp = int(float(ts))

if DayofWeek==4:
    # client.chat_postMessage(channel="C01RXTCMKLN", text=ReminderMessage)
    pass

if DayofWeek==2:
    # gets channels that we need
    channel_ID_list = []
    channel_NAME_list = []

    print("Found channels are: ")
    for data in client.conversations_list(types="public_channel,private_channel",exclude_archived=True, limit=999)["channels"]:
        print(data["name"])
        if (re.search(r"client-",data["name"])):
            channel_ID_list.append(data["id"])
            channel_NAME_list.append(data["name"])
            print(f"CHANNEL:{data['name']} | ID:{data['id']}\n")

    # get first page
    page = 1
    print("Retrieving page {}".format(page))

    #TEST SECTION
    i=0
    message_list = []
    print(channel_NAME_list)
    MessageToBeSent = ""
    MessageToBeSent2 = ""
    for channel in channel_NAME_list:
        flag = 0
        flag2 = 0
        flag3=0
        message_list=[]
        message_list2=[]
        print(channel_ID_list[i])
        response = client.conversations_history(
            channel=channel_ID_list[i],
            limit=MESSAGES_PER_PAGE,
            oldest=UNIXTime,
        )
        assert response["ok"]
        messages_all = response['messages']

        # get additional pages if below max message and if they are any
        while len(messages_all) + MESSAGES_PER_PAGE <= MAX_MESSAGES and response['has_more']:
            page += 1
            print("Retrieving page {}".format(page))
            sleep(1)   # need to wait 1 sec before next call due to rate limits
            response = client.conversations_history(
                channel=channel_ID_list[i],
                limit=MESSAGES_PER_PAGE,
                cursor=response['response_metadata']['next_cursor'],
                oldest=UNIXTime,
            )
            assert response["ok"]
            messages = response['messages']
            messages_all = messages_all + messages


        response = client.conversations_history(
            channel=channel_ID_list[i],
            limit=MESSAGES_PER_PAGE,
            oldest=UNIXTime,
        )
        assert response["ok"]
        messages_all = response['messages']

        # get additional pages if below max message and if they are any
        while len(messages_all) + MESSAGES_PER_PAGE <= MAX_MESSAGES and response['has_more']:
            page += 1
            print("Retrieving page {}".format(page))
            sleep(1)   # need to wait 1 sec before next call due to rate limits
            response = client.conversations_history(
                channel=channel_ID_list[i],
                limit=MESSAGES_PER_PAGE,
                cursor=response['response_metadata']['next_cursor'],
                oldest=UNIXTime,
            )
            assert response["ok"]
            messages = response['messages']
        # print(messages_all)
        
        message_list = message_list+messages_all

        messages_needed = []
        
        numArr = []
        numArr2 = []
        # numArr3=[{}]
        get_replies(messages_all,i)
        for message_dumpp in messages_all:
            if float(message_dumpp["ts"])<UNIXTime:
                break
            else:
                # print("message:\n")
                # print(message_dumpp["ts"])
                # print("\n:message\n")
                # numArr3.clear()
                # print(message_dumpp["text"])
                one_message = message_dumpp["text"].lower()
                
                # if (re.search(r"traffic.light:",one_message)):
                #     print("success")
                #     messages_needed.append("success")
                
                
                
                if (re.search(r"traffic.light:.?(:large_green_circle:|:large_yellow_circle:|:red_circle:|🔴|🟢|🟡)\ntarget.spend.\(budget\):.?([+-]?([0-9]*[.])?[0-9]+)\nactual.spend:.?([+-]?([0-9]*[.])?[0-9]+)\ntarget.cpa:.?([+-]?([0-9]*[.])?[0-9]+)\nactual.cpa:.?([+-]?([0-9]*[.])?[0-9]+)",one_message)):
                    flag2  = 1
                    
                    # print(one_message)
                    # print("success")
                    messages_needed.append("success")
                    regexTrafficLight = '[\d]+[.,\d]+|[\d]*[.][\d]+|[\d]+'
                    if (":red_circle:" in one_message):
                        numArr.append(":red_circle:")
                    elif (":large_yellow_circle:" in one_message):
                        numArr.append(":large_yellow_circle:")
                    elif (":red_circle:" in one_message):
                        numArr.append(":red_circle:")
                    else:
                        numArr.append("No status found")
                    if re.search(regexTrafficLight, one_message) is not None:
                        for catch in re.finditer(regexTrafficLight, one_message):
                            # print(catch[0])
                            numArr.append(catch[0])
                    numArr.append(channel)
                    # print("Hello\n")
                    # print(numArr)
                    # print("Hello\n")
                    
                if (re.search(r"traffic.light:.?:large_green_circle:",one_message)):
                    # print(re.search(r"Hasura",message_dumpp["text"]))
                    messages_needed.append(message_dumpp["text"])
                    flag=1
                    break
                elif (re.search(r"traffic.light:.?:large_yellow_circle:",one_message)):
                    # print(re.search(r"Hasura",message_dumpp["text"]))
                    messages_needed.append(message_dumpp["text"])
                    flag=2
                    break
                elif (re.search(r"traffic.light:.?:red_circle:",one_message  )):
                    # print(re.search(r"Hasura",message_dumpp["text"]))
                    messages_needed.append(message_dumpp["text"])
                    flag=3
                    break
        
        #For second message:
        sprintDict={}
        for message_dumpp in messages_all:
            if float(message_dumpp["ts"])<UNIXTime:
                break
            else:
                # print(message_dumpp["text"])
                one_message = message_dumpp["text"].lower()
                
                # if (re.search(r"traffic.light:",one_message)):
                #     print("success")
                #     messages_needed.append("success")
                
                # print(one_message)
                
                    
                
                if (re.search(r"sprint.status:\s*(:large_green_circle:|:large_yellow_circle:|:red_circle:|🔴|🟢|🟡)\nsprint:",one_message)):
                    flag3  = 1
                    sprintDict={}
                    print(one_message)
                    # print("success")
                    messages_needed.append("success")
                    stringSprintStatus = ['sprint:(.*)week #']
                    if (":large_green_circle:" in one_message):
                        sprintDict["status"]=":large_green_circle:"
                        # numArr3.append(":large_green_circle:")
                    elif (":large_yellow_circle:" in one_message):
                        # numArr3.append(":large_yellow_circle:")
                        sprintDict["status"]=":large_yellow_circle:"
                    elif (":red_circle:" in one_message):
                        # numArr3.append(":red_circle:")
                        sprintDict["status"]=":red_circle:"
                    else:
                        sprintDict["No status found"]=":red_circle:"
                        # numArr3.append("No status found")
                    s = one_message
                    sprintDict["sprint"]=(s[s.find("sprint:")+len("sprint:"):s.rfind("week #:")])
                    sprintDict["week"]=(s[s.find("week #:")+len("week #:"):s.rfind("leading results:")])
                    sprintDict["leadingResult"]=(s[s.find("leading results:")+len("leading results:"):s.rfind("lagging results:")])
                    sprintDict["laggingResult"]=(s[s.find("lagging results:")+len("lagging results:"):s.rfind("notes:")])
                    sprintDict["notes"]=(s[s.find("notes:")+len("notes:"):])
                    sprintDict["channel"]=channel
                    
                    # for reg in regexSprintStatus:
                    #     if re.search(reg, one_message) is not None:
                    #         result = re.search(reg, one_message)
                    #         numArr2.append(result)
                    #     else:
                    #         numArr2.append("Not found\n")
                    # numArr3.append(channel)

                    numArr2.append(sprintDict)
                    
                    if (re.search(r"sprint.status:.?:large_green_circle:",one_message)):
                        # print(re.search(r"Hasura",message_dumpp["text"]))
                        # messages_needed.append(message_dumpp["text"])
                        MessageToBeSent2 = MessageToBeSent2+(f"{channel} - {sprintDict['sprint']} :large_green_circle:\n")
                        
                        # flag=1
                        # break
                    elif (re.search(r"sprint.status:.?:large_yellow_circle:",one_message)):
                        # print(re.search(r"Hasura",message_dumpp["text"]))
                        # messages_needed.append(message_dumpp["text"])
                        MessageToBeSent2 = MessageToBeSent2+(f"{channel} - {sprintDict['sprint']} :large_yellow_circle:\n")
                        # flag=2
                        # break
                    elif (re.search(r"sprint.status:.?:red_circle:",one_message)):
                        # print(re.search(r"Hasura",message_dumpp["text"]))
                        # messages_needed.append(message_dumpp["text"])
                        # flag=3
                        # break
                        MessageToBeSent2 = MessageToBeSent2+(f"{channel} - {sprintDict['sprint']} :red_circle:\n")
        print("THIS IS SECOND MESSAGE: ")
        print(sprintDict)
        # print(": THIS IS SECOND MESSAGE")
        # print(flag)
        # print(messages_needed)
        
        if flag==1:
            MessageToBeSent = MessageToBeSent+(f"{channel}: :large_green_circle:\n")
        if flag==2:
            MessageToBeSent = MessageToBeSent+(f"{channel}: :large_yellow_circle:\n")
        if flag==3:
            MessageToBeSent = MessageToBeSent+(f"{channel}: :red_circle:\n")
        
        #updating to google sheet
        for sprintOutput in numArr2:
            
            try:    
                print(numArr2)
                sheet3_inputs = {
                    "sheet3": {
                        "companyName": f"{sprintOutput['channel']}",
                        "status":f"{sprintOutput['status']}",
                        "sprint" : f"{sprintOutput['sprint']}",
                        "week#" : f"{sprintOutput['week']}",
                        "leadingResults" : f"{sprintOutput['leadingResult']}",
                        "laggingResults":f"{sprintOutput['laggingResult']}",
                        "notes" : f"{sprintOutput['notes']}",
                    }
                }
                
                sheet3_response = requests.post(mainLinks["sheet3_endpoint"], json=sheet3_inputs)
                print("TRYING TO POST\n\n")
                # numArr3.pop()
            except:
                error_message = sheet3_response.json().get("error")
                print(f"Error: {sheet3_response}")
                print("error in sheet 3")
            
        if(flag!=0):
            try:
                
                sheet_inputs = {
                    "sheet1": {
                        "company": f"{channel}",
                        "status" : f"{flag}",
                        "date" : f"{current_date}",
                    }
                }
                sheet_response = requests.post(mainLinks["sheet_endpoint"], json=sheet_inputs)
                print("hi")
                # print(sheet_response.text)
            except:
                error_message = sheet_response.json().get("error")
                print(f"Error: {error_message}")
                print("error in sheet 1")
        
        
        if flag2==1:
            try:
                
                
                # try:  
                sheet_inputs2 = {
                    "sheet2": {
                        "channel": f"{numArr[6]}",
                        "tl": f"{numArr[0]}",
                        "ts" : f"{numArr[1]}",
                        "date" : f"{current_date}",
                        "as" : f"{numArr[2]}",
                        "tc" : f"{numArr[3]}",
                        "ac" : f"{numArr[4]}",
                        "acc" : f"{numArr[5]}",
                    }
                }
                sheet_response2 = requests.post(mainLinks["sheet_endpoint2"], json=sheet_inputs2)
            except:
                print("error in sheet 2")
            
       
        i=i+1


    print(MessageToBeSent)
    print(MessageToBeSent2)

    maxretries = 5
    attempt = 0

    while attempt < maxretries:
        try:
            print(MessageToBeSent)
            # client.chat_postMessage(channel=testerLinks["channelM1"], text=MessageToBeSent)
            print(MessageToBeSent)
            pass
        except:
            attempt += 1
        else:
            break
    maxretries = 5
    attempt = 0

    while attempt < maxretries:
        try:
            print(MessageToBeSent2)
            # client.chat_postMessage(channel=testerLinks["channelM2"], text=MessageToBeSent2)
            pass
        except:
            attempt += 1
        
        else:
            break

    print(
        "Fetched a total of {} messages from channel {}".format(
            len(message_list),
            CHANNEL,
        )
    )
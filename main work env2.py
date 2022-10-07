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

# init web client
client = slack_sdk.WebClient(token='YOUR TOKEN')

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

if DayofWeek==4:
    # gets channels that we need
    channel_ID_list = []
    channel_NAME_list = []

    print("Found channels are: ")
    for data in client.conversations_list(types=["public_channel", "private_channel "], exclude_archived=True)["channels"]:
        # print(data["name"])
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
    for channel in channel_NAME_list:
        message_list=[]
        print(channel_ID_list[i])
        response = client.conversations_history(
            channel=channel_ID_list[i],
            limit=MESSAGES_PER_PAGE,
            latest=UNIXTime,
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
                cursor=response['response_metadata']['next_cursor']
            )
            assert response["ok"]
            messages = response['messages']
            messages_all = messages_all + messages


        response = client.conversations_history(
            channel=channel_ID_list[i],
            limit=MESSAGES_PER_PAGE,
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
                cursor=response['response_metadata']['next_cursor']
            )
            assert response["ok"]
            messages = response['messages']
        # print(messages_all)
        
        message_list = message_list+messages_all

        messages_needed = []
        flag = 0
        get_replies(messages_all,i)
        for message_dumpp in messages_all:
            # print(message_dumpp["text"])
            one_message = message_dumpp["text"].lower()
            # if (re.search(r"traffic.light:",one_message)):
            #     print("success")
            #     messages_needed.append("success")
            #     break
            numArr = []
            if (re.search(r"traffic.light:.?(:large_green_circle:|:large_yellow_circle:|:red_circle:|🔴|🟢|🟡)\ntarget.spend.\(budget\):.?([+-]?([0-9]*[.])?[0-9]+)\nactual.spend:.?([+-]?([0-9]*[.])?[0-9]+)\ntarget.cpa:.?([+-]?([0-9]*[.])?[0-9]+)\nactual.cpa:.?([+-]?([0-9]*[.])?[0-9]+)\n",one_message)):
                
                # print(one_message)
                # print("success")
                messages_needed.append("success")
                p = '[\d]+[.,\d]+|[\d]*[.][\d]+|[\d]+'
                if (":red_circle:" in one_message):
                    numArr.append(":red_circle:")
                elif (":large_yellow_circle:" in one_message):
                    numArr.append(":large_yellow_circle:")
                elif (":red_circle:" in one_message):
                    numArr.append(":red_circle:")
                else:
                    numArr.append("No status found")
                if re.search(p, one_message) is not None:
                    for catch in re.finditer(p, one_message):
                        print(catch[0])
                        numArr.append(catch[0])
                
                print(numArr)
                
            # if (re.search(r"client.status.?.?.?:large_green_circle:",one_message)):
            #     # print(re.search(r"Hasura",message_dumpp["text"]))
            #     messages_needed.append(message_dumpp["text"])
            #     flag=1
            #     break
            # elif (re.search(r"client.status.?.?.?:large_yellow_circle:",one_message)):
            #     # print(re.search(r"Hasura",message_dumpp["text"]))
            #     messages_needed.append(message_dumpp["text"])
            #     flag=2
            #     break
            # elif (re.search(r"client.status.?.?.?:red_circle:",one_message  )):
            #     # print(re.search(r"Hasura",message_dumpp["text"]))
            #     messages_needed.append(message_dumpp["text"])
            #     flag=3
            #     break

            
        print(flag)
        print(messages_needed)
        
        if flag==1:
            MessageToBeSent = MessageToBeSent+(f"{channel}: :large_green_circle:\n")
        if flag==2:
            MessageToBeSent = MessageToBeSent+(f"{channel}: :large_yellow_circle:\n")
        if flag==3:
            MessageToBeSent = MessageToBeSent+(f"{channel}: :red_circle:\n")
        
        #updating to google sheet
        
        #updating to google sheet
        sheet_endpoint = "YOUR API KEY"
        sheet_inputs = {
            "sheet1": {
                "company": f"{channel}",
                "status" : f"{flag}",
                "date" : f"{current_date}",
            }
        }

        sheet_response = requests.post(sheet_endpoint, json=sheet_inputs)

        print(sheet_response.text)
        i=i+1


    print(MessageToBeSent)

    maxretries = 5
    attempt = 0

    while attempt < maxretries:
        try:
            client.chat_postMessage(channel="C03T226TGBG", text=MessageToBeSent)
            pass
        except http.client.IncompleteRead:
            attempt += 1
        else:
            break

    print(
        "Fetched a total of {} messages from channel {}".format(
            len(message_list),
            CHANNEL,
        )
    )

        except http.client.IncompleteRead:
            attempt += 1
        else:
            break

    print(
        "Fetched a total of {} messages from channel {}".format(
            len(message_list),
            CHANNEL,
        )
    )

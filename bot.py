# -*- coding: utf-8 -*-
"""
In this file, we'll create a python Bot Class.
"""
import shortuuid
import os
import json
from slackclient import SlackClient
from python_mysql_connect import iter_row, getRoomType, getRoomInfo, getAvailableRoomInfo, getRoomAvailabilityByType, getRoomAvailabilityByDate, bookRoom, getBookingByEmail
from flask import make_response

import os.path
import sys

try:
    import apiai
except ImportError:
    sys.path.append(
        os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir)
    )
    import apiai

CLIENT_ACCESS_TOKEN = 'f98dc606670d4d4f868d0424f62e03e6'


# Messages

WELCOME_MESSAGE = " Welcome to Hotel California! How can I help you ?"

# 

BOOKING_IN_PROGRESS = {}


class Bot(object):
    """ Instanciates a Bot object to handle Slack interactions."""
    def __init__(self):
        super(Bot, self).__init__()
        self.oauth = {"client_id": os.environ.get("CLIENT_ID"),
                      "client_secret": os.environ.get("CLIENT_SECRET"),
                      "scope": "bot"}
        self.verification = os.environ.get("VERIFICATION_TOKEN")
        self.client = SlackClient("xoxb-275349460131-zeL0WUalzSkyXwMgvuBpJy5I")
        #self.client = SlackClient("")

    def auth(self, code):
        """
        A method to exchange the temporary auth code for an OAuth token
        which is then saved it in memory on our Bot object for easier access.
        """
        auth_response = self.client.api_call("oauth.access",
                                             client_id=self.oauth['client_id'],
                                             client_secret=self.oauth[
                                                            'client_secret'],
                                             code=code)
        self.user_id = auth_response["bot"]["bot_user_id"]
        print("AUTH RESPONSE")
        print(auth_response["bot"]["bot_access_token"])
        self.client = SlackClient(auth_response["bot"]["bot_access_token"])

    def getAPIAIResponseObject(self, message_text, userid):

        print(message_text)

        ai = apiai.ApiAI(CLIENT_ACCESS_TOKEN)

        request = ai.text_request()
        request.lang = 'en'
        request.session_id = userid
        request.query = message_text
        response = request.getresponse()

        response_json = response.read()
        #print (response_text)

        responseObj = json.loads(response_json)
        return responseObj


    def handleMessage(self, message):
        
        print(message)
        text = message.get('text')
        channel = message["channel"]
        responseObj = self.getAPIAIResponseObject(text, message["user"])

        print(responseObj)
        self.interprete_response(responseObj, channel, message["user"])


    def interprete_response(self, responseObj, channel, user_id):
        response_message = responseObj["result"]["fulfillment"]["messages"][0]["speech"]
        action = responseObj["result"]["action"]
        message_attachments = None

        if action == "smalltalk.greetings.hello":
            response_message += WELCOME_MESSAGE
            self.send_response(response_message, message_attachments, channel)

        elif action.startswith('smalltalk.'):
            self.send_response(response_message, message_attachments, channel)

        else:
            
            intent = self.get_value_if_key_exists(responseObj["result"]["metadata"], "intentName")
            room_type = self.get_value_if_key_exists(responseObj["result"]["parameters"],"RoomType")
            date_period = self.get_value_if_key_exists(responseObj["result"]["parameters"], "date-period")
            bActionComplete = responseObj["result"]["actionIncomplete"] == False
            email = self.get_value_if_key_exists(responseObj["result"]["parameters"],"email")
            dates = date_period.split("/")

            if bActionComplete:
                
                if intent == "Booking":
                    arr_available_rooms = getRoomAvailabilityByType(room_type)
                    if len(arr_available_rooms) == 0:
                        response_message = "Sorry. We don't have " + room_type + " rooms available from " + dates[0] + " to " + dates[1]
                    else:
                        response_message = "Thank you " + email + " . we have some " + room_type + " rooms available from " + dates[0] + " to " + dates[1]
                        BOOKING_IN_PROGRESS[user_id] = {}
                        BOOKING_IN_PROGRESS[user_id]["msg"] = response_message
                        BOOKING_IN_PROGRESS[user_id]["channel"] = channel
                        message_attachments = [
                                {
                                    "text": "Are you sure you want to book this room ?",
                                    "callback_id": "booking",
                                    "color": "warning",
                                    "attachment_type": "default",
                                    "actions": [
                                        {
                                            "name": "confirm_booking",
                                            "text": ":hotel: Pay Later and Confirm Booking",
                                            "type": "button",
                                            "value": "confirm_booking"
                                        },
                                        {
                                            "name": "pay_and_confirm_booking",
                                            "text": ":hotel: Pay Now and Confirm Booking",
                                            "type": "button",
                                            "value": "pay_and_confirm_booking"
                                        }
                                    ]
                                }
                            ]
                elif intent == "cancellation":
                    booked_room = getBookingByEmail(email)
                    print("BOOKED ROOM Info", booked_room)

                    if booked_room == None:
                        response_message = "Sorry. We couldn't find any booking with email id: " + email
                    else:
                        
                        attachment_text = "Email: " + email + "\n" \
                                            "Room Type: " + booked_room[1] + "\n" \
                                            "Date: " + booked_room[2].strftime('%Y-%m-%d') + " to " + booked_room[3].strftime('%Y-%m-%d')  + "\n";

                        response_message = "Here is your booking details. Are you sure you want to cancel your booking ?"
                        message_attachments = [
                                {
                                    "text": attachment_text,
                                    "callback_id": "booking",
                                    "color": "danger",
                                    "attachment_type": "default",
                                    "actions": [
                                        {
                                            "name": "cancel_booking",
                                            "text": "Cancel Booking",
                                            "type": "button",
                                            "value": "cancel_booking"
                                        }
                                    ]
                                }
                            ]
                
                elif intent == "ShowMyBooking":
                    booked_room = getBookingByEmail(email)
                    print("BOOKED ROOM Info", booked_room)
                    
                    if booked_room == None:
                        response_message = "Sorry. We couldn't find any booking with email id: " + email
                    else:
                        
                        attachment_text = "Email: " + email + "\n" \
                                            "Room Type: " + booked_room[1] + "\n" \
                                            "Date: " + booked_room[2].strftime('%Y-%m-%d') + " to " + booked_room[3].strftime('%Y-%m-%d')  + "\n";

                        response_message = "Here is your booking details."
                        message_attachments = [
                                {
                                    "text": attachment_text,
                                    "callback_id": "booking",
                                    "color": "good",
                                    "attachment_type": "default"
                                }
                            ]


            self.send_response(response_message, message_attachments, channel)

    def send_response(self, response_message, message_attachments, channel):
        
        print("message_attachments")
        print(message_attachments)

        if message_attachments == None:
            print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
            self.client.api_call("chat.postMessage",
                            channel=channel,
                            text=response_message)
        
        else:
            print("###########################################")
            self.client.api_call("chat.postMessage",
                            channel=channel,
                            text=response_message,
                            attachments=json.dumps(message_attachments))            

    def show_booking_confirmation(self, room_type, date_period, email):
        dates = date_period.split("/")
        confimationId = shortuuid.ShortUUID().random(length=6).upper()
        message = {
            "as_user": False,
            "replace_original": True,
            "response_type": "ephemeral",
            "text": "*Booking Confirmation:*:\n Here's details about your booking at Hotel California.",
            "attachments": [{
                "attachment_type": "default",
                "mrkdwn_in": ["text", "pretext"],
                "color": "good",
                "text": "Booking Confirmation ID: " + confimationId + "\n"
                        "Email: " + email + "\n"
                        "Room Type: " + room_type + "\n"
                        "Date: " + dates[0] + " to " + dates[1]  + "\n",
                "callback_id": "booking",
                "actions": [
                    {
                        "name": "email_confirmation",
                        "text": ":email: Send Email Confirmation",
                        "type": "button",
                        "value": "email_confirmation"
                    },
                    {
                        "name": "sms_confirmation",
                        "text": ":phone: Send SMS Confirmation",
                        "type": "button",
                        "value": "sms_confirmation"
                    }
                ]
                
            }]}
        return message

    def show_room_not_available(self, room_type, date_period):
        message = {
        "as_user": False,
        "replace_original": False,
        "response_type": "ephemeral",
        "text": "Sorry. Room you are looking is no more available."
        }
        return message


    def show_email_sent(self, room_type, date_period, email):
        
        message = {
            "as_user": False,
            "replace_original": False,
            "response_type": "ephemeral",
            "text": "I have sent booking confirmation email to " + email + ". Thanks for choosing Hotel California.",
            }
        return json.dumps(message)

    def show_sms_sent(self, room_type, date_period, mobile):
        
        message = {
            "as_user": False,
            "replace_original": False,
            "response_type": "ephemeral",
            "text": "I have sent booking confirmation to " + mobile + ". Thanks for choosing Hotel California.",
            }
        return json.dumps(message)

    def show_booking_cancellation_info(self, response_msg):
        
        message = {
            "as_user": False,
            "replace_original": False,
            "response_type": "ephemeral",
            "text": response_msg,
            }
        return json.dumps(message)


    def get_value_if_key_exists(self, dic, key):
        if key in dic:
            return dic[key]
        return ""

    def OpenPaymentDialog(self, trigger_id):

        # Show the ordering dialog to the user
        open_dialog = self.client.api_call(
            "dialog.open",
            trigger_id=trigger_id,
            dialog={
                "title": "Make Payment",
                "submit_label": "Submit",
                "callback_id":  "payment_form",
                "elements": [
                    {
                        "label": "Credit Card Number",
                        "type": "text",
                        "name": "card_number",
                        "placeholder": "Card Number"
                    },
                    {
                        "label": "Card Holder Name",
                        "type": "text",
                        "name": "card_holder_name",
                        "placeholder": "Card Holder Name"
                    },
                    {
                        "label": "Expiry Year",
                        "type": "select",
                        "name": "expiry_year",
                        "placeholder": "Select a expiry year",
                        "options": [
                            {
                                "label": "2017",
                                "value": "2017"
                            },
                            {
                                "label": "2018",
                                "value": "2018"
                            },
                            {
                                "label": "2019",
                                "value": "2019"
                            },
                            {
                                "label": "2020",
                                "value": "2020"
                            },
                            {
                                "label": "2021",
                                "value": "2021"
                            },
                            {
                                "label": "2022",
                                "value": "2022"
                            },
                            {
                                "label": "2023",
                                "value": "2023"
                            },
                            {
                                "label": "2024",
                                "value": "2024"
                            },
                            {
                                "label": "2025",
                                "value": "2025"
                            },
                            {
                                "label": "2026",
                                "value": "2026"
                            },
                            {
                                "label": "2027",
                                "value": "2027"
                            },
                            {
                                "label": "2028",
                                "value": "2028"
                            },
                            {
                                "label": "2029",
                                "value": "2029"
                            },
                            {
                                "label": "2030",
                                "value": "2030"
                            },
                            {
                                "label": "2031",
                                "value": "2031"
                            },
                            {
                                "label": "2032",
                                "value": "2032"
                            },
                            {
                                "label": "2033",
                                "value": "2033"
                            },
                            {
                                "label": "2034",
                                "value": "2034"
                            },
                            {
                                "label": "2035",
                                "value": "2035"
                            },
                            {
                                "label": "2036",
                                "value": "2036"
                            }
                        ]
                    },
                    {
                        "label": "Expiry Month",
                        "type": "select",
                        "name": "expiry_month",
                        "placeholder": "Select a expiry month",
                        "options": [
                            {
                                "label": "1 - Jan",
                                "value": "1"
                            },
                            {
                                "label": "2 - Feb",
                                "value": "2"
                            },
                            {
                                "label": "3 - Mar",
                                "value": "3"
                            },
                            {
                                "label": "4 - Apr",
                                "value": "4"
                            },
                            {
                                "label": "5 - May",
                                "value": "5"
                            },
                            {
                                "label": "6 - Jun",
                                "value": "6"
                            },
                            {
                                "label": "7 - Jul",
                                "value": "7"
                            },
                            {
                                "label": "8 - Aug",
                                "value": "8"
                            },
                            {
                                "label": "9 - Sep",
                                "value": "9"
                            },
                            {
                                "label": "10 - Oct",
                                "value": "10"
                            },
                            {
                                "label": "11 - Nov",
                                "value": "11"
                            },
                            {
                                "label": "12 - Dec",
                                "value": "12"
                            }
                        ]
                    },
                    {
                        "label": "CVV",
                        "type": "text",
                        "name": "cvv",
                        "placeholder": "Please enter CVV"
                    },
                ]
            }
        )

        print(open_dialog)

    def get_user_booking_progress_info(self, user_id):
        if user_id in BOOKING_IN_PROGRESS:
            return BOOKING_IN_PROGRESS[user_id]
        return ""

    def send_confirmation_message(self, res_json, channel):
        self.client.api_call(
            "chat.postMessage",
            channel=channel,
            text=res_json["text"],
            attachments=res_json["attachments"]
        )
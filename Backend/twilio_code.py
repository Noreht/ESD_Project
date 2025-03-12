# from: https://medium.com/@agarwalsrishti367/sending-sms-messages-with-twilio-and-python-91f78941d1c3


from twilio.rest import Client

# Account Credentials of the Twilio account

# "YOUR_ACCOUNT_SID" and "YOUR_ACCOUNT_TOKEN" are placeholders.
account_SID, account_token = "YOUR_ACCOUNT_SID", "YOUR_ACCOUNT_TOKEN"

# "YOUR_TWILIO_PHONE_NO" is a placeholder.
twilio_phone_no = "YOUR_TWILIO_PHONE_NO"

# My phone number where you intend to receive the SMS
my_phone_no = "+6588164892"

# Create a Twilio client
client = Client(account_SID, account_token)

# Send the SMS message
message = client.messages.create(
    body = "This is a test message using Python and Twilio.",
    from_ = twilio_phone_no,
    to = my_phone_no
)

print("SMS sent successfully! Message SID: {}".format(message.sid))

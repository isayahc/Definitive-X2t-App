from twilio.rest import Client
from config import APIs

client = Client(APIs().getTwilioCreditals())
message = client.messages.create(
                              body='Hi there! I cost money, bro',
                              from_='+1 205 304 5988',
                              to='+13474320300'
                          )

print(message.sid)
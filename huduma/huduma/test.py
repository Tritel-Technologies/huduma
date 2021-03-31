# works with both python 2 and 3
from __future__ import print_function

import africastalking

class SMS:
	def __init__(self):
		# Set your app credentials
		self.username = "investment"
		self.api_key = "bd144c4ab4b995a825dc5479f6642c9703bef65886c919b1482f390ea37eaa53"

		# Initialize the SDK
		africastalking.initialize(self.username, self.api_key)

		# Get the SMS service
		self.sms = africastalking.SMS

	def send(self):
		# Set the numbers you want to send to in international format
		recipients = ["+254717349800"]

		# Set your message
		message = "I'm a lumberjack and it's ok, I sleep all night and I work all day";

		# Set your shortCode or senderId
		sender = "DENNIS"
		try:
			# Thats it, hit send and we'll take care of the rest.
			response = self.sms.send(message, recipients, sender)
			print (response)
		except Exception as e:
			print ('Encountered an error while sending: %s' % str(e))

if __name__ == '__main__':
	SMS().send()




#from datetime import datetime, timedelta
#start = datetime(2019,4,23)
#start += timedelta(days = 10)
#print(start)

#for i in range(6,11):
#	print(i) 


related partner --> email
update cases with id of new related partner

https://www.odoo.com/forum/help-1/question/how-to-modify-the-customer-portal-form-27511
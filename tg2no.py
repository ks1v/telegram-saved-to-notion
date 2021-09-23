import configparser
from telethon import TelegramClient, events, sync
import json

from telethon.tl.types import (PeerChannel)
from telethon.tl.functions.messages import (GetHistoryRequest)



def loadSavedMessages(saved_messages_tg, total_count_limit = 1000):
	offset_id = 0
	limit = 100
	saved_messages_dict = []
	total_messages = 0

	while True:
		print("Current Offset ID is:", offset_id, "; Total Messages:", total_messages)
		history = client(GetHistoryRequest(
			peer=saved_messages_tg,
			offset_id=offset_id,
			offset_date=None,
			add_offset=0,
			limit=limit,
			max_id=0,
			min_id=0,
			hash=0
		))
		if not history.messages:
			break
			
		messages = history.messages
		
		for message in messages:
			saved_messages_dict.append(message.to_dict())
				
		offset_id = messages[len(messages) - 1].id
		
		total_messages = len(saved_messages_dict)
		
		if total_count_limit != 0 and total_messages >= total_count_limit:
			break
	
	print('Total loaded', len(saved_messages_dict), 'messages')
	return saved_messages_dict

def utf2json(object):
	return json.dumps(object, default=str, ensure_ascii=False).encode('utf8').decode()


def writeMessages(dict, filename): 
	jsons = []
	for message in dict:
		jsons.append(utf2json(message))

	with open(filename, 'w', encoding='utf8') as json_file:
		json.dump(jsons, json_file, ensure_ascii=False)


	


# Reading Configs
config = configparser.ConfigParser()
config.read("config.ini")
api_id = config['Telegram']['api_id']
api_hash = config['Telegram']['api_hash']
phone = config['Telegram']['phone']
username = config['Telegram']['username']


client = TelegramClient(username, api_id, api_hash)
client.start()
print("Client created")

# Ensure you're authorized
if not client.is_user_authorized():
	client.send_code_request(phone)
	try:
		client.sign_in(phone, input('Enter the code: '))
	except SessionPasswordNeededError:
		client.sign_in(password=input('Password: '))
		

# Create instance of saved messages
saved_messages_tg = client.get_entity('self')

# load saved messages and write as json
saved_messages_dict = loadSavedMessages(saved_messages_tg, total_count_limit = 500)
writeMessages(saved_messages_dict, 'saved_messages.json')





with open('saved_messages.json', 'r') as infile:
	saved_messages_loaded = json.load(infile)


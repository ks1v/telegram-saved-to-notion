import configparser
import json
import os
import pandas as pd

from datetime import timedelta
from datetime import datetime
from telethon import TelegramClient, events, sync
from telethon.tl.functions.messages import GetHistoryRequest
from telethon.tl.types import PeerChannel
from pprint import pprint

def checkAuth(client):
	if not client.is_user_authorized():
		client.send_code_request(phone)
		try:
			client.sign_in(phone, input('Enter the code: '))
		except SessionPasswordNeededError:
			client.sign_in(password=input('Password: '))


def processMedia(message, client, path):
	msg_media_filename = client.download_media(message.media)
	msg_media_filename_new = path+str(message.id)+'_'+msg_media_filename
	os.rename(msg_media_filename, msg_media_filename_new)
	return os.path.abspath(msg_media_filename_new)


def processContact(message):
	# clean VCard payload if a message has it
	vcard_str = ''
	if hasattr(message.media, 'vcard'): 
		vcard = message.media.vcard.split('\n')
		vcard_for_removal=[]

		for vcard_field in vcard:
			if vcard_field.startswith('BEGIN:') or vcard_field.startswith('VERSION:') or vcard_field.startswith('END:') or vcard_field.startswith('FN:') or vcard_field.startswith('N:'):
				vcard_for_removal.append(vcard_field)
			if hasattr(message.media, 'phone_number') and vcard_field.startswith('TEL'):
				vcard_for_removal.append(vcard_field)
			if hasattr(message.media, 'address') and vcard_field.startswith('ADR'):
				vcard_for_removal.append(vcard_field)
				
		for vcard_field in vcard_for_removal:
			vcard.remove(vcard_field)

		vcard_str = '\n'.join(vcard)
		
	msg_message = '\n'.join([message.message, 
						' '
						'Name: ' + message.media.first_name + ' ' + message.media.last_name, 
						'Phone: ' + message.media.phone_number, 
						vcard_str
						])

	return msg_message


def processLocation(message):
	msg_message = '\n'.join([message.message, ' '
							'Coordinates: ' + str(message.media.geo.lat) + ', ' + str(message.media.geo.long)])
	if hasattr(message.media, 'title'): 
		msg_message = '\n'.join([msg_message, 'Name: ' + message.media.title])
	if hasattr(message.media, 'address'): 
		msg_message = '\n'.join([msg_message, 'Address: ' + message.media.address]) 

	return msg_message
	

# We need to fold as much message's rich content into text message as possible (contacts, locations)
# Media and Documents are downloaded 
def processMessage(message, client, media_path, tz_shift): 
	msg_message = str(message.message)
	msg_datetime = message.date + timedelta(hours = tz_shift)
	msg_media_filename = ''

	if hasattr(message, 'media') : # message has an attachment
		if hasattr(message.media, 'photo') or hasattr(message.media, 'document'): # downloadable
			msg_media_filename = processMedia(message, client, media_path)
		if hasattr(message.media, 'vcard'): # convert contact to text
			msg_message = processContact(message)
		if hasattr(message.media, 'geo'): # convert location to text 
			msg_message = processLocation(message)
		
	msg_processed = {'id': str(message.id), 
					'dttm': msg_datetime,
					'date': msg_datetime.date(),
					'time': msg_datetime.time(),
					'text': msg_message,
					'filename': msg_media_filename
					}
	
	return msg_processed


def loadSavedMessages(saved_messages_tg, total_count_limit = 1000, tz_shift = 3):
	offset_id = 0
	batch_size = 100
	total_messages = 0
	processed_messages = [] # list of dicts which stores processed messages
	
	# create directory for saving messages' media 
	media_path = './media_' + datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + '/'
	os.makedirs(media_path)

	while True:
		print("Current Offset ID is:", offset_id, "; Total Messages:", total_messages)

		# load a batch of messages 
		history = client(GetHistoryRequest(
			peer=saved_messages_tg,
			offset_id=offset_id,
			offset_date=None,
			add_offset=0,
			limit=batch_size,
			max_id=0,
			min_id=0,
			hash=0
		))
		if not history.messages:
			break
		
		# porcess loaded batch of messages
		for message in history.messages:
			print('\t message.id = ', str(message.id))
			msg_processed = processMessage(message, client, media_path, tz_shift)
			processed_messages.append(msg_processed)
				
		offset_id = history.messages[len(history.messages) - 1].id
		total_messages = len(processed_messages)
		
		if total_count_limit != 0 and total_messages >= total_count_limit:
			break
	
	print('Total loaded', len(processed_messages), 'messages')
	return processed_messages


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
media_path = config['Processing']['media_path']
tz_shift = int(config['Processing']['tz_shift'])


client = TelegramClient(username, api_id, api_hash)
client.start()
print("Client created")

checkAuth(client)



		



# Create instance of saved messages
tg_user = client.get_entity('self')

# load saved messages and write as json
processed_messages = loadSavedMessages(tg_user, total_count_limit = 100000)
writeMessages(processed_messages, 'processed_messages_all.json')






## Calculate adjusted date

with open('processed_messages_all.json', encoding='utf8') as json_file:
	processed_messages_tmp = json.load(json_file)

processed_messages = []

for row in processed_messages_tmp:
	processed_messages.append(json.loads(row))  


const_seconds_in_a_hour = 60*60

df = pd.DataFrame(processed_messages)
df = df.set_index('id')
print(df.index)
df['dttm'] = pd.to_datetime(df['dttm'].astype(str).str[:-6], format='%Y-%m-%d %H:%M:%S')
df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d').dt.date
df['time'] = pd.to_datetime(df['time'], format='%H:%M:%S').dt.time

df = df.sort_values('dttm')

df['dttm_unix'] = (df.dttm - pd.Timestamp("1970-01-01").tz_localize(None)) // pd.Timedelta('1s')
df['dttm_diff'] = (df.dttm_unix.rolling(2).apply(lambda x: x[-1]-x[0]).shift(-1) / const_seconds_in_a_hour ).round(2).fillna(0)
df['hour'] = df.time.apply(lambda x: x.hour)

df['flg_gap'] = (df.dttm_diff >= 5) & (df.hour <=8) 
df['gap_hour'] = df.hour.where(df.flg_gap).groupby(df.date, sort=False).transform(min)
df['flg_retain_date'] = df.hour <= df.gap_hour

df.date_adj = None
df.loc[df.flg_retain_date, 'date_adj'] = df.date - pd.Timedelta('1day')
df.loc[df.date_adj.isna(), 'date_adj'] = df.date  
df['check_date_diff'] = df.date - df.date_adj
df['check_final'] = (df.check == pd.Timedelta('1day')) == df.flg_retain_date

# check
df.drop('text',1).drop('filename',1).head(20)
df.drop('text',1).drop('filename',1).iloc[range(-45, -20), :]

for col in ['dttm_unix', 'dttm_diff','hour','flg_gap','gap_hour']:
	df = df.drop(col,1)





client.stop()





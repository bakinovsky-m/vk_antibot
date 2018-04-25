import vk_api as vk
import sqlite3
from pathlib import Path

DB_FILENAME = 'antibot.db'
BOT_USER_ID = 0
API = None
BOT_FRIENDS = None

def create_db(sql_cursor):
	c.execute('''
		CREATE TABLE if not exists accounts (
		id int primary key unique,
		first_name text, 
		last_name text,
		affected int
		)
		''')
	c.execute('''
		CREATE TABLE if not exists groups (
		id int primary key unique,
		name text,
		screen_name text
		)
		''')

	c.execute('''
		CREATE TABLE if not exists relations (
		source int,
		target int,
		foreign key(source) references accounts(id),
		foreign key(target) references accounts(id)
		)
		''')

	c.execute('''
		CREATE TABLE if not exists accounts_groups(
		account_id int,
		group_id int,
		foreign key (account_id) references accounts(id),
		foreign key (group_id) references groups(id)
		)
		''')

def get_creds():
	if not Path('creds.txt').is_file():
		raise FileNotFoundError('I need creds.txt file!')
	f = open('creds.txt')
	login = f.readline()
	password = f.readline()
	return (login, password)

def is_affected(a):
	# print('Checking if {} {} is affected by bot'.format(a['first_name'], a['last_name']), end=' ', flush=True)
	# a_followers = API.users.getFollowers(user_id=a['id'])
	# if a['id'] in BOT_FRIENDS['items'] or BOT_USER_ID in a_followers['items']:
	if a['id'] in BOT_FRIENDS['items']:
		# print('YES')
		return True
	else:
		# print('NO')
		return False

db_file = Path(DB_FILENAME)
if db_file.is_file():
	db_file.unlink()
db_file.touch()
conn = sqlite3.connect(DB_FILENAME)
c = conn.cursor()
create_db(c)

login, password = get_creds()
print('Authenticate, may take a while')
session = vk.VkApi(login=login, password=password)
session.auth()
API = session.get_api()

print('''Getting target's and bot's ids''')
users_request = API.users.get(user_ids='svetlanka_lashchuk, nadia677')
target_user = users_request[0]
BOT_USER_ID = users_request[1]['id']
BOT_FRIENDS = API.friends.get(user_id=BOT_USER_ID)

print('''Getting target friends''')
friends = API.friends.get(user_id=target_user['id'], fields='first_name, last_name')
friends = friends['items']
friends = [f for f in friends if f['first_name'] != 'DELETED' and 'deactivated' not in f.keys()]

## ALARM !!!!!

# friends = friends[:10]

## ALARM !!!!!

friends.append(target_user)

counter1 = 1
for f in friends:
	print('\nWorking on {} {}. {}/{}'.format(f['first_name'], f['last_name'], counter1, len(friends)))
	tmp = (f['id'], f['first_name'], f['last_name'], is_affected(f))
	c.execute('INSERT or ignore INTO accounts VALUES (?, ?, ?, ?)', tmp)

	print('''\tGetting friends of friend''')
	friends_of_friends = API.friends.get(user_id=f['id'], fields='first_name, last_name')['items']
	friends_of_friends = [ff for ff in friends_of_friends if 'deactivated' not in ff.keys()]
	ff_to_acc = []
	for ff in friends_of_friends:
		tmp = (ff['id'], ff['first_name'], ff['last_name'], is_affected(ff))

		ff_to_acc.append(tmp)

	ff_to_rel = [(f['id'], fff['id']) for fff in friends_of_friends if 'deactivated' not in f.keys()]
	c.executemany('''INSERT or ignore INTO accounts values (?, ?, ?, ?)''', ff_to_acc)
	c.executemany('INSERT INTO relations(source, target) values (?, ?)', ff_to_rel)

	# print('''\tWorking on groups''')
	# f_groups = API.groups.get(user_id=f['id'], extended=1)['items']
	# f_groups_to_sql = [(g['id'], g['name'], g['screen_name']) for g in f_groups]
	# c.executemany('''INSERT OR IGNORE INTO groups(id, name, screen_name) values (?, ?, ?)''', f_groups_to_sql)

	# f_groups_ids = [(f['id'], g['id']) for g in f_groups]
	# c.executemany('''INSERT INTO accounts_groups(account_id, group_id) values (?, ?)''', f_groups_ids)



	conn.commit()
	counter1 += 1

counter2 = 1
for friend in friends:
	print('Building relations of {} {}. {}/{}'.format(friend['first_name'], friend['last_name'], counter2, len(friends)))
	ff = API.friends.get(user_id=friend['id'])
	# c.execute('''SELECT id from ''')
	ff = ff['items']

	# to_db = [(friend['id'], f_id) for f_id in ff]

	c.execute('''SELECT id from accounts''')
	ids = c.fetchall()
	ids = [idd[0] for idd in ids]

	# print(ids)
	# import sys; sys.quit()
	to_db = [(friend['id'], idd) for idd in ids if idd in ff]


	c.executemany('''INSERT into relations(source, target) values (?, ?)''', to_db)
	conn.commit()
	counter2 += 1

conn.close()
import vk_api as vk
import sqlite3
from pathlib import Path

DB_FILENAME = 'antibot.db'

def create_db(sql_cursor):
	c.execute('''
		CREATE TABLE if not exists accounts (
		id int primary key unique,
		first_name text, 
		last_name text
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
api = session.get_api()

print('''Getting Sveta's id''')
# target_user = api.users.get(user_ids='svetlanka_lashchuk', v='5.21')
target_user = api.users.get(user_ids='nadia677', v='5.21')

sv_id = target_user[0]['id']

print('''Getting friends''')
friends = api.friends.get(user_id=sv_id, fields='first_name, last_name')
friends = friends['items']
friends = [f for f in friends if f['first_name'] != 'DELETED' and 'deactivated' not in f.keys()]
friends.append(target_user[0])
# for f in friends:
# 	print(f)

for f in friends:
	print('\nWorking on {} {}'.format(f['first_name'], f['last_name']))
	tmp = (f['id'], f['first_name'], f['last_name'])
	c.execute('INSERT or ignore INTO accounts VALUES (?, ?, ?)', tmp)

	print('''\tGetting friends of friend''')
	ff = api.friends.get(user_id=f['id'], fields='first_name, last_name')['items']
	ff_to_acc = [(fff['id'], fff['first_name'], fff['last_name']) for fff in ff if f['first_name'] != 'DELETED' and 'deactivated' not in f.keys()]
	ff_to_rel = [(f['id'], fff['id']) for fff in ff if f['first_name'] != 'DELETED' and 'deactivated' not in f.keys()]
	c.executemany('''INSERT or ignore INTO accounts values (?, ?, ?)''', ff_to_acc)
	c.executemany('INSERT INTO relations(source, target) values (?, ?)', ff_to_rel)

	print('''\tWorking on groups''')
	f_groups = api.groups.get(user_id=f['id'], extended=1)['items']
	f_groups_to_sql = [(g['id'], g['name'], g['screen_name']) for g in f_groups]
	c.executemany('''INSERT OR IGNORE INTO groups(id, name, screen_name) values (?, ?, ?)''', f_groups_to_sql)

	f_groups_ids = [(f['id'], g['id']) for g in f_groups]
	# print(f_groups_ids)
	c.executemany('''INSERT INTO accounts_groups(account_id, group_id) values (?, ?)''', f_groups_ids)
	conn.commit()

# conn.commit()
conn.close()
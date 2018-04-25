sqlite3 antibot.db -header -csv "select id, (first_name || ' ' || last_name) as Label from accounts where affected = 1" > nodes.csv
# sqlite3 antibot.db -header -csv "select source, target from relations" > edges.csv
# sqlite3 antibot.db -header -csv "select accounts.id, (accounts.first_name || ' ' || accounts.last_name) as Label, groups.name as group_name from accounts join accounts_groups on accounts_groups.account_id = accounts.id join groups on accounts_groups.group_id = groups.id" > group.csv
# select accounts.id, accounts.first_name, accounts.last_name, groups.name from accounts join accounts_groups on accounts_groups.account_id = accounts.id join groups on accounts_groups.group_id = groups.id
# sqlite3 antibot.db -header -csv "select relations.source, relations.target from relations join accounts on "

# select * from relations join accounts on relations.source = accounts.id join accounts as accs on relations.target = accs.id where (accounts.affected = 1) and (accs.affected = 1);
sqlite3 antibot.db -header -csv "select relations.source as source, relations.target as target from relations join accounts on relations.source = accounts.id join accounts as accs on relations.target = accs.id where (accounts.affected = 1) and (accs.affected = 1);" > edges.csv

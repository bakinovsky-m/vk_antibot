sqlite3 antibot.db -header -csv "select id, (first_name || ' ' || last_name) as Label from accounts" > nodes.csv
sqlite3 antibot.db -header -csv "select source, target from relations" > edges.csv
sqlite3 antibot.db -header -csv "select accounts.id, (accounts.first_name || ' ' || accounts.last_name) as Label, groups.name as group_name from accounts join accounts_groups on accounts_groups.account_id = accounts.id join groups on accounts_groups.group_id = groups.id" > group.csv
# select accounts.id, accounts.first_name, accounts.last_name, groups.name from accounts join accounts_groups on accounts_groups.account_id = accounts.id join groups on accounts_groups.group_id = groups.id
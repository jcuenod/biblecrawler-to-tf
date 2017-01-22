rules = []
rules.append({
	"affected_records": ["Exod 6:6,1.1", "Exod 6:6,1.2"],
	"lexical_data": [{
		"id": "Exod 6:6,1.1",
		"betacode": "L.FMF70H",
		"hebrew": "לכן",
		"SDBH":"",
		"lexical_domain":""
	}]
})
rules.append({
	"affected_records": ["Song 6:12,6.1"],
	"lexical_data": [{
		"id": "Song 6:12,6.1",
		"betacode": "(AM.IY-",
		"hebrew": "עמי",
		"SDBH":"",
		"lexical_domain":""
	},{
		"id": "Song 6:12,6.2",
		"betacode": "NFDI75YB00",
		"hebrew": "נדיב",
		"SDBH":"",
		"lexical_domain":""
	},]
})
rules.append({
	"affected_records": ["Song 7:5,9.1"],
	"lexical_data": [{
		"id": "Song 7:5,9.1",
		"betacode": "B.AT-RAB.I80YM",
		"hebrew": "בת רבים",
		"SDBH":"B.AT~RAB.IYM_1a",
		"lexical_domain":"Names of Locations"
	}]
})



records_affected = []
for rule in rules:
	records_affected = records_affected + rule["affected_records"]

def rule_affected(record_id):
	return record_id in records_affected

processed = []
def solution_for_rule(record_id):
	for i in range(len(rules)):
		rule = rules[i]
		if record_id in rule["affected_records"]:
			if i in processed:
				return False
			else:
				processed.append(i)
				return rule["lexical_data"]

rules = []
# rules.append({
# 	"affected_records": ["Jer 29:23,18.1", "Jer 29:23,18.2"],
# 	"lexical_data": [{
# 		"id": "Jer 29:23,18.1",
# 		"betacode": "*HW.",
# 		"hebrew": "ה",
# 		"SDBH":"HW.)_1a",
# 		"lexical_domain":"Participants"
# 	},{
# 		"id": "Jer 29:23,18.2",
# 		"betacode": "*YOD\"(A",
# 		"hebrew": "וידע",
# 		"SDBH":"YD(_1a",
# 		"lexical_domain":"Know"
# 	}]
# })
rules.append({
	"affected_records": ["Judg 1:36,3.2", "Judg 1:36,4.1"],
	"lexical_data": [{
		"id": "Judg 1:36,3.2",
		"betacode": "M.A(:AL\"73H (AQ:RAB.I92YM",
		"hebrew": "מעלה עקרבים",
		"sdbh":"",
		"domain":"Names of Locations"
	}]
})
rules.append({
	"affected_records": ["2Kgs 9:27,17.2", "2Kgs 9:27,18.1"],
	"lexical_data": [{
		"id": "2Kgs 9:27,17.2",
		"betacode": "M.A(:AL\"73H (AQ:RAB.I92YM",
		"hebrew": "מעלה עקרבים",
		"sdbh":"",
		"domain":"Names of Locations"
	}]
})
rules.append({
	"affected_records": ["2Kgs 6:25,16.1", "2Kgs 6:25,16.2"],
	"lexical_data": [{
		"id": "2Kgs 6:25,16.1",
		"betacode": "X:AR""Y YOWNIYM",
		"hebrew": "חרייונים",
		"sdbh":"X:ARF)IYM_1a",
		"domain":"Body Products"
	}]
})

rules.append({
	"affected_records": ["Num 34:4,5.2", "Num 34:4,6.1"],
	"lexical_data": [{
		"id": "Num 34:4,5.2",
		"betacode": "M.A(:AL\"73H (AQ:RAB.I92YM",
		"hebrew": "מעלה עקרבים",
		"sdbh":"",
		"domain":"Names of Locations"
	}]
})
rules.append({
	"affected_records": ["Josh 15:3,4.2", "Josh 15:3,5.1"],
	"lexical_data": [{
		"id": "Josh 15:3,4.2",
		"betacode": "M.A(:AL\"73H (AQ:RAB.I92YM",
		"hebrew": "מעלה עקרבים",
		"sdbh":"",
		"domain":"Names of Locations"
	}]
})

rules.append({
	"affected_records": ["1Chr 4:12,10.1", "1Chr 4:12,11.1"],
	"lexical_data": [{
		"id": "1Chr 4:12,10.1",
		"betacode": "M.A(:AL\"73H (AQ:RAB.I92YM",
		"hebrew": "עיר נחשׁ",
		"sdbh":"",
		"domain":"Names of Locations"
	}]
})

rules.append({
	"affected_records": ["Ps 22:2,3.1", "Ps 22:2,3.2"],
	"lexical_data": [{
		"id": "Ps 22:2,3.1",
		"betacode": "MF74H",
		"hebrew": "למה",
		"sdbh":")\"L.EH_1a",
		"domain":"Identifiers"
	}]
})

rules.append({
	"affected_records": ["Job 19:29,11.1", "Job 19:29,11.2"],
	"lexical_data": [{
		"id": "Job 19:29,11.1",
		"betacode": "$AD.IYN",
		"hebrew": "שׁדין",
		"sdbh":"D.IYN",
		"domain":"Laws"
	}]
})

# Do to these as to Jeremiah (no - I'm just going to apply the sdbh categories kind of loosely)
#"Eccl 6:10,14.1",*$E,$E_1a,"Relations of Description",*$E
#"Eccl 6:10,14.2",*HAT:QIYP,TQP_1b,Strong,*HAT:QIYP
#"Ps 102:4,6.1",K.:,K._1a,"Relations of Description",K.:
#"Ps 102:4,6.2","MOW-Q""71D",,,"MOW-Q""71D"
#"Neh 2:13,16.1",*HA,H_1a,Identifiers,*HA
#"Neh 2:13,16.2",*M:PORWFCIYM,PRC_1b,Impact,*M:PORWFCIYM
#"2Kgs 7:15,14.1",*B.:,,,*B.:
#"2Kgs 7:15,14.2","*H""XFP:Z/FM",XPZ_1a,Attitude,"*H""XFP:Z/FM"

# Remove the bizarro things in here...
rules.append({
	"affected_records": [ \
		"2Kgs 19:31,10.1", \
		"2Kgs 19:37,9.1", \
		"2Sam 8:3,13.1", \
		"2Sam 16:23,9.1", \
		"2Sam 18:20,19.1", \
		"Jer 31:38,3.1", \
		"Jer 50:29,13.1", \
		"Judg 20:13,15.1", \
		"Ruth 3:5,6.1", \
		"Ruth 3:17,9.1" \
	],
	"lexical_data": []
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

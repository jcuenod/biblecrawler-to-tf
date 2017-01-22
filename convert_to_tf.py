import re
from tf.fabric import Fabric
import csv
import unicodedata
from betacode import decode
from rules import rule_affected, solution_for_rule


#read in csv
sdbh_counter = 0
ketiv = 0
qere = 0
rafe = 0
line = ""
sdbh_contents = []
sdbh_books = ['Hab', 'Prov', 'Esth', 'Eccl', 'Ps', 'Jonah', 'Mal', 'Neh', 'Hos', 'Exod', 'Joel', 'Obad', '1Chr', 'Judg', '1Sam', 'Ezra', 'Num', 'Ruth', 'Deut', 'Dan', 'Jer', 'Lev', '2Chr', '2Kgs', 'Isa', 'Zech', '2Sam', 'Lam', 'Gen', 'Mic', 'Song', 'Nah', 'Hag', 'Job', 'Zeph', 'Ezek', 'Josh', '1Kgs', 'Amos']

with open('sdbh.csv') as csvfile:
	reader = csv.DictReader(csvfile)
	for row in reader:
		if rule_affected(row["RecordId"]):
			solution = solution_for_rule(row["RecordId"])
			if solution:
				sdbh_contents = sdbh_contents + solution
			continue


		sdbh_counter += 1
		to_decode = re.sub(r'[\d\/]', '', row['HebrewText'])
		to_decode = re.sub(r'~', ' ', to_decode)

		if re.search(r'\*\*', to_decode):
			qere+=1
			continue
		if re.search(r'\*', to_decode):
			ketiv += 1
			to_decode = re.sub(r'\*', '', to_decode)
		if re.search(r',', to_decode):
			to_decode = re.sub(r'\,', '', to_decode)
			rafe += 1

		if to_decode == "_":
			continue

		sdbh_contents.append({
			"id": row["RecordId"],
			"betacode": row["HebrewText"],
			"hebrew": decode(to_decode)
		})


#clean up some funny stuff
l_suffix = ["מה", "כן"]
for i in reversed(range(len(sdbh_contents) - 2)):
	if sdbh_contents[i]["hebrew"] == "ל" and sdbh_contents[i+1]["hebrew"] in l_suffix:
		del sdbh_contents[i+1]
		sdbh_contents[i]["hebrew"] = "ל" + sdbh_contents[i+1]["hebrew"]

# Get words from SDBH
sdbh_words = []
sdbh_words_references = []
for match in sdbh_contents:
	if not match["id"].startswith("Gen "):
		continue
	if match["hebrew"] == "ס" or match["hebrew"] == "ף":
		continue
	sdbh_words.append(match["hebrew"])
	sdbh_words_references.append(match["id"])


TF = Fabric(locations='/home/jcuenod/Programming/text-fabric-data', modules='hebrew/etcbc4c')
api = TF.load('g_cons_utf8')
api.makeAvailableIn(globals())


verse_node = T.nodeFromSection(('Genesis', 1, 1))
book_node = L.u(verse_node, otype='book')[0]
tf_words = []
for w in L.d(book_node, otype='word'):
	if F.g_cons_utf8.v(w) != "":
		tf_words.append(F.g_cons_utf8.v(w))

final_chars = set('ךםןףץ')

counter = 0
print("sdbh units: ", len(sdbh_words))
print("  tf units: ", len(tf_words))
for i in range(len(min(sdbh_words, tf_words))):
	if unicodedata.normalize("NFKD", sdbh_words[i]) == unicodedata.normalize("NFKD", tf_words[i]):
		continue
	if sdbh_words[i] in final_chars:
		continue
	print(sdbh_words_references[i], ": ", sdbh_words[i], "=!=", tf_words[i])
	counter += 1
	if counter > 100:
		print("TOO MANY ISSUES - EXITING")
		exit()


if len(sdbh_words) != len(tf_words):
	print("WARNING: lists of unequal length, not all data has been compared")

import re
from datetime import datetime

from tf.fabric import Fabric
import csv
import unicodedata
from betacode import decode
from greekbeta_to_unicode import gk_decode
from rules import rule_affected, solution_for_rule


#read in csv
sdbh_counter = 0
ketiv = 0
qere = 0
rafe = 0
line = ""
sdbh_contents = []
sdbh_books = [ "Gen", "Exod", "Lev", "Num", "Deut", "Josh", "Judg", "1Sam", "2Sam", "1Kgs", "2Kgs", "Isa", "Jer", "Ezek", "Hos", "Joel", "Amos", "Obad", "Jonah", "Mic", "Nah", "Hab", "Zeph", "Hag", "Zech", "Mal", "Ps", "Job", "Prov", "Ruth", "Song", "Eccl", "Lam", "Esth", "Dan", "Ezra", "Neh", "1Chr", "2Chr" ]

print("Reading csv ...")
with open('processed_tfdata.csv') as csvfile:
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
			"hebrew": decode(to_decode),
			"domain": row["LexDomain"],
			"sdbh": row["SDBH"],
			"glemma": row["GLemma"]
		})
print("Completed csv prep")

glemma_missing_counter = 0
def get_glemma(obj):
	if "glemma" in obj:
		return obj["glemma"]
	else:
		global glemma_missing_counter
		glemma_missing_counter += 1
		return ""

# Get words from SDBH
def get_sdbh(book_abbreviation):
	sdbh_words = []
	sdbh_references = []
	sdbh_ids = []
	for i, match in enumerate(sdbh_contents):
		if not match["id"].startswith(book_abbreviation):
			continue
		if match["hebrew"] == "ס" or match["hebrew"] == "ף" or match["hebrew"] == "ן":
			continue
		sdbh_words.append(match["hebrew"])
		sdbh_references.append(match["id"])
		sdbh_ids.append(i)
	return sdbh_words, sdbh_references, sdbh_ids


TF = Fabric(locations='/home/jcuenod/Programming/text-fabric-data', modules='hebrew/etcbc4c')
api = TF.load('g_cons_utf8')
api.makeAvailableIn(globals())


def get_tf(book_abbreviation):
	verse_node = T.nodeFromSection((book_abbreviation, 1, 1), lang='sblspaceless')
	book_node = L.u(verse_node, otype='book')[0]
	tf_words = []
	tf_references = []
	tf_ids = []
	for w in L.d(book_node, otype='word'):
		tf_words.append(F.g_cons_utf8.v(w))
		tf_references.append(str(T.sectionFromNode(w)))
		tf_ids.append(w)
	return tf_words, tf_references, tf_ids

def replace_finals(word):
	return word.replace("ך", "כ") \
		.replace("ם", "מ") \
		.replace("ן", "נ") \
		.replace("ף", "פ") \
		.replace("ץ", "צ")

def _norm(w):
	return replace_finals(unicodedata.normalize("NFKD", w)).replace(" ", "")

def normalised_compare(w1, w2):
	return _norm(w1) == _norm(w2)



node_data = []
domains_to_ignore = ["Negators", "Identifiers"]
do_print = True
# for book_abbreviation in ["Gen"]:
for book_abbreviation in sdbh_books:
	tf_words, tf_references, tf_ids = get_tf(book_abbreviation)
	sdbh_words, sdbh_references, sdbh_ids = get_sdbh(book_abbreviation)
	offset_counter = 0
	def increment_offset_counter(offset_counter):
		offset_counter += 1
		# if offset_counter % 2500 == 0:
		# 	print("offsets: ", offset_counter)
		return offset_counter

	counter = 0
	if do_print:
		print(book_abbreviation, "SDBH units: ", len(sdbh_words), " TF units: ", len(tf_words))
	offset_sdbh = 0
	offset_tf = 0
	i = -1
	while i + offset_tf + 1 < len(tf_words) and i + offset_sdbh + 1 < len(sdbh_words):
		i += 1
		# for i in range(len(min(sdbh_words, tf_words))):
		if normalised_compare(sdbh_words[i + offset_sdbh], tf_words[i + offset_tf]):
			# if write_to_file:
				# write to file
			node_data.append((_norm(sdbh_words[i+offset_sdbh]), sdbh_contents[sdbh_ids[i+offset_sdbh]]["domain"], sdbh_references[i+offset_sdbh], get_glemma(sdbh_contents[sdbh_ids[i+offset_sdbh]])))
			continue
		elif sdbh_words[i + offset_sdbh] == "ישׂשכר" and tf_words[i + offset_tf] == "ישׂשׂכר":
			# variant spelling of Issachar
			node_data.append((_norm(sdbh_words[i+offset_sdbh]), sdbh_contents[sdbh_ids[i+offset_sdbh]]["domain"], sdbh_references[i+offset_sdbh], get_glemma(sdbh_contents[sdbh_ids[i+offset_sdbh]])))
			continue
		elif len(sdbh_words[i + offset_sdbh]) > len(tf_words[i + offset_tf]):
			# data from sdbh for one word goes to two...
			to_test = tf_words[i + offset_tf] + tf_words[i + offset_tf + 1]
			temp_offset = offset_tf + 1
			while len(_norm(to_test)) < len(_norm(sdbh_words[i + offset_sdbh])):
				temp_offset += 1
				to_test += tf_words[i + temp_offset]
			if normalised_compare(sdbh_words[i + offset_sdbh], to_test):
				for j in range(temp_offset - offset_tf + 1):
					if tf_words[i + offset_tf + j] == "":
						node_data.append(("","","",""))
					else:
						node_data.append((_norm(sdbh_words[i+offset_sdbh]), sdbh_contents[sdbh_ids[i+offset_sdbh]]["domain"], sdbh_references[i+offset_sdbh], get_glemma(sdbh_contents[sdbh_ids[i+offset_sdbh]])))
				offset_tf = temp_offset
				# if do_print:
				# 	print("  tf fix:", sdbh_references[i + offset_sdbh], ":SD: ", sdbh_words[i + offset_sdbh], "==", to_test, " :TF:", tf_references[i + offset_tf], "OFFSETS (tf, sdbh):", offset_tf, offset_sdbh)
				continue
		elif len(tf_words[i + offset_tf]) > len(sdbh_words[i + offset_sdbh]):
			# data from multiple sdbh goes to one tf word...
			to_test = sdbh_words[i + offset_sdbh] + sdbh_words[i + offset_sdbh + 1]
			temp_offset = offset_sdbh + 1
			while len(_norm(to_test)) < len(_norm(tf_words[i + offset_tf])):
				temp_offset += 1
				to_test += sdbh_words[i + temp_offset]
			if normalised_compare(tf_words[i + offset_tf], to_test):
				possibles = []
				last_resort = []
				prefer_me = []
				for j in range(temp_offset - offset_sdbh + 1):
					if sdbh_contents[sdbh_ids[i+offset_sdbh+j]]["domain"] == "":
						# ignore empty lexical domains
						continue
					if sdbh_contents[sdbh_ids[i+offset_sdbh+j]]["domain"] in domains_to_ignore:
						# ignore certain domains
						last_resort.append((_norm(sdbh_words[i+offset_sdbh+j]), sdbh_contents[sdbh_ids[i+offset_sdbh+j]]["domain"], sdbh_references[i+offset_sdbh+j], get_glemma(sdbh_contents[sdbh_ids[i+offset_sdbh+j]])))
						continue
					if len(_norm(sdbh_words[i+offset_sdbh+j])) == 1:
						# ignore certain domains
						last_resort.append((_norm(sdbh_words[i+offset_sdbh+j]), sdbh_contents[sdbh_ids[i+offset_sdbh+j]]["domain"], sdbh_references[i+offset_sdbh+j], get_glemma(sdbh_contents[sdbh_ids[i+offset_sdbh+j]])))
						continue
					if sdbh_contents[sdbh_ids[i+offset_sdbh+j]]["domain"] in map(lambda x: x[1], possibles):
						# if we already have this category, ignore it a second time
						#although maybe we should use the second one instead?
						continue
					if sdbh_contents[sdbh_ids[i+offset_sdbh+j]]["domain"] == "Names of Locations":
						# ignore names of locations -- maybe we will just end up using this value
						prefer_me.append((_norm(sdbh_words[i+offset_sdbh+j]), sdbh_contents[sdbh_ids[i+offset_sdbh+j]]["domain"], sdbh_references[i+offset_sdbh+j], get_glemma(sdbh_contents[sdbh_ids[i+offset_sdbh+j]])))
						continue
					possibles.append((_norm(sdbh_words[i+offset_sdbh+j]), sdbh_contents[sdbh_ids[i+offset_sdbh+j]]["domain"], sdbh_references[i+offset_sdbh+j], get_glemma(sdbh_contents[sdbh_ids[i+offset_sdbh+j]])))

				if len(possibles) > 1:
					print("POSSIBLES:", possibles)
				elif len(possibles) == 0:
					if len(prefer_me) > 0:
						if len(prefer_me) == 1:
							node_data.append(prefer_me[0])
						else:
							print("PREFER: ", prefer_me)
					elif len(last_resort) > 0:
						if len(last_resort) == 1:
							node_data.append(last_resort[0])
						else:
							print("LAST RESORT:", last_resort)
					else:
						# print("LAST RESORT/PREFER: not enough options...")
						node_data.append(("","","",""))
				else:
					if len(prefer_me) > 1:
						if len(prefer_me) == 1:
							node_data.append(prefer_me[0])
						else:
							print("PREFER: ", prefer_me)
					else:
						node_data.append(possibles[0])
				# if do_print:
				# 	print("sdbh fix:", sdbh_references[i + offset_sdbh], ":SD: ", to_test, "=", tf_words[i + offset_tf], " :TF:", tf_references[i + offset_tf], "OFFSETS (tf, sdbh):", offset_tf, offset_sdbh)

				offset_sdbh = temp_offset
				continue

		if do_print:
			print(sdbh_references[i + offset_sdbh], ":SD: ", sdbh_words[i + offset_sdbh], "=!=", tf_words[i + offset_tf], " :TF:", tf_references[i + offset_tf], "OFFSETS (tf, sdbh):", offset_tf, offset_sdbh)
		# Having tested, I'm fairly confident that there aren't any of these that mess up alignment:
		print("Guess I'll just append whatever...")
		node_data.append((_norm(sdbh_words[i+offset_sdbh]), sdbh_contents[sdbh_ids[i+offset_sdbh]]["domain"], sdbh_references[i+offset_sdbh], get_glemma(sdbh_contents[sdbh_ids[i+offset_sdbh]])))

		counter += 1
		if counter > 10:
			print("TOO MANY ISSUES - EXITING")
			exit()

	if do_print:
		if len(sdbh_words) - offset_sdbh != len(tf_words) - offset_tf:
			print("\nlast 5 words:")
			print("sdbh_words: ", " ".join(sdbh_words[len(sdbh_words) - 5:]), sdbh_references[-1])
			print("  tf_words: ", " ".join(tf_words[len(tf_words) - 5:]), tf_references[-1])
			print("WARNING: lists of unequal length, not all data has been compared")
		else:
			print("success ({0} nodes)".format(str(len(node_data))))


sdbh_filename = "sdbh.tf"
sdbh_fileheader = '''@node
@valueType=str
@writtenBy=James Cuénod & SDBH
@dateWritten={0}

'''.format(datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"))
print("writing file:", sdbh_filename)

with open(sdbh_filename, mode='wt', encoding='utf-8') as out:
	out.write(sdbh_fileheader)
	out.write('\n'.join(map(lambda x: x[1], node_data)))


lxx_filename = "lxxlexeme.tf"
lxx_fileheader = '''@node
@valueType=str
@writtenBy=James Cuénod & CCAT
@dateWritten={0}

'''.format(datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"))
print("writing file:", lxx_filename)

with open(lxx_filename, mode='wt', encoding='utf-8') as out:
	out.write(lxx_fileheader)
	out.write('\n'.join(map(lambda x: gk_decode(x[3]), node_data)))

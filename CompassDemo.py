from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime, date, timedelta
import random
import barnum
from geopy.geocoders import Nominatim, ArcGIS
import traceback

# create n documents
n = 10

client = MongoClient('mongodb://localhost:27017/')
db = client['compass']
collection = db['demo']

# choose geolocator
geolocator = Nominatim()
#geolocator = ArcGIS()

def offset():
	return (random.random()-0.5)/10.0

def calculate_age(born):
    today = date.today()
    return today.year - born.year - ((today.month, today.day) < (born.month, born.day))

def get_credit_card_number(cc):
	if (random.random() < 0.7):
		cc = cc[:-4]+"****"
		return cc
	return int(cc)

def random_date(start, end):
    delta = end - start
    int_delta = (delta.days * 24 * 60 * 60) + delta.seconds
    random_second = random.randrange(int_delta)
    return start + timedelta(seconds=random_second)

def create_object_id(when):
#	when = barnum.create_date(past=True, max_years_past=2, max_years_future=2)
	epoch = datetime.utcfromtimestamp(0)
	since_epoch = int((when - epoch).total_seconds())
	return ObjectId(oid="%6x" % since_epoch + str(ObjectId())[8:])

for i in range(0,n):
	try:
		(zipcode, city, state) = barnum.create_city_state_zip()
		for j in range(0,5):
			location = geolocator.geocode("%s, %s %s, USA" % (city, state, zipcode))
			if location != None:
				rlocation = geolocator.reverse("%s, %s" % (location.latitude, location.longitude))
				print rlocation.address[-3:]
				if rlocation.address[-3:] == "USA":
					break
				print ': %s, %s, %s' % (zipcode, city, state)
				print ': %s' % rlocation
			print "."
		if location != None:
			name = barnum.create_name()
			now = datetime.utcnow()
			then = now - timedelta(2 * 365)
			when = random_date(then, now)
			birthday = barnum.create_birthday()
			document = {
				"_id": create_object_id(when),
				"Name": ' '.join(name),
				"Address": {
					"Street": barnum.create_street(),
					"City": city,
					"State": state,
					"Zip": zipcode,
					"Location": {
						"type": "Point",
						"coordinates": [ location.longitude+offset(), location.latitude+offset() ]
					}
				},
				"DOB": {
					"Date": birthday.strftime("%B %d, %Y"),
					"Day": birthday.strftime("%A")
				},
				"Age": calculate_age(birthday),
				"LastLogin": random_date(when, now)
			}
			if (random.random() < 0.9):
				document['CreditCard'] = []
				for n in range(0, random.randint(1,4)):
					creditcard = barnum.create_cc_number()
					document['CreditCard'].append({
						"Type": creditcard[0],
						"Number": get_credit_card_number(creditcard[1][0])
						})
			if (random.random() < 0.8):
				if (random.random() < 0.9):
					document['JobTitle'] = barnum.create_job_title()
				if (random.random() < 0.9):
					document['Company'] = barnum.create_company_name()
			if (random.random() < 0.8):
				if (random.random() < 0.6):
					document['Email'] = barnum.create_email(name=name)
				else:
					document['Email'] = [ barnum.create_email(name=name), barnum.create_email(name=name) ]
			if (random.random() < 0.8):
				phone = barnum.create_phone(zipcode)
				if (random.random() < 0.75):
					document['Phone'] = phone
				else:
					toremove = ['(', ')', '-']
					document['Phone'] = int(phone.translate(None, ' '.join(toremove)))
			id = collection.insert_one(document).inserted_id
			print document
		else:
			print '! %s' % ((zipcode, city, state),)
	except:
		print '!'
		print traceback.print_exc()

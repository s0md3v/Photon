import json

def exporter(directory, method, datasets):
	if method.lower() == 'json':
		json_string = json.dumps(datasets, indent=4) # convert json_dict to a json styled string
		savefile = open('%s/exported.json' % directory, 'w+') # save
		savefile.write(json_string)
		savefile.close()

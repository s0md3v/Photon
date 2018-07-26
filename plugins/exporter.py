import json

json_dict = {
'files' : [],
'intel' : [],
'robots' : [],
'custom' : [],
'failed' : [],
'storage' : [],
'scripts' : [],
'external' : [],
'fuzzable' : [],
'endpoints' : [],
'processed' : []
}

def exporter(directory, method, *datasets):
	if method.lower() == 'json':
		for data, json_list in zip(datasets, json_dict): # iterating over two two arrays at once
			json_dict[json_list] = list(data) # replace blank lists in json_dict with results
		json_string = json.dumps(json_dict, indent=4) # convert json_dict to a json styled string
		savefile = open('%s/exported.json' % directory, 'w+') # save
		savefile.write(json_string)
		savefile.close()

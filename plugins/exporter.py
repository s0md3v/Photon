"""Support for exporting the results."""
import json


def exporter(directory, method, datasets):
	"""Export the results."""
	if method.lower() == 'json':
		# Convert json_dict to a JSON styled string
		json_string = json.dumps(datasets, indent=4)
		savefile = open('%s/exported.json' % directory, 'w+')
		savefile.write(json_string)
		savefile.close()

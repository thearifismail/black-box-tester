import json
import pathlib

sd  = pathlib.Path(__file__).parent.absolute()
cwd = pathlib.Path().absolute()

print("Script directory: " + str(sd))
print("Current working directory" + str(cwd))

with open('cachet-tools/nested-services.json') as json_file:
    data = json.load(json_file)
    for g, svc in data.items():
        print(g)
        print('') 
        for s in svc:
            print('Name: ' + s['name'])
            print('Label: ' + s['label'])
            print('URI: ' + s['uri'])
            print('')
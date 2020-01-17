import json
import logging
import pprint

# format the logger message
logging.basicConfig(level='INFO', format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %H:%M:%S %p: ')
logger = logging.getLogger(__name__)

pp = pprint.PrettyPrinter(indent=4, compact=True)

class Services:
    'class for defining hosted services in Insights'
    groupcount   = 0
    serviceCount = 0

    def __init__(self):
        with open('/hosted-services.json') as services_file:
            self.data = json.load(services_file)
            Services.groupcount = len(self.data)
            print("Group count: " + str(Services.groupcount))
            
    # end of init

    def getData(self):
        return self.data
    
    def getServiceNameByLabel(self, label):
        for g, services in self.data.items():
            for svc in services:
                if svc['label'] == label:
                    return svc['name']
    # end of getServiceByLabel

    def getServiceUriByLabel(self, label):
        for g, services in self.data.items():
            for svc in services:
                if svc['label'] == label:
                    return svc['uri']
    # end of getServiceByLabel


def main():
    svcs  = Services()
    name  = svcs.getServiceNameByLabel("3Scale")
    uri   = svcs.getServiceUriByLabel("3Scale")

    pp.pprint(name)
    pp.pprint(uri)


if __name__ == '__main__':
   logger.info ("Let's kick the pig!")
   main()

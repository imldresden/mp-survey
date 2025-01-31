import csv
import json
import argparse
import logging

# properties without a filter or view
excludeProp = ["Name", "Authors", "Year", "DOI", "Bibtex"]

optionals = ["Optional Category"]

# categories that will be shown in the website
includeProp = {
  # fixed
  "Name":"String",
  "Authors": "MultiSelect",
  "Bibtex": "String",
  "DOI": "String",
  "Year": "Timeline",
  
  # custom categories
  "CategoryOne": "MultiSelect",
  "CategoryTwo": "MultiSelect",
  "CategoryThree": "MultiSelect",
}

# properties that will be read from the csv, indexed to their supergroups
categories = {
  "PropertyC1One": "CategoryOne",
  "PropertyC1Two": "CategoryOne",
  
  "PropertyC2One": "CategoryTwo", 
  "PropertyC2Two": "CategoryTwo", 
          
  "PropertyC3One": "CategoryThree",
  "PropertyC4Two": "CategoryThree",
}

groups = { 
  "CategoryOne": "GroupOne",
  "CategoryTwo": "GroupOne",
  "CategoryThree": "GroupTwo"
}

def get_arguments():
    """ Get parsed CLI arguments """
    parser = argparse.ArgumentParser(description='Python script for converting csv to JSON for Indy.'
                                                 'Generates a config and data file.',
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-i', '--input-file', type=str, default="Survey-Info.csv",
                        dest="filename", help='The files that gets parsered.')
    parser.add_argument('-o','--only-data', action='store_true', default=False,
                        dest="onlydata", help='generate only the data file')
    parser.add_argument('-n','--name', type=str, 
                        default="Example Title",
                        dest="surveyname", help='sets the website title')
    parser.add_argument('-d','--desc', type=str, 
                        default="Example Description",
                        dest="surveydesc", help='sets the website description')
    parser.add_argument('-a','--authors', type=str, 
                        default="<anonymized for submission>",
                        dest="surveyauthors", help='sets the website authors')
    parser.add_argument('-g','--github', type=str, 
                        default="<anonymized for submission>",
                        dest="github", help='sets the website link to Github')

    return parser.parse_args()

class CustomFormatter(logging.Formatter):    
    yellow = '\x1b[38;5;226m'
    red = '\x1b[38;5;196m'
    reset = '\x1b[0m'

    def __init__(self, fmt):
        super().__init__()
        self.fmt = fmt
        self.FORMATS = {
            logging.WARNING: self.yellow + self.fmt + self.reset,
            logging.ERROR: self.red + self.fmt + self.reset
        }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)

def main():
  args = get_arguments()
  
  logger = logging.getLogger(__name__)
  
  stdout_handler = logging.StreamHandler()
  stdout_handler.setFormatter(CustomFormatter('%(levelname)8s | %(message)s'))
  logger.addHandler(stdout_handler)

  with open(args.filename, encoding='utf-8-sig') as csvfile:
    spamreader = csv.reader(csvfile)
    jsonfile = {"meta":[], "data":[]}
    configfile = {"filterBy":[], "filterBy":[], "detailView":{
        "view" : "normal",
        "show":[] #Add properties that you want to view on summary view
      }, 
      "summaryView": {
        "view": "text",
        "showImg": True,
        "show":[] #Add properties that you want to view on summary view
      },
      "topView":{
        "title":args.surveyname,
        "description":args.surveydesc,
        "authors":args.surveyauthors,
        "addEntry": {
          "description":[
            "If you know a peer-reviewed published work that presents a contribution missing in our browser, please submit an entry!", 
            "Filling out the form below will create a json entry that can be added to an issue in our Github repository."],
          "github":args.github
        }
      }
    }

    header = []
    uniques = set()

    # get header information
    for row in spamreader:
      for name in row:
        header.append(name)
        if name in includeProp:
          jsonfile["meta"].append({'name': name, "type":includeProp[name]})
          if (includeProp[name] == 'MultiSelect' or includeProp[name] == 'String') and name not in excludeProp :
            configfile["filterBy"].append(name)
          if name not in excludeProp:
            configfile["detailView"]["show"].append(name)
        elif name in categories: 
          catname = categories[name]
          nametype = includeProp[catname]
          
          if catname not in uniques: 
            uniques.add(catname)
            jsonfile["meta"].append({'name': catname, "type": nametype})
            if (nametype == 'MultiSelect' or nametype == 'String') and catname not in excludeProp :
              configfile["filterBy"].append(catname)
            if catname not in excludeProp:
              configfile["detailView"]["show"].append(catname)
      break

    propStructure = {}
    for prop in includeProp:
      propStructure[prop] = {"name":prop, "values":set()}

    # reads every paper 
    for row in spamreader:
      entry = {}
      for index, prop in enumerate(row):

        # read and collect values with "x" in them 
        if header[index] in categories:  
          catname = categories[header[index]]
          nametype = includeProp[catname]

          if catname not in entry: 
            entry[catname] = set()
          
          if (prop != ""):
            entry[catname].add(header[index])
                
          for doc in entry[catname]:
            propStructure[catname]['values'].add(doc)
        
        # read as lists of strings (comma separated)
        elif header[index] in includeProp:
            catname = header[index]

            # handle edge cases
            if (catname == "Edge Case"): 
              if (prop == "x"): 
                entry[catname] = ["Yes"]
              elif (prop == ""):       
                entry[catname] = ["No"]
            
            else: 
              if includeProp[catname] == "MultiSelect":
                entry[catname] = [x.strip() for x in prop.split(",")]
              else:
                entry[catname] = prop.strip()
              
            if includeProp[catname] == "MultiSelect":
              propList = entry[catname]
              for doc in propList:
                propStructure[catname]['values'].add(doc)

        
        
      for k in entry: 
        if isinstance(entry[k], set):
          entry[k] = list(entry[k])

      for k in includeProp: 
        if (not k in entry or (len(entry[k]) == 0)) and (not k in optionals):
          logger.warning(
            "Prop: \"" + k + "\" empty for: \"" + entry["Name"] + "\". " + 
            "Check for duplicate headings, or this may be an edge case."
          )
      jsonfile["data"].append(entry)
    
    dataObject = json.dumps(jsonfile, indent=4)
    
    # writing to survey-data.json
    with open("survey-data.json", "w") as outfile:
        outfile.write(dataObject)
    
    filterGroups = {}
    if args.onlydata == False:
      for i in range(len(configfile["filterBy"])):
        name = configfile["filterBy"][i]
        propStructure[name]['values'] = list(propStructure[name]['values'] )

        
        if not groups[name] in filterGroups: 
          filterGroups[groups[name]] = { "groupName": groups[name], "categories": [] }
        filterGroups[groups[name]]["categories"].append(propStructure[name])

      configfile["filterBy"] = [x for x in filterGroups.values()]

      with open("survey-config.json", "w") as outfile:
          configObject= json.dumps(configfile, indent=4)
          outfile.write(configObject)

if __name__ == '__main__':
  main()
import csv
import json
import argparse
import logging

# properties without a filter or view
excludeProp = ["Name", "Authors", "Year", "DOI", "Bibtex", "source"]

optionals = []


# properties that will be shown in the website
includeProp = {
  # fixed
  "Name":"String",
  "Authors": "MultiSelect",
  "Bibtex": "String",
  "DOI": "String",
  "Year": "Timeline",
  
  # custom categories
  "Use Case: Task/Task Type": "MultiSelect",
  "Use Case: Domain": "MultiSelect",
  "Study Task": "MultiSelect",
  # "Study Methodology / Evaluation": "MultiSelect",

  "device limitations": "MultiSelect",
  "scene acquisition & reconstruction": "MultiSelect",
  "user acquisition & modelling": "MultiSelect",
  "system complexity": "MultiSelect",
  "latency & real-time presentation": "MultiSelect",

  "spatial consistency": "MultiSelect",
  "shared & blended environment": "MultiSelect",
  "spatial awareness & orientation": "MultiSelect",

  "user representation & techniques": "MultiSelect",
  "communication & sensory feedback": "MultiSelect",
  "interpersonal awareness": "MultiSelect",
  "cognition & presence": "MultiSelect",
  "accessibility & inclusion": "MultiSelect",

  "asymmetric experiences": "MultiSelect",
  "interaction & UI design": "MultiSelect",
  "evaluation & studies": "MultiSelect",
  "domain & use case specific": "MultiSelect",
  "data privacy & security": "MultiSelect",
}

# properties that will be read from the csv, indexed to their supergroups
categories = {
  "Instruction & Guidance": "Use Case: Task/Task Type",
  "Assembly & Arrangement": "Use Case: Task/Task Type",
  "Problem Solving & Games": "Use Case: Task/Task Type",
  "Communication & Collaboration": "Use Case: Task/Task Type",

  "(Tele) Medicine": "Use Case: Domain",
  "Maintenance & Industry": "Use Case: Domain",
  "Design & Creativity": "Use Case: Domain",
  "Education & Knowledge Work": "Use Case: Domain",
  "Social & Play": "Use Case: Domain",
  "Various & Unspecified": "Use Case: Domain",

  "no study": "Study Task",
  "communication": "Study Task",
  "puzzle and assembly": "Study Task",
  "object arrangement and manipulation": "Study Task",
  "locating object in environment": "Study Task",
  "training, instruction, guiding": "Study Task",
  "information extraction and generation": "Study Task",
  "maintainance": "Study Task",
  "game": "Study Task",
  "walkthrough": "Study Task",

  # Technology
  "general - device limitations": "device limitations",
  "display": "device limitations",
  "ergonomics": "device limitations",
  "tracking": "device limitations",

  "general - scene acquisition & reconstruction": "scene acquisition & reconstruction",
  "point cloud Level of Detail": "scene acquisition & reconstruction",
  "point cloud stability": "scene acquisition & reconstruction",
  "point cloud completeness": "scene acquisition & reconstruction",
  "3D reconstruction": "scene acquisition & reconstruction",
  "scale of environment & tracking area": "scene acquisition & reconstruction",
  "general object recognition & alignment": "scene acquisition & reconstruction",

  "general - user acquisition & modelling": "user acquisition & modelling",
  "hand tracking": "user acquisition & modelling",
  "body tracking": "user acquisition & modelling",
  "face & gaze tracking": "user acquisition & modelling",

  "general - system complexity": "system complexity",
  "devices & sensors": "system complexity",
  "computational challenges": "system complexity",
  "heterogeneity & interoperability": "system complexity",
  "scalability": "system complexity",

  "general - latency & real-time presentation": "latency & real-time presentation",
  "synchronicity": "latency & real-time presentation",
  "network challenges": "latency & real-time presentation",
  "general latency": "latency & real-time presentation",
  "bandwidth issue": "latency & real-time presentation",
  "performance": "latency & real-time presentation",

  # Environment
  "general - spatial consistency": "spatial consistency",
  "calibration & alignment": "spatial consistency",

  "general - shared & blended environment": "shared & blended environment",
  "dissimilar spaces": "shared & blended environment",
  "virtual content positioning": "shared & blended environment",
  "shared objects": "shared & blended environment",
  "controlling real-world properties": "shared & blended environment",
  "physical & spatial limits": "shared & blended environment",

  "general - spatial awareness & orientation": "spatial awareness & orientation",
  "locating  objects & user": "spatial awareness & orientation",
  "communication about the environment": "spatial awareness & orientation",
  "dynamic changes": "spatial awareness & orientation",

  # User
  "general - user representation & techniques": "user representation & techniques",
  "level of detail & accuracy": "user representation & techniques",
  "avatar designs & uncanny valley": "user representation & techniques",

  "general - communication & sensory feedback": "communication & sensory feedback",
  "verbal": "communication & sensory feedback",
  "non-verbal": "communication & sensory feedback",
  "gestures": "communication & sensory feedback",
  "facial expressions & eyes": "communication & sensory feedback",
  "physical props & haptic feedback": "communication & sensory feedback",

  "general - interpersonal awareness": "interpersonal awareness",
  "gaze & view sharing": "interpersonal awareness",
  "content & intention sharing": "interpersonal awareness",

  "general - cognition & presence": "cognition & presence",
  "presence": "cognition & presence",
  "cognitive & mental load": "cognition & presence",
  "co- & social-presence": "cognition & presence",
  
  "accessibility & inclusion": "accessibility & inclusion",

  # Cross-Cutting
  "general - asymmetric experiences": "asymmetric experiences",
  "content & environment sharing": "asymmetric experiences",
  "user representation": "asymmetric experiences",
  "awareness on shared personal information": "asymmetric experiences",
  "interaction & general capabilities": "asymmetric experiences",

  "general - interaction & UI design": "interaction & UI design",
  "workflow": "interaction & UI design",
  "annotations": "interaction & UI design",
  "adaptive & customizable UI": "interaction & UI design",

  "evaluation & studies": "evaluation & studies",

  "domain & use case specific": "domain & use case specific",
  
  "data privacy & security": "data privacy & security",
}

groups = { 
  "Use Case: Task/Task Type": "Meta",
  "Use Case: Domain": "Meta",
  "Study Task": "Meta",
  # "Study Methodology / Evaluation": "Meta",

  "device limitations": "Technology",
  "scene acquisition & reconstruction": "Technology",
  "user acquisition & modelling": "Technology",
  "system complexity": "Technology",
  "latency & real-time presentation": "Technology",

  "spatial consistency": "Environment",
  "shared & blended environment": "Environment",
  "spatial awareness & orientation": "Environment",

  "user representation & techniques": "User",
  "communication & sensory feedback": "User",
  "interpersonal awareness": "User",
  "cognition & presence": "User",
  "accessibility & inclusion": "User",

  "asymmetric experiences": "Cross-Cutting",
  "interaction & UI design": "Cross-Cutting",
  "evaluation & studies": "Cross-Cutting",
  "domain & use case specific": "Cross-Cutting",
  "data privacy & security": "Cross-Cutting",
}

def get_arguments():
    """ Get parsed CLI arguments """
    parser = argparse.ArgumentParser(description='Python script for converting csv to JSON for Indy.'
                                                 'Generates a config and data file.',
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-i', '--input-file', type=str, default="Survey-Info.csv",
                        dest="filename", help='The files that gets parsed.')
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
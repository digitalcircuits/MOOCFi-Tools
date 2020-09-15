from MOOCFiRipper import MOOCFiRipper
import os
from dotenv import load_dotenv
load_dotenv()

#You can replace these with strings of your information
username = os.environ.get("MOOCFI_USER")
password = os.environ.get("MOOCFI_PASS")
user_agent = os.environ.get("MOOCFI_AGENT")

ObjT = MOOCFiRipper(username=username, password=password, user_agent=user_agent)

#Save a zip file
with open('Part01_33-Suggestion.zip', 'wb') as f:
    f.write(ObjT.download_suggestion(exer_id=83137))

#Get all assignments, regardless whether completed or not
print(ObjT.retAllAssn())

#Check to see if a specific assignment is completed
print(ObjT.retCompAssnById(exer_id=83137))
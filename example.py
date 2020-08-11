from MOOCFiRipper import MOOCFiRipper
import os
from dotenv import load_dotenv
load_dotenv()

#You can replace these with strings of your information
username = os.environ.get("MOOCFI_USER")
password = os.environ.get("MOOCFI_PASS")
user_agent = os.environ.get("MOOCFI_AGENT")


ObjT = MOOCFiRipper(username=username, password=password, user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:78.0) Gecko/20100101 Firefox/78.0")

#Download your successful submission
print(ObjT.download_your_success_submission(83213, os.getcwd()))

#Retrieve all assignments
print(ObjT.retAllAssn())

#Retrieve all assignments and save them in a path
print(ObjT.retAllAssn(save=True, Path=os.getcwd()))

#Download the suggested answer to your assignment
print(ObjT.download_suggestion(exer_id=83213, Path=os.getcwd()))
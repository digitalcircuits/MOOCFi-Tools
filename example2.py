from MOOCFiRipper import MOOCFiRipper
import os, time
from dotenv import load_dotenv
load_dotenv()

#You can replace these with strings of your information
username = os.environ.get("MOOCFI_USER")
password = os.environ.get("MOOCFI_PASS")
user_agent = os.environ.get("MOOCFI_AGENT")

#This example downloads all assignment suggestioned answers for all completed assignments

ObjT = MOOCFiRipper(username=username, password=password, user_agent=user_agent)

if ObjT.checkLogin()['status'] == 0:
    raise Exception("Error logging in")

#Get all completed assignments
completed_assignments = ObjT.retCompAssn()['completed_assignments']

#Create a directory which we will store our assignments
if not os.path.exists(os.path.join(os.getcwd(), 'completed_suggestion')):
    os.makedirs(os.path.join(os.getcwd(), 'completed_suggestion'))

#Loop through all completed assignments and download them all
for assignment in completed_assignments:
    print(f"Downloading assignment suggestion: {assignment}")
    with open(os.path.join(os.getcwd(), 'completed_suggestion', f'{assignment}_suggestion.zip'), 'wb') as f:
        #Access the byte object (since download_suggestion() returns a dictionary with the bytes)
        result = ObjT.download_suggestion(exer_id=assignment)
        if result['status'] == 0:
            raise Exception(f"Error downloading file {assignment}")

        #Save the bytes read
        f.write(result['object'].read())
        
    time.sleep(5) #Sleep for 5 seconds so we dont send too many requests to the server in a short period of time

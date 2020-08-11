import requests, json, os, time
from bs4 import BeautifulSoup
import html5lib
import re

#Show all exercises: https://tmc.mooc.fi/api/v8/org/mooc/courses/java-programming-i/exercises/

class MOOCFiRipper():

    def __init__(self, username, password, user_agent):
        self.username = username
        self.password = password
        self.user_agent = user_agent
        self.goodLog = False

        #Login to MOOC fi
        self.s = requests.Session()
        infoReq = self.s.get("https://tmc.mooc.fi/login", headers={'User-Agent': self.user_agent}, timeout=5)
        getUTFCheck = BeautifulSoup(infoReq.text, 'html.parser').find("form").find('input', {'name':'utf8'})['value']
        getPageAuthToken = BeautifulSoup(infoReq.text, 'html.parser').find("form").find('input', {'name':'authenticity_token'})['value']
        getSessionCookie = infoReq.headers['Set-Cookie'].split(";")[0]

        loginCookie = self.s.post("https://tmc.mooc.fi/sessions", allow_redirects=True,
        headers={'Cookie': getSessionCookie, 'User-Agent': self.user_agent, "location": "https://tmc.mooc.fi/login"},
        data={"session[login]": self.username, "session[password]": self.password, "commit": "Sign+in", "utf8": getUTFCheck, "authenticity_token": getPageAuthToken},timeout=5
        )

        checkAuthy = self.s.get("https://tmc.mooc.fi/api/v8/org/mooc/courses/java-programming-i/exercises/", headers={'User-Agent': self.user_agent}, timeout=5).json()
        if "errors" in checkAuthy:
            #We failed to log in
            self.goodLog = False
        else:
            #Login was successful
            self.goodLog = True
    
    def retAllAssn(self, save=False, Path=None):
        if self.goodLog:
            all_assn = {}
            #Retrieves a list of avaliable assignments, whether completed or not
            p1 = self.s.get("https://tmc.mooc.fi/api/v8/org/mooc/courses/java-programming-i/exercises/", headers={'User-Agent': self.user_agent}, timeout=5).json()
            p2 = self.s.get("https://tmc.mooc.fi/api/v8/org/mooc/courses/java-programming-ii/exercises/", headers={'User-Agent': self.user_agent}, timeout=5).json()
            
            #Add all the assignments to a dictionary as {id: assignment_name}
            for key in p1:
                all_assn[key["id"]] = key["name"]
            for key in p2:
                all_assn[key["id"]] = key["name"]

            #If the user wants, save it to a file
            if save:
                if not Path:
                    return {"status": 0, "msg": "Save Path Not Set (Did you mean to set 'save' to false?)"}
                try:
                    with open(os.path.join(Path, "avaliable_assignments.json"), 'wb') as f:
                        f.write(json.dumps(all_assn))
                    return {"status": 1, "msg": "Assignments saved to to {}".format(os.path.join(Path, "avaliable_assignments.json")), "all_assn": all_assn}
                except Exception as e:
                    return {"status": 0, "msg": f"Error While Downloading Template: {e}"}
            return {"status": 1, "all_assignments": all_assn}
        else:
            return {"status": 0, "msg": "Failed to Login to MOOCfi"}

    def retCompAssn(self, Path=None, defaultans=False):
        #Retrieves a list of completed assignments
        if self.goodLog:
            print("Checking on completed assignments! This will take awhile....")
            all_assn = self.retAllAssn()['all_assignments']
            comp_assn = {}
            for key in all_assn:
                print(f"Checking On {key} : {all_assn[key]}")
                time.sleep(2) #Dont spam the server with requests that quick
                r = self.s.get(f"https://tmc.mooc.fi/api/v8/org/mooc/courses/java-programming-i/exercises/{all_assn[key]}", timeout=5).json()
                if r['completed'] == True:
                    comp_assn[key] = all_assn[key]
            if Path:
                if os.path.exists(os.path.join(Path, 'completed_assignments.json')) and defaultans == False:
                    print("The 'completed_assignments.json' file already exist, are you sure you want to overwrite?")
                    ans = input("'y' for Yes, anything else for No -> ")
                    if ans.lower() == "y":
                        with open(os.path.join(Path, 'completed_assignments.json'), 'w') as f:
                            f.write(json.dumps(comp_assn))
                            return {"status": 1, "completed_assignments": comp_assn, 'path': Path}
                    else:
                        return {"status": 0, "msg": "File Overwrite Rejected"}
                else:
                    print(comp_assn)
                    with open(os.path.join(Path, 'completed_assignments.json'), 'w') as f:
                        f.write(json.dumps(comp_assn))
                        return {"status": 1, "completed_assignments": comp_assn, 'path': Path}
            return {"status": 1, "completed_assignments": comp_assn}
        else:
            return {"status": 0, "msg": "Failed to Login to MOOCfi"}

    def download_suggestion(self, exer_id, Path):
        exer_id = int(exer_id)
        #Downloads suggested solution, can only be used if assignment is completed
        if self.goodLog:
            if not Path:
                return {"status": 0, "msg": "Path has not been set"}

            #If the assignment is not completed, throw an error since MOOC fi wont allow us to see the suggested solution
            all_assn = self.retAllAssn()['all_assignments']
            r = self.s.get(f"https://tmc.mooc.fi/api/v8/org/mooc/courses/java-programming-i/exercises/{all_assn[exer_id]}", timeout=5).json()
            if r['completed'] == False:
                return {"status": 0, "msg": "Assignment not completed, cannot download suggestion"}
            
            #Otherwise, continue along...
            r = self.s.get(f"https://tmc.mooc.fi/exercises/{exer_id}/solution", timeout=5).text
            individual_ans = BeautifulSoup(r, 'html5lib').find("div", {"class": "solution-files"}).find_all("div", {"class": "card"})
            for ans in individual_ans:
                codepath = ans.find("a", {"class": "panel-group-toggle"}).text.strip().split("/") #File path and name
                codeans = ans.find("code", {"class": "brush"}).text #The answer
                #Create the file and write the answer
                if os.path.exists(os.path.join(Path, f'{exer_id}_template', *codepath[:-1])) == False:
                    os.makedirs(os.path.join(Path, f'{exer_id}_template', *codepath[:-1]))
                with open(os.path.join(Path, f'{exer_id}_template', *codepath), 'wb') as f:
                    f.write(codeans.encode(encoding='UTF-8'))
            return {"status": 1, "msg": "Downloaded Exercise {} suggestion to {}".format(exer_id, Path)}
        else:
            return {"status": 0, "msg": "Failed to Login to MOOCfi"}

    def download_template(self, exer_id, Path):
        exer_id = int(exer_id)
        #Downloads the template from MOOC fi
        if self.goodLog:
            if not Path:
                return {"status": 0, "msg": "Path has not been set"}
            r = self.s.get(f"https://tmc.mooc.fi/exercises/{exer_id}.zip", allow_redirects=True, timeout=5)
            try:
                with open(os.path.join(Path, f"{exer_id}_template.zip"), 'wb') as f:
                    f.write(r.content)
                return {"status": 1, "msg": "Downloaded Template {} to {}".format(exer_id, os.path.join(Path, f"{exer_id}.zip"))}
            except Exception as e:
                return {"status": 0, "msg": f"Error While Saving Template: {e}"}
        else:
            return {"status": 0, "msg": "Failed to Login to MOOCfi"}

    def download_your_success_submission(self, exer_id, Path):
        exer_id = int(exer_id)
        #Downloads your submitted successful solution (if you have one)
        if self.goodLog:
            if not Path:
                return {"status": 0, "msg": "Path has not been set"}
            all_assn = self.retAllAssn()['all_assignments']
            if self.s.get(f"https://tmc.mooc.fi/api/v8/org/mooc/courses/java-programming-i/exercises/{all_assn[exer_id]}", timeout=5).json()["completed"] == True:
                r = self.s.get("https://tmc.mooc.fi/exercises/83265", allow_redirects=True, timeout=5).text
                res = BeautifulSoup(r, 'html5lib').find("table", {'id': "submissions"}).find("tbody").find_all("tr")
                for submission in res:
                    if submission.find('span', {'class': 'ok'}):
                        #Extract the download number
                        resultr = submission.find_all("a")[1].get('href')
                        temp = re.findall(r'\d+', resultr) 
                        download_num = list(map(int, temp))[0]
                        break
                r = self.s.get(f"https://tmc.mooc.fi/submissions/{download_num}/full_zip", allow_redirects=True, timeout=5)
                with open(os.path.join(Path, f'{download_num}-submission.zip'), 'wb') as z:
                    z.write(r.content)
                return {'status': 1, 'msg': f"{download_num} Submission has been downloaded to {os.path.join(Path, f'{download_num}-submission.zip')}"}
            else:
                return {"status": 0, "msg": "Assignment not completed - Complete your assignment to download your solution"}
        else:
            return {"status": 0, "msg": "Failed to Login to MOOCfi"}   
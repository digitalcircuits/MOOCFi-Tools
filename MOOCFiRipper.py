import requests, json, os, time, io, zipfile
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

        #Extract some variables the course expects from the Login page
        infoReq = self.s.get("https://tmc.mooc.fi/login", headers={'User-Agent': self.user_agent}, timeout=5)
        getUTFCheck = BeautifulSoup(infoReq.text, 'html.parser').find("form").find('input', {'name':'utf8'})['value']
        getPageAuthToken = BeautifulSoup(infoReq.text, 'html.parser').find("form").find('input', {'name':'authenticity_token'})['value']
        getSessionCookie = infoReq.headers['Set-Cookie'].split(";")[0]

        #Create the cookies for the session
        loginCookie = self.s.post("https://tmc.mooc.fi/sessions", allow_redirects=True,
        headers={'Cookie': getSessionCookie, 'User-Agent': self.user_agent, "location": "https://tmc.mooc.fi/login"},
        data={"session[login]": self.username, "session[password]": self.password, "commit": "Sign+in", "utf8": getUTFCheck, "authenticity_token": getPageAuthToken},timeout=5
        )
        
        try:
            #Check to see if we actually logged in
            checkAuthy = self.s.get("https://tmc.mooc.fi/api/v8/org/mooc/courses/java-programming-i/exercises/", headers={'User-Agent': self.user_agent}, timeout=5).json()
            if "errors" in checkAuthy:
                #We failed to Log In
                self.goodLog = False
            else:
                #Login was successful
                self.goodLog = True
        except Exception as e:
            self.goodLog = False
    
    def _ValidCourse(self, exer_id):
        #Check to see if the exercise id is valid. We only want exercise ID's from the Java Programming 2020 course
        return ((83113 <= exer_id <= 83283) or exer_id == 85612 or (87694 <= exer_id <= 87783))

    def checkLogin(self):
        if not self.goodLog:
            return {'status': 0, 'msg': 'Login Failed', 'username': self.username, 'user_agent': self.user_agent}
        elif self.goodLog:
            return {'status': 1, 'msg' : 'Login Successful', 'username': self.username, 'user_agent': self.user_agent}
    
    def retAllAssn(self):
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
            return {"status": 1, "all_assignments": all_assn}
        else:
            return {"status": 0, "msg": "Failed to Login to MOOCfi"}

    def retCompAssnById(self, exer_id):
        #Check a specific exercise ID to see if its completed
        exer_id = int(exer_id)
        if self.goodLog:
            if self._ValidCourse(exer_id) == False:
                return {"status": 0, "msg": "Invalid Exercise ID"}
            r = self.s.get(f"https://tmc.mooc.fi/api/v8/org/mooc/courses/java-programming-i/exercises/{self.retAllAssn()['all_assignments'][exer_id]}", timeout=5).json()
            if r['completed'] == True:
                return {"status": 1, "completed": 1}
            else:
                return {"status": 1, "completed": 0}
        else:
            return {"status": 0, "msg": "Failed to Login to MOOCfi"}

    def retCompAssn(self):
        #Retrieves a list of completed assignments - This will take awhile....
        if self.goodLog:
            print("retCompAssn - Checking on completed assignments! This will take awhile....")
            all_assn = self.retAllAssn()['all_assignments']
            comp_assn = {}
            for key in all_assn:
                #print(f"Checking On {key} : {all_assn[key]}")
                r = self.s.get(f"https://tmc.mooc.fi/api/v8/org/mooc/courses/java-programming-i/exercises/{all_assn[key]}", timeout=5).json()
                if r['completed'] == True:
                    comp_assn[key] = all_assn[key]
            return {"status": 1, "completed_assignments": comp_assn}
        else:
            return {"status": 0, "msg": "Failed to Login to MOOCfi"}

    def download_suggestion(self, exer_id):
        exer_id = int(exer_id)
        #Downloads suggested solution, can only be used if assignment is completed
        if self.goodLog:
            if self._ValidCourse(exer_id) == False:
                return {"status": 0, "msg": "Invalid Exercise ID"}

            all_assn = self.retAllAssn()['all_assignments']
            r = self.s.get(f"https://tmc.mooc.fi/api/v8/org/mooc/courses/java-programming-i/exercises/{all_assn[exer_id]}", timeout=5).json()
            #If the assignment is not completed, throw an error since MOOC fi wont allow us to see the suggested solution
            if r['completed'] == False:
                return {"status": 0, "msg": "Assignment not completed, cannot download suggestion"}
            
            #Otherwise, continue along...
            r = self.s.get(f"https://tmc.mooc.fi/exercises/{exer_id}/solution", timeout=5).text
            individual_ans = BeautifulSoup(r, 'html5lib').find("div", {"class": "solution-files"}).find_all("div", {"class": "card"})
            
            zip_buffer = io.BytesIO() 
            zip_file = zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False)
            for ans in individual_ans:
                codepath = ans.find("a", {"class": "panel-group-toggle"}).text.strip().split("/") #File path and name
                codeans = ans.find("code", {"class": "brush"}).text #The answer

                zip_file.writestr(os.path.join(*codepath), codeans.encode(encoding='UTF-8'))
                zip_file.close()
            zip_buffer.seek(0)
            return {"status": 1, "object": zip_buffer}    
        else:
            return {"status": 0, "msg": "Failed to Login to MOOCfi"}

    def download_template(self, exer_id):
        exer_id = int(exer_id)
        #Downloads the exercise template from MOOC Fi
        storeFile = io.BytesIO
        if self.goodLog:
            if self._ValidCourse(exer_id) == False:
                return {"status": 0, "msg": "Invalid Exercise ID"}
            r = self.s.get(f"https://tmc.mooc.fi/exercises/{exer_id}.zip", allow_redirects=True, timeout=5, stream=True)
            storeFile = io.BytesIO(r.content)
            return {'status': 1, 'object': storeFile}
        else:
            return {"status": 0, "msg": "Failed to Login to MOOCfi"}

    def download_your_success_submission(self, exer_id):
        exer_id = int(exer_id)
        #Downloads your submitted successful solution (if the user has submitted one)
        if self.goodLog:
            if self._ValidCourse(exer_id) == False:
                return {"status": 0, "msg": "Invalid Exercise ID"}
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
                r = self.s.get(f"https://tmc.mooc.fi/submissions/{download_num}/full_zip", allow_redirects=True, timeout=5, stream=True)
                storeFile = io.BytesIO(r.content)
                return {'status': 1, 'object': storeFile}
            else:
                return {"status": 0, "msg": "Assignment not completed - Complete your assignment to download your solution"}
        else:
            return {"status": 0, "msg": "Failed to Login to MOOCfi"}   

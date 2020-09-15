![](https://i.imgur.com/zflkJAs.png)

# About

## About MOOC.fi Java Programming Course

MOOC.fi Java Programming is an Object Oriented (OOP) Java Programming course offered for free by the University of Helsinki. It is aimed at anyone who wishes to learn programming, specifically using the Java programming language. Even if you are an experienced programmer, the course is worth taking if your Java skills are rusty and the course does a good job explaining how OOP works. The course is free and anyone can sign up for it, regardless where you are located or even if you are a student at the university.

During the Spring of 2020, the University of Helsinki launched their 2020 version of Java Programming, an updated iteration from their previously popular 2013 version.

You can find the course at: https://java-programming.mooc.fi/

## About this Github Repo

The MOOC.fi Java Programming course is a great course for anyone who is first learning how to program or even learning how to program in Java. However, there are issues I immediately noticed:

* **Answers do not get downloaded between PCs** - If you were to install TMCBeans on another PC and tried to download your completed answers, you would only get the templates, not your actual answers

* **Cannot download suggested answers** - You are given a link to view the suggested answers but you cannot download them to a zip file

* **No easy way to export "completed" answers** - You cannot easily "export" a JSON list of your completed and uncompleted assignments

* **Cannot download your answers unless logging into your portal** - The MOOC.fi course is known for the java-programming where you view your assignments but many may not there is a seperate portal where you must login, find your assignment, scroll through all your failed submissions, click on your successful submission, then you can download

* **Cannot easily get a copy of the template** - If you mess up and want to start over again, you would need to close the assignment, then go to Options where you can download another copy of all uncompleted assignments, just to get a fresh start

## No API? Let's create our own!

As of August 2020, there is no easy API that we can use to fetch our completed projects or suggested templates. However, there is a hidden JSON api that the TMC plugin uses and an old frontend system. Using BeautifulSoup4, a popular HTML parser, we can scrape the MOOC.fi website for what we need, allowing us to make functions easily.

## Requirements

Ensure you have Python 3 installed. If you are on Windows and you installed Python from https://www.python.org/, you can check by opening up the CommandLine:
```
> python -V
Python 3.7.7
```

If you are on Mac or Linux, you may need to type Python3 instead
```
> python3 -V
Python 3.7.7
```

Once you ensured you have Python 3 installed, install all the dependancies:
```
python -m pip --no-cache-dir install -r requirements.txt
```


## How To Use

There are two ways to use the API. The server method (good if you do not know Python) and the library method.

### Server method
Since many students are learning Java, they may not have good Python experience. Therefore, there is a server.py script that, when ran, spins up a server you can use.

After installing the requirements, you can type:
```
python server.py
```
*Notice:* You can change the port in the script or in the .env file (once your renamed '.env-example' to '.env')

Then, go to the URL it specifies. Here are some screenshots:

![Login Page](https://i.imgur.com/nw70VmS.png)
![Panel](https://i.imgur.com/jLK8bal.png)
![Download](https://i.imgur.com/ON9Ga82.png)

### Library method

If you wish to perform a large amount of operations & are familiar with the Python programming language, you can import the MOOCFi Ripper to your script run whatever you wish. This is an example of how to run use it:

```
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
```

You can find this in the "example.py" file in this repository.

### I just want to see the answers for the MOOC.fi Java Programming course, do you have them online?

Sure! Check out https://github.com/moocfianswers/mooc.fi-java-programming-2020

*(You can read through the README of that repo to understand the files inside the folders)*

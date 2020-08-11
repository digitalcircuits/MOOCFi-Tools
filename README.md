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

As of August 2020, there is no easy API that we can use to fetch our completed projects or suggested templates. However, there is a frontend online interface we can scrape. Using BeautifulSoup4, a popular HTML parser, we can scrape the MOOC.fi website for what we need, allowing us to make functions easily.

## How To Use

First, you create a new MOOCFiRipper object, containing your username, password, and [user-agent](https://www.google.com/search?&q=what+is+my+user+agent). Then run a command and see if its successful

*Example If Login Failed:*
```
> a = MOOCFiRipper(username="john@smith.com", password="12345", user-agent="Chrome")
> print(a)

return {"status": 0, "msg": "Failed to Login to MOOCfi"}
```

*Example if Login Successful*:
```
> a = MOOCFiRipper(username="john@smith.com", password="12345", user-agent="Chrome")
> print(a.retAllAssn())

(output here)

```

Some functions require you to set "save" as True, indicating you wish to save your results to a file (assuming you also set a Path). Others require a Path to save those resuklts. You can check the MOOCFiRipper.py for all the commands and example.py for an example of how it was ran

### I just want to see the answers for the MOOC.fi Java Programming course, do you have them online?

Sure! Check out https://github.com/moocfianswers/mooc.fi-java-programming-2020

*(You can read through the README of that repo to understand the files inside the folders)*

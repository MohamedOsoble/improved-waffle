# The Daily Tracker
#### Video Demo:  https://youtu.be/WTaESL4z0vE
#### Description: A Daily Diary that keeps track of daily tasks and activities that a user may want to track or complete, the video has given examples of tasks to track such as time woken up or bed times, exercise and meals. These are just examples used but the limits of its use are entirely dependent on the user. For example, the daily diary can be used to track known triggers in patients with migraine to get a better understanding of what causes migraines in individuals and disease management. 

## app.py
#### app.py is the main python application that runs the entire application. It uses the CS50 Library to import the SQL function to link to the database and allow users to register, login and have an individualised experience when using the application. Flask and flask sessions are also imported to run the flask application. Wraps from functools has also been imported to write the login_required function that only allows users to display certain pages/routes of the application if they are indeed logged in. The date function has been imported from datetime to obtain the current date for use in the daily diary. I have also used the apology function that was in PSET9's problem set to help with the login/registration errors that may occur when a user tries to log in or register. 

### The default '/' route 
#### This route only renders a template as the majority of the application functions happen on other pages. 

### The register route
#### This function is straight forward, it accepts both GET and POST, it error checks for usernames, emails and passwords. Also compares the confirmation password field with the first password field to ensure they match. Once the error checking is complete, it generates a hashed password using the generate_password_hash function from werkzeug.security import. These are all then inserted into the users table of the database which then allows the user to log in. 

### The login route & logout route
#### allows the user to log in and then redirects them to the index page. The log out route simply clears the session and logs the user out and redirects them back to the index page. 

### The Diary Route
#### This is the applications main route where the bulk of the application is focused on. This route initializes the userId into a variable called userId for simplicities sake and then checks the request method. For the GET method, the logs are obtained into logSQL from the first query which is then turned into a dictionary of key:values which can be rendered properly by the template, I had issues getting this function to work using the logSQL variable and managed to get it working by making my own dictionary in the python application which is then passed into the template. The POST route obtains the information from the form the user submitted and then enter it into the log table of the database. The route will then call upon itself again to update the template with the new information that is stored in the log table.

### Add Task Route
#### This route is similar to the diary route where it checks if the method is post, retrieves the submitted information and then enters it into the usertasks table and daily table. If a task with the same name already exists in this table, it does not add the task again and adds this task to the daily table specifically for the user. 

### Export Route
#### This route exports the users logs by writing all the entries in the log table for the user to a CSV file and returns the file location to allow the user to download the file. 

### The activity route
#### This route doesthe same as the add task route except it is for the activities rather than daily tasks.

### Update/Edit Diary  routes
#### Occasionally a user may forget to complete all the entries to their diary or cannot update their diary until another day and would like to log their tasks for days previous. These two routes allow the user to go back in time and retrieve logs and complete them so they have a complete set of data for previous days. The user is required to select a date they wish to update and the route retrieves the logs completed for that day and renders the incompleted tasks as forms for the user to submit and update into the logs. 

## database.db
#### It is an SQL database with 5 tables: users, usertasks, daily, log and activities. Each of these tables is used to track an indivual thing which is specified by the name. The users table keeps the record of the users login information, name, userid and email. the usertasks table keeps track of the all the daily tasks a user has subscribed to, the daily table keeps track of all the daily tasks between all the users. The activities table keeps track of each activity for each user and finally the log table keeps track of every entry made by all the users like a transactions table. 

## static folder
#### in the static folder we have the images and the styles.css file for which we use some on the index page. These images have been used to show the user before they register what functions are available on the application

## templates folder
#### in the templates folder we have all the webpages that are available on the website, starting with index.html we have a fairly basic homepage with a brief description of what the website does. The template uses an if else statement to show two seperate functionalities based on whether the user is logged in or not. This is done so one page can be used as the homepage for both logged in and logged out users but display different information/buttons based on which status. The layout.html file is the main template file for which all the other pages are based off. It uses bootstrap 5.1.3 for the template, nav bar and page layout. It also uses an if else condition which displays one of two navigation bars based on the users session status. The log page calls the /export route for the export function which allows the user to download their individual csv file whose name is generated by combining their username with a random number generated by the randint function. Initially I tried to use the datetime function however this proved rather difficult to get the file naming to be in an acceptable format and therefore settled with a random number as the functionality was more important than the correctness of the function. 

## flask_session folder
#### this folder records the sessions for the flask applicatoin as the session type for this application was filesystem. This is because to code for the application i used visual studio code on my home computer and it was just a practice project rather than a project that is being deployed on the web and therefore this seemed like the most suitable approach at the beginning of my project. 
# Database-Project
Using MySql,Python,Flas, HTML and CSS to simulate a simple photo sharing website

# Introduction
Instagram Website, a web application for sharing photos. It gives users more privacy than many photo sharing sites by giving them more detailed control over who can see which photos they post. The focus of the project will be on storing data about who posted which photos and who has permission to view them, tag others in them, see who’s tagged in what, etc.

# Features
**Login:** The user enters her username and password. Finstagram will add “salt” to the password, hash it, and check whether the hash of the password matches the stored password for that e-mail. If so, it initiates a session, storing the username and any other relevant data in session variables, then goes to the home page (or provides some mechanism for the user to select her next action.) If the password does not match the stored password for that username (or no such user exists) Finstagram informs the user that the the login failed and does not initiate the session.

**View visible photos and info about them:** Finstagram shows the user the photoID, photoOwner’s name, and caption of photos that are visible to the her, arranged in reverse chronological order. Display the photo or include a link to display it. Along with each photo the following further information should be displayed or there should be an option to display it: timestamp, the first names and last names of people who have been tagged in the photo (taggees), provided that they have accepted the tags (Tag.acceptedTag == true)

**Post a photo:** User enters the relevant data and a link to a real photo and a designation of whether the photo is visible to all followers (allFollowers == true) or only to members of designated CloseFriendGroups (allFollowers == false). Finstagram inserts data about the photo (including current time, and current user as owner) into the Photo table. If the photo is not visible to all followers, Finstagram gives the user a way to designate CloseFriendGroups that the user belongs to with which the Photo is shared.

**Manage Follows:** a. User enters the username of someone they want to follow. Finstagram adds an appropriate tuple to Follow, with acceptedFollow == False. b. User sees list of requests others has made to follow them and has opportunity to accept, by setting acceptFollow to True or to decline by removing the request from the Follow table.

**Manage tag requests:** Finstagram shows the user relevant data about photos that have proposed tags of this user (i.e. user is the taggee and acceptedTag is false.) User can choose to accept a tag (change acceptedTag to true), decline a tag (remove the tag from Tag table), or not make a decision (leave the proposed tag in the table with acceptedTag == false.)

**Tag a photo:** Current user, whom we’ll call x, selects a photo that is visible to her and proposes to tag it with username y i. If the user is self-tagging (y == x), Finstagram adds a row to the Tag table: (x, photoID, true) ii. else if the photo is visible to y, Finstagram adds a row to the Tag table: (y, photoID, false) iii. else if photo is not visible to y, Finstagram doesn’t change the tag table and prints some message saying that she cannot propose this tag.

**Add friend:** User selects an existing CloseFriendGroup that they own and provides username of someone she’d like to add to the group. Finstagram checks whether there is exactly one person with that name and updates the Belong table to indicate that the selected person is now in the CloseFriendGroup.

**Like and Comment on Photos:** Users can like and leave comments on individual's posts who they follow

## Prerequisite

* Python
* Flask

### Install Flask

* pip install flask
* pip install pymysql (used to connect to database)


### If You Don't Have pip

* https://pypi.python.org/pypi/pip
Run: python get-pip.py


### More Information

http://flask.pocoo.org/


### run on localhost:5000

# Instructions to run:
```
python3 finstagram_master.py

Notes: 
1) Be sure that the port used by your MySQL server is the same as the one configured in finstagram_master.py
```

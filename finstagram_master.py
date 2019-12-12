from flask import Flask, render_template, request, session, url_for, redirect, flash
import pymysql.cursors
import os
import uuid
import hashlib
import time
from functools import wraps

app = Flask(__name__)
app.secret_key = "super secret key"
IMAGES_DIR = os.path.join(os.getcwd(), "static")
SALT = '12345'


conn = pymysql.connect(host='localhost',
                       port = 3306,
                       user='root',
                       password='',
                       db='finstagram',
                       charset='utf8mb4',
                       cursorclass=pymysql.cursors.DictCursor,
                       autocommit =True)

def login_required(f):
    @wraps(f)
    def dec(*args, **kwargs):
        if not "username" in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return dec

#index
@app.route('/')
def start():
    return render_template('index.html')

#login
@app.route('/login')
def login():
    return render_template('login.html')

#register
@app.route('/register')
def register():
    return render_template('register.html')

#login authentication
@app.route('/loginAuth', methods=['GET', 'POST'])
def loginAuth():
    if request.form:
        requestData = request.form
        username = requestData["username"]
        password = requestData["password"] + SALT
        hashed_password = hashlib.sha256(password.encode("utf-8")).hexdigest()
                    
        cursor = conn.cursor()
        query = 'SELECT * FROM person WHERE username = %s and password = %s'
        cursor.execute(query, (username, hashed_password))
        data = cursor.fetchone()
        cursor.close()
        error = None
        if(data):
            session['username'] = username
            return redirect(url_for('home'))
        else:
            error = 'Incorrect username or password'
            return render_template('login.html', error=error)

#register authentication
@app.route('/registerAuth', methods=['GET', 'POST'])
def registerAuth():
    username = request.form['username']
    password = request.form['password'] + SALT
    hashed_password = hashlib.sha256(password.encode('utf-8')).hexdigest()
    firstname = request.form['firstName']
    lastname = request.form['lastName']
    biography = request.form['biography']
    cursor = conn.cursor()
    query = 'SELECT * FROM person WHERE username = %s'
    cursor.execute(query, (username))
    data = cursor.fetchone()
    error = None
    if(data):
        error = 'This user already exists'
        return render_template('register.html', error = error)
    else:
        ins = 'INSERT INTO person VALUES(%s, %s, %s, %s, %s)'
        cursor.execute(ins, (username, hashed_password, firstname, lastname, biography))
        cursor.close()
        return render_template('index.html')

#home with only personal posts
@app.route('/home')
@login_required
def home():
    user = session['username']
    cursor = conn.cursor();
    query = '''SELECT ID, firstName, lastName, photoOwner, postingDate, caption, filePath
    FROM photo JOIN person ON (photoOwner = username)
    WHERE photoOwner = %s
    ORDER BY postingDate DESC'''
    cursor.execute(query, (user))
    data = cursor.fetchall()
    query2= 'SELECT * FROM tagged NATURAL JOIN person WHERE tagStatus =1'
    cursor.execute(query2)
    data2 = cursor.fetchall()
    query3='SELECT * FROM liked'
    cursor.execute(query3)
    data3 = cursor.fetchall()
    cursor.close()
    return render_template('home.html', username=user, posts=data, tagposts = data2,likepost = data3)

#view posts that are posted by person who the user follows &
#shared posts from the person who is a member of a group which logged-in user also is 
@app.route('/view')
@login_required
def view():
    user = session['username']
    cursor = conn.cursor();
    query = '''SELECT ID, photoOwner, postingDate, caption, filePath, firstName, lastName
    FROM photo JOIN follow ON (photoOwner = followingUsername) 
    JOIN person ON (followingUsername = username)
    WHERE followerUsername = %s AND allFollowers = 1 AND followStatus = 1
    UNION
    SELECT p.ID, p.photoOwner, p.postingDate, p.caption, p.filePath, r.firstName, r.lastName
    FROM belongto AS b JOIN sharewith AS s ON (s.groupName = b.groupName AND s.groupOwner = b.groupOwner)
    JOIN photo AS p ON (p.ID = s.ID) JOIN person AS r ON (p.photoOwner = r.username)
    WHERE b.username = %s AND b.username != p.photoOwner
    ORDER BY postingDate DESC'''
    cursor.execute(query, (user,user))
    data = cursor.fetchall()
    query2= 'SELECT * FROM tagged NATURAL JOIN person WHERE tagStatus =1'
    cursor.execute(query2)
    data2 = cursor.fetchall()
    query3='SELECT * FROM liked'
    cursor.execute(query3)
    data3 = cursor.fetchall()
    cursor.close()
    return render_template('view.html', username=user, posts=data, tagposts =data2, likepost =data3)

#see which groups the user is in
@app.route('/group')
@login_required
def group():
    user = session['username']
    cursor = conn.cursor();
    query = 'SELECT groupName, groupOwner FROM belongto WHERE username =%s'
    cursor.execute(query, (user))
    data = cursor.fetchall()
    cursor.close()
    return render_template('group.html', username= user, group_list=data)

#see who are registered in finstagram
@app.route('/select_blogger')
@login_required
def select_blogger():
    user = session['username']
    cursor = conn.cursor();
    query = 'SELECT username, firstName, lastName FROM person WHERE username != %s'
    cursor.execute(query, (user))
    data = cursor.fetchall()
    cursor.close()
    return render_template('select_blogger.html', user_list=data)

#see posts of specific user
@app.route('/show_posts')
@login_required
def show_posts():
    user = request.args['photoOwner']
    cursor = conn.cursor();
    query = '''SELECT filePath, ID, firstName, lastName, photoOwner, postingDate, caption
    FROM photo JOIN person ON (photoOwner = username)
    WHERE photoOwner = %s
    ORDER BY postingDate DESC'''
    cursor.execute(query, (user))
    data = cursor.fetchall()
    query2= 'SELECT * FROM tagged NATURAL JOIN person WHERE tagStatus =1'
    cursor.execute(query2)
    data2 = cursor.fetchall()
    query3='SELECT * FROM liked'
    cursor.execute(query3)
    data3 = cursor.fetchall()
    cursor.close()
    return render_template('show_posts.html', username=user, posts=data, tags=data2, likepost =data3)


#see who the user follows, followed, and request pending
@app.route('/following') 
@login_required
def following():
    user = session['username']
    cursor = conn.cursor();
    query = 'SELECT followingUsername FROM follow WHERE followerUsername =%s AND followStatus =1'
    cursor.execute(query, (user))
    data = cursor.fetchall()
    query2 = 'SELECT followingUsername FROM follow WHERE followerUsername =%s AND followStatus =0'
    cursor.execute(query2, (user))
    data2 = cursor.fetchall()
    query3 = 'SELECT followerUsername FROM follow WHERE followingUsername =%s AND followStatus =1'
    cursor.execute(query3, (user))
    data3 = cursor.fetchall()
    cursor.close()
    return render_template('following.html',username=user, user_list=data, user_list2=data2, user_list3=data3)

#image
@app.route("/image/<image_name>", methods=["GET"])
def image(image_name):
    image_location = os.path.join(IMAGES_DIR, image_name)
    if os.path.isfile(image_location):
        return send_file(image_location, mimetype="image/jpg")
    
#posting page
@app.route("/post")
@login_required
def post():
    username = session['username']
    cursor = conn.cursor();
    query = 'SELECT DISTINCT groupName, groupOwner FROM belongto NATURAL JOIN friendgroups WHERE username = %s'
    cursor.execute(query, (username))
    data = cursor.fetchall()
    cursor.close()
    return render_template("post.html", group= data )

#to post an image
@app.route('/postAuth', methods=["POST"])
@login_required
def postAuth():
     if request.files:
         photoOwner = session['username']
         cursor=conn.cursor()
         allFollowers = request.form['allFollowers']
         caption = request.form['caption']
         image_file = request.files.get('imageToUpload', '')
         image_name = image_file.filename
         filepath = os.path.join(IMAGES_DIR, image_name)
         image_file.save(filepath)
         groupName = request.form['groupName']
         query = 'INSERT INTO photo (photoOwner, postingDate, filePath, allFollowers, caption) VALUES (%s, %s, %s, %s, %s)'
         cursor.execute(query, (photoOwner, time.strftime('%Y-%m-%d %H:%M:%S'), image_name, allFollowers, caption))

         if (allFollowers=='1'):
             flash('Image has been successfully uploaded')
             return redirect (url_for('post'))
         else:
             groupName = request.form['groupName']
             query0='SELECT groupOwner FROM friendgroups WHERE groupName = %s'
             cursor.execute(query0, groupName)
             groupowner = cursor.fetchone()
             groupOwner = groupowner['groupOwner']
             grouped='SELECT * FROM belongto WHERE groupName = %s AND username = %s'
             cursor.execute(grouped, (groupName, photoOwner))
             inGroup = cursor.fetchall()
             if (inGroup):            
                 query1 = '''SELECT ID FROM photo WHERE ID IN (SELECT ID FROM photo WHERE postingDate = (SELECT MAX(postingDate) FROM photo))
                 ORDER BY ID DESC LIMIT 1'''
                 cursor.execute(query1)
                 photoID = cursor.fetchone()
                 value = int(photoID['ID'])
                 query2 = 'INSERT INTO sharewith (ID, groupName, groupOwner) VALUES(%s, %s, %s)'
                 cursor.execute(query2, (value, groupName, groupOwner))
                 cursor.close()
                 flash('Image has been successfully uploaded')
                 return redirect (url_for('post'))
             else:
                 flash('You are not in that friend group')
                 return redirect (url_for('post'))

#to send a tag request to the user who can see the logged-in user's images
@app.route('/tagAuth', methods = ["GET", "POST"])
@login_required
def tagAuth():
    username = session['username']
    taggedUser = request.form['taggedUsername']
    ID = request.form['ID']
    cursor = conn.cursor();
    query1 = 'SELECT * FROM tagged WHERE username =%s AND ID = %s AND tagStatus =0'
    cursor.execute (query1, (taggedUser, ID))
    duplicate1 = cursor.fetchone()
    query2 = 'SELECT * FROM tagged WHERE username =%s AND ID = %s AND tagStatus =1'
    cursor.execute (query2, (taggedUser, ID))
    duplicate = cursor.fetchone()
    query3 = '''SELECT followerUsername AS username FROM follow WHERE followerUsername = %s AND
    followingUsername = %s AND followStatus =1
    UNION SELECT username FROM belongto AS b JOIN sharewith AS s ON (b.groupName = s.groupName)
    JOIN photo AS p ON (s.ID = p.ID)  WHERE username= %s AND p.ID = %s'''
    cursor.execute (query3, (taggedUser, username, taggedUser, ID))
    visible = cursor.fetchone() 
    if (duplicate):
        flash('You already tagged the user')
        return redirect (url_for('home'))
    if (duplicate1):
        flash('You already sent a tag request and still pending')
        return redirect (url_for('home'))
    query = 'SELECT username FROM person WHERE username =%s'
    cursor.execute(query, (taggedUser))
    data = cursor.fetchone()
    if (not data):
        flash('No Such User Exists')
        return redirect (url_for('home'))
    if (taggedUser == username):
        query = 'INSERT INTO tagged(username, ID, tagStatus) VALUES (%s,%s,1)'
        cursor.execute(query, (taggedUser, ID))
        flash('Tagged Successfully')
        return redirect (url_for('home'))
    elif (not visible):
        flash('This user cannot see your image')
        return redirect (url_for('home'))
    else:
        query = 'INSERT INTO tagged(username, ID, tagStatus) VALUES (%s,%s,0)'
        cursor.execute(query, (taggedUser, ID))
        flash('Tag request sent')
        cursor.close()
        return redirect (url_for('home'))

#to send a follow request to the user
@app.route('/followingAuth', methods=['GET', 'POST'])
@login_required
def followingAuth():
    username = session['username']
    user = request.form['photoOwner']
    cursor = conn.cursor();
    query0 = '''SELECT filePath, ID, firstName, lastName, photoOwner, postingDate, caption
    FROM photo JOIN person ON (photoOwner = username)
    WHERE photoOwner = %s
    ORDER BY postingDate DESC'''
    cursor.execute(query0, (user))
    data = cursor.fetchall()
    query = 'SELECT followerUsername, followingUsername FROM follow where followerUsername = %s and followingUsername = %s and followStatus = 1'
    cursor.execute(query, (username, user))
    followed = cursor.fetchone()
    query4 = 'SELECT * FROM follow where followerUsername = %s and followingUsername = %s and followStatus = 0'
    cursor.execute(query4, (username, user))
    followed2 = cursor.fetchone()
    if (followed2):
        flash("You already sent a follow request and still pending")
        return render_template('show_posts.html', username=user, posts=data )
    if (followed): #duplicate
        flash("You are already following this user")
        return render_template('show_posts.html', username=user, posts=data )
    else:
        query2 = 'INSERT INTO follow VALUES (%s, %s, 0)'
        cursor.execute(query2, (username, user))
        flash("You have requested a Follow")
        cursor.close()
        return render_template('show_posts.html', username=user, posts=data)

#page for managing received tag and follow request
@app.route("/manage")
@login_required
def manage():
    username = session['username']
    cursor = conn.cursor()
    query = 'SELECT * FROM follow WHERE followingUsername= %s AND followStatus = 0'
    cursor.execute(query, (username))
    data1 =cursor.fetchall()
    query2 = 'SELECT * FROM tagged NATURAL JOIN photo WHERE username = %s AND  tagStatus=0'
    cursor.execute(query2, (username))
    data2 =cursor.fetchall()
    cursor.close()
    return render_template("manage.html",dataFollow=data1,dataTag=data2)

#accept or decline tag request
@app.route('/manageTag', methods=['GET', 'POST'])
@login_required
def manageTag():
    cursor = conn.cursor()
    username = session['username']
    choice = request.form['choice']
    ID= request.form['ID']
    if (choice =='1'):
        query1 = 'UPDATE tagged SET tagStatus =1 WHERE username = %s AND ID = %s'
        cursor.execute (query1, (username, ID))
    else:
        query2 = 'DELETE FROM tagged WHERE username = %s AND ID = %s'
        cursor.execute (query2, (username, ID))
    cursor.close()
    return redirect (url_for('manage'))

#accept or decline follow request
@app.route('/manageFollow', methods=['GET', 'POST'])
@login_required
def manageFollow():
    cursor = conn.cursor()
    username = session['username']
    choice = request.form['choice']
    followerusername = request.form['followerUsername']
    if (choice =='1'):
        query1 = 'UPDATE follow SET followStatus =1 WHERE followerUsername= %s AND followingUsername = %s'
        cursor.execute (query1, (followerusername, username))
    else:
        query2 = 'DELETE FROM follow WHERE followerUsername =%s AND followingUsername = %s'
        cursor.execute (query2, (followerusername, username))
    cursor.close()
    return redirect (url_for('manage'))

#logout
@app.route('/logout')
def logout():
    session.pop('username')
    return redirect('/')


if __name__ == "__main__":
    if not os.path.isdir("static"):
        os.mkdir(IMAGES_DIR)
    app.run('127.0.0.1', 5000, debug = True)

from flask import Flask, render_template, request, session, url_for, redirect
import pymysql.cursors
import hashlib
import datetime
from functools import wraps

app = Flask(__name__)
app.secret_key = "super secret key"
SALT = '12345'

conn = pymysql.connect(host='localhost',
                       port = 3306,
                       user='root',
                       password='',
                       db='finstagram',
                       charset='utf8mb4',
                       cursorclass=pymysql.cursors.DictCursor)

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
        hashedPassword = hashlib.sha256(password.encode("utf-8")).hexdigest()
                    
        cursor = conn.cursor()
        query = 'SELECT * FROM person WHERE username = %s and password = %s'
        cursor.execute(query, (username, password))
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
        error = "This user already exists"
        return render_template('register.html', error = error)
    else:
        ins = 'INSERT INTO person VALUES(%s, %s, %s, %s, %s)'
        cursor.execute(ins, (username, password, firstname, lastname, biography))
        conn.commit()
        cursor.close()
        return render_template('index.html')

#see what are posted without logging in
@app.route('/test')
def test():
    cursor = conn.cursor();
    query = 'SELECT * FROM photo ORDER BY postingDate DESC'
    cursor.execute(query)
    data = cursor.fetchall()
    cursor.close()
    return render_template('test.html', posts=data)

#home with personal posts
@app.route('/home')
@login_required
def home():
    user = session['username']
    cursor = conn.cursor();
    query = '''SELECT ID, photoOwner, postingDate, caption
    FROM photo
    WHERE photoOwner = %s
    ORDER BY postingDate DESC'''
    cursor.execute(query, (user))
    data = cursor.fetchall()
    cursor.close()
    return render_template('home.html', username=user, posts=data)

#view posts that are posted by people who the user follows &
#people who shared the post in the group which the user is in
@app.route('/view')
@login_required
def view():
    user = session['username']
    cursor = conn.cursor();
    query = '''SELECT ID, photoOwner, postingDate, caption
    FROM photo JOIN follow ON (photoOwner = followerUsername) 
    WHERE followingUsername = %s AND allFollowers = 1 AND followStatus = 1
    UNION
    SELECT p.ID,p.photoOwner, p.postingDate, p.caption
    FROM photo AS p JOIN sharewith AS s ON (p.ID = s.ID)
    JOIN belongto AS b ON (s.groupName = b.groupName AND s.groupOwner = b.groupOwner)
    WHERE b.username = %s AND b.username != b.groupOwner
    ORDER BY postingDate DESC'''
    cursor.execute(query, (user,user))
    data = cursor.fetchall()
    cursor.close()
    return render_template('view.html', username=user, posts=data)

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
    cursor = conn.cursor();
    query = 'SELECT username, firstName, lastName FROM person'
    cursor.execute(query)
    data = cursor.fetchall()
    cursor.close()
    return render_template('select_blogger.html', user_list=data)

#see who the user follows
@app.route('/following') 
@login_required
def following():
    user = session['username']
    cursor = conn.cursor();
    query = 'SELECT followerUsername FROM follow WHERE followingUsername =%s'
    cursor.execute(query, (user))
    data = cursor.fetchall()
    cursor.close()
    return render_template('following.html',username=user, user_list=data)

#post page
@app.route('/post')
def post():
    cursor = conn.cursor()
    cursor.execute('SELECT groupName FROM belongto WHERE username = %s', (session['username']))
    data = cursor.fetchall()
    return render_template('post.html', data = data)


#logout
@app.route('/logout')
def logout():
    session.pop('username')
    return redirect('/')

#Run the app on localhost port 5000
#debug = True -> you don't have to restart flask
#for changes to go through, TURN OFF FOR PRODUCTION
if __name__ == "__main__":
    app.run('127.0.0.1', 5000, debug = True)

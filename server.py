
"""
Columbia's COMS W4111.001 Introduction to Databases
Example Webserver
To run locally:
    python3 server.py
Go to http://localhost:8111 in your browser.
A debugger such as "pdb" may be helpful for debugging.
Read about it online.
"""
import os
import re
import datetime
from click.core import Context
from flask.globals import session
  # accessible as a variable in index.html:
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)
#
# The following is a dummy URI that does not connect to a valid database. You will need to modify it to connect to your Part 2 database in order to use the data.
#
# XXX: The URI should be in the format of: 
#
#     postgresql://USER:PASSWORD@34.74.246.148/proj1part2
#
# For example, if you had username gravano and password foobar, then the following line would be:
#
#     DATABASEURI = "postgresql://gravano:foobar@34.74.246.148/proj1part2"
#
DATABASEURI = "postgresql://daa2182:daa2182@34.74.246.148/proj1part2"


#
# This line creates a database engine that knows how to connect to the URI above.
#
engine = create_engine(DATABASEURI)

#Secret Key
app.secret_key = "\x1b\x86'\x19'\x16\x9f\\V\xee\xf0\xc6\nU\xe0\xf1\xceX~\x13K\x0bL\x93"

#
# Example of running queries in your database
# Note that this will probably not work if you already have a table named 'test' in your database, containing meaningful data. This is only an example showing you how to run queries in your database using SQLAlchemy.

#Commented 5 lines:
#engine.execute("""CREATE TABLE IF NOT EXISTS test (
#  id serial,
#  name text
#);""")
#engine.execute("""INSERT INTO test(name) VALUES ('grace hopper'), ('alan turing'), ('ada lovelace');""")


@app.before_request
def before_request():
  """
  This function is run at the beginning of every web request 
  (every time you enter an address in the web browser).
  We use it to setup a database connection that can be used throughout the request.

  The variable g is globally accessible.
  """
  try:
    g.conn = engine.connect()
  except:
    print("uh oh, problem connecting to database")
    import traceback; traceback.print_exc()
    g.conn = None

@app.teardown_request
def teardown_request(exception):
  """
  At the end of the web request, this makes sure to close the database connection.
  If you don't, the database could run out of memory!
  """
  try:
    g.conn.close()
  except Exception as e:
    pass


#
# @app.route is a decorator around index() that means:
#   run index() whenever the user tries to access the "/" path using a GET request
#
# If you wanted the user to go to, for example, localhost:8111/foobar/ with POST or GET then you could use:
#
#       @app.route("/foobar/", methods=["POST", "GET"])
#
# PROTIP: (the trailing / in the path is important)
# 
# see for routing: https://flask.palletsprojects.com/en/2.0.x/quickstart/?highlight=routing
# see for decorators: http://simeonfranklin.com/blog/2012/jul/1/python-decorators-in-12-steps/
#
@app.route('/')
def index():
  """
  request is a special object that Flask provides to access web request information:

  request.method:   "GET" or "POST"
  request.form:     if the browser submitted a form, this contains the data in the form
  request.args:     dictionary of URL arguments, e.g., {a:1, b:2} for http://localhost?a=1&b=2

  See its API: https://flask.palletsprojects.com/en/2.0.x/api/?highlight=incoming%20request%20data

  """

  # DEBUG: this is debugging code to see what request looks like
  # print(request.args)


  #
  # Flask uses Jinja templates, which is an extension to HTML where you can
  # pass data to a template and dynamically generate HTML based on the data
  # (you can think of it as simple PHP)
  # documentation: https://realpython.com/primer-on-jinja-templating/
  #
  # You can see an example template in templates/index.html
  #
  # context are the variables that are passed to the template.
  # for example, "data" key in the context variable defined below will be 
  # accessible as a variable in index.html:
  #
  #     # will print: [u'grace hopper', u'alan turing', u'ada lovelace']
  #     <div>{{data}}</div>
  #     
  #     # creates a <div> tag for each element in data
  #     # will print: 
  #     #
  #     #   <div>grace hopper</div>
  #     #   <div>alan turing</div>
  #     #   <div>ada lovelace</div>
  #     #
  #     {% for n in data %}
  #     <div>{{n}}</div>
  #     {% endfor %}
  #
  #Our Instructions:
  # render_template looks in the templates/ folder for files.
  # for example, the below file reads template/index.html
  # Dictionary pass with prefix **
  context = {'message': 'Welcome to the Columbia Tutor Center'}
  return render_template("index.html", **context)

#
# This is an example of a different path.  You can see it at:
# 
#     localhost:8111/another
#
# Notice that the function name is another() rather than index()
# The functions for each app.route need to have different names
#

@app.route('/DashBoard')
def DashBoard():
  Context = {'message': "Welcome to dashboard " + session['Username']}
  return render_template('dashboard.html', **Context)

@app.route('/Registration', methods=['POST', 'GET'])
def registration():
  context = {'message':'Welcome to the registration page.'}
  return render_template("registration.html", **context)

@app.route('/loginCheck', methods=['POST'])
def loginCheck():
  # User input to login
  Username = request.form['usernameInput']
  Password = request.form['passwordInput']
  # Arguments setup
  args = (Username, Password)
  # SQL execute
  cursor = g.conn.execute('SELECT Username FROM Users WHERE Username = (%s) AND Password = (%s)', args)
  result = cursor.fetchone()
  cursor.close()
  # Check whether this user exist or not
  if result == None:
    context = {'message': 'Wrong Username or Password, please try again!'}
    return render_template('index.html', **context)
  else:
    session['Username'] = Username
    return redirect('/DashBoard')

@app.route('/registrationCheck', methods = ['POST'])
def registrationCheck():
  try:
    Username = request.form['usernameInput']
    Password = request.form['passwordInput']
    RealName = request.form['realnameInput']
    Email = request.form['emailInput']
    PhoneNumber = request.form['phonenumberInput']
    RoutingNumber = request.form['routingnumberInput']
    BankAccount = request.form['bankaccountInput']
    AccountType = request.form['accounttypeInput']
    GPA = request.form['gpaInput']
    Skills = request.form['skillsInput']
    argsUsers = (Username, Password, RealName, Email, PhoneNumber, RoutingNumber, BankAccount, AccountType)
    argsTutors = (Username, Skills)
    argsStudents = (Username, float(GPA))
    g.conn.execute('INSERT INTO Users VALUES (%s, %s, %s, %s, %s, %s, %s, %s)', argsUsers)
    g.conn.execute('INSERT INTO Tutors(Username, Skills) VALUES (%s, %s)', argsTutors)
    g.conn.execute('INSERT INTO Students(Username, GPA) VALUES (%s, %s)',argsStudents)
  except Exception as e:
    context = {'message':e}
    return render_template('registration.html', **context)

  argsNotification = ("Welcome to Columbia Tutoring Center!", Username)
  g.conn.execute('INSERT INTO NotificationBoxes_access (time, content, username) VALUES (now() AT TIME ZONE \'EST\', %s, %s)', argsNotification)
  context = {'message': 'Register Successfully And Please Login!'}
  return render_template('index.html', **context)

'''
@app.route('/another')
def another():
  return render_template("another.html")
'''
@app.route('/Logout')
def Logout():
  session['Username'] = None
  Context = {'message': "Logout Successfully"}
  return render_template('index.html', **Context)

@app.route('/Advertisement')
def Advertisement():
  cursor = g.conn.execute('SELECT AD.AdID, AD.Location, AD.AppointmentTime, AD.AvailableSeats, AD.Price, AD.Comments, AD.Username, D.DepartmentName, C.CourseName, C.CoureDescription \
    FROM Adertisements_manage_associate AD, Departments D, Courses_belongs C WHERE AD.DepartmentID = D.DepartmentID  AND AD.CourseID = C.CourseID AND \
    AD.DepartmentID = C.DepartmentID AND AD.AppointmentTime >= now() AT TIME ZONE \'EST\'')
  result = cursor.fetchone()
  store = []
  document = {}
  while result != None:
    document['AdID'] = result[0]
    document['Location'] = result[1]
    document['AppointmentTime'] = result[2]
    document['AvailableSeats'] = result[3]
    document['Price'] = result[4]
    document['Comments'] = result[5]
    document['Username'] = result[6]
    document['DepartmentName'] = result[7]
    document['CourseName'] = result[8]
    document['CoureDescription'] = result[9]
    store.append(document)
    document = {}
    result = cursor.fetchone()
  Context = {'store': store}
  cursor.close()
  return render_template('advertisement.html', **Context)

@app.route('/MyAdvertisement')
def MyAdvertisement():
  args = (session['Username'])
  cursor = g.conn.execute('SELECT AD.AdID, AD.Location, AD.AppointmentTime, AD.AvailableSeats, AD.Price, AD.Comments, AD.Username, D.DepartmentName, C.CourseName, C.CoureDescription \
    FROM Adertisements_manage_associate AD, Departments D, Courses_belongs C WHERE AD.DepartmentID = D.DepartmentID  AND AD.CourseID = C.CourseID AND \
    AD.DepartmentID = C.DepartmentID AND AD.Username = (%s)', args)
  result = cursor.fetchone()
  store = []
  document = {}
  while result != None:
    document['AdID'] = result[0]
    document['Location'] = result[1]
    document['AppointmentTime'] = result[2]
    document['AvailableSeats'] = result[3]
    document['Price'] = result[4]
    document['Comments'] = result[5]
    document['Username'] = result[6]
    document['DepartmentName'] = result[7]
    document['CourseName'] = result[8]
    document['CoureDescription'] = result[9]
    store.append(document)
    document = {}
    result = cursor.fetchone()
  Context = {'store': store}
  cursor.close()
  cursor = g.conn.execute('SELECT now() AT TIME ZONE \'EST\'')
  # only one result, fetchone is enough
  nowTime = cursor.fetchone()
  Context['nowTime'] = nowTime[0]
  cursor.close()
  # Departments and courses
  cursor = g.conn.execute('SELECT C.DepartmentID, D.DepartmentName, C.CourseID, C.CourseName \
    FROM Departments D, Courses_belongs C WHERE D.DepartmentID = C.DepartmentID')
  result = cursor.fetchone()
  store = []
  document = {}
  while result != None:
    document['DepartmentID'] = result[0]
    document['DepartmentName'] = result[1]
    document['CourseID'] = result[2]
    document['CourseName'] = result[3]
    store.append(document)
    document = {}
    result = cursor.fetchone()
  Context['Department'] = store
  cursor.close()
  return render_template('myadvertisement.html', **Context)

@app.route('/newAdInsertion', methods=['POST'])
def newAdInsertion():
  location = request.form['LocationInput']
  AppointmentTime = request.form['AppointmentTimeDateInput'] + ' ' + request.form['AppointmentTimeTimeInput'] + ':00'
  AvailableSeats = request.form['AvailableSeatsInput']
  Price = request.form['PriceInput']
  CommentsInput = request.form['CommentsInput']
  DepartmentCourseInput = request.form['DepartmentCourseInput'].split('/')
  Department = DepartmentCourseInput[0]
  Course = DepartmentCourseInput[1]
  try:
    temp = datetime.datetime.strptime(AppointmentTime, '%Y-%m-%d %H:%M:%S')
    if temp < datetime.datetime.now():
      Context = {'message': 'Please input a future appoinment time'}
      return render_template('dashboard.html', **Context)
    args = (location, AppointmentTime, AvailableSeats, Price, CommentsInput, session['Username'], Department, Course)
    g.conn.execute('INSERT INTO Adertisements_manage_associate (Location, AppointmentTime, AvailableSeats, Price, Comments, Username, DepartmentID, CourseID) VALUES\
      (%s, %s, %s, %s, %s, %s, %s, %s)', args)
    args = ('Your advertisement has been succefully placed', session['Username'])
    g.conn.execute('INSERT INTO NotificationBoxes_access (Time, Content, Username) VALUES (now() AT TIME ZONE \'EST\', %s, %s)', args)
  except Exception as e:
    Context = {'message': e}
    return render_template('dashboard.html', **Context)
  Context = {'message':'Advertisement Placed Successfully'}
  return render_template('dashboard.html', **Context)

# Update advertisement
@app.route('/MyAdvertisement/Update/<AdID>')
def AdUpdate(AdID):
  session['AdID'] = AdID
  Context = {}
  args = (AdID)
  cursor = g.conn.execute('SELECT AD.Location, AD.AppointmentTime, AD.AvailableSeats, AD.Price, AD.Comments \
    FROM Adertisements_manage_associate AD WHERE AD.AdID = (%s)', args)
  # Only one ad will be returned because AdID is a primary key.
  result = cursor.fetchone()
  Context['Location'] = result[0]
  Context['AppointmentTime'] = result[1]
  Context['AvailableSeats'] = result[2]
  Context['Price'] = result[3]
  Context['Comments'] = result[4]
  cursor.close()
  # Departments and courses
  cursor = g.conn.execute('SELECT C.DepartmentID, D.DepartmentName, C.CourseID, C.CourseName \
    FROM Departments D, Courses_belongs C WHERE D.DepartmentID = C.DepartmentID')
  result = cursor.fetchone()
  store = []
  document = {}
  while result != None:
    document['DepartmentID'] = result[0]
    document['DepartmentName'] = result[1]
    document['CourseID'] = result[2]
    document['CourseName'] = result[3]
    store.append(document)
    document = {}
    result = cursor.fetchone()
  Context['Department'] = store
  cursor.close()
  return render_template('AdUpdate.html',**Context)

@app.route('/AdUpdateCheck', methods = ['POST'])
def AdUpdateCheck():
  AdID = session['AdID']
  location = request.form['LocationInput']
  AppointmentTime = request.form['AppointmentTimeDateInput'] + ' ' + request.form['AppointmentTimeTimeInput'] + ':00'
  AvailableSeats = request.form['AvailableSeatsInput']
  Price = request.form['PriceInput']
  CommentsInput = request.form['CommentsInput']
  DepartmentCourseInput = request.form['DepartmentCourseInput'].split('/')
  Department = DepartmentCourseInput[0]
  Course = DepartmentCourseInput[1]
  try:
    temp = datetime.datetime.strptime(AppointmentTime, '%Y-%m-%d %H:%M:%S')
    if temp < datetime.datetime.now():
      Context = {'message': 'Please input a future appoinment time'}
      return render_template('dashboard.html', **Context)
    # Argument set up
    args = (location, AppointmentTime, AvailableSeats, Price, CommentsInput, Department, Course, AdID)
    g.conn.execute('UPDATE Adertisements_manage_associate SET Location=(%s), AppointmentTime=(%s), AvailableSeats=(%s), Price=(%s), Comments=(%s),\
      DepartmentID=(%s), CourseID=(%s) WHERE AdID=(%s)',args)
  except Exception as e:
    Context = {'message': e}
    return render_template('dashboard.html', **Context)
  # message notification
  args = ('Your advertisement has been succefully updated', session['Username'])
  g.conn.execute('INSERT INTO NotificationBoxes_access (Time, Content, Username) VALUES (now() AT TIME ZONE \'EST\', %s, %s)', args)
  Context = {'message':'Advertisement Updated Successfully'}
  return render_template('dashboard.html', **Context)

@app.route('/MyProfile')
def MyProfiles():
  #select query join tutors+ student+users
  cursor = g.conn.execute("SELECT u.Password, u.RealName, u.Email, u.PhoneNumber, u.RoutingNumber, u.BankAccount, u.AccountType, t.Score, t.NumberRate,\
    t.Skills , s.GPA\
    FROM Users u, Tutors t, Students  s \
    where s.Username = t.Username and s.Username = u.Username and u.Username = (%s)",session['Username'])
  result = cursor.fetchone()
  Context = {}
  Context['Username'] = session['Username']
  Context['Password'] = result[0]
  Context['RealName'] = result[1]
  Context['Email'] = result[2]
  Context['PhoneNumber'] = result[3]
  Context['RoutingNumber'] = result[4]
  Context['BankAccount'] = result[5]
  Context['AccountType'] = result[6]
  Context['Score'] = result[7]
  Context['NumberRate'] = result[8]
  Context['Skills'] = result[9]
  Context['GPA'] = result[10]

  return render_template('MyProfile.html', **Context)

@app.route('/profileCheck', methods = ['POST'])
def ProfileCheck():
  try:
    Username = session['Username']
    Password = request.form['passwordInput']
    RealName = request.form['realnameInput']
    Email = request.form['emailInput']
    PhoneNumber = request.form['phonenumberInput']
    RoutingNumber = request.form['routingnumberInput']
    BankAccount = request.form['bankaccountInput']
    AccountType = request.form['accounttypeInput']
    GPA = request.form['gpaInput']
    Skills = request.form['skillsInput']
    argsUsers = (Password, RealName, Email, PhoneNumber, RoutingNumber, BankAccount, AccountType, Username)
    argsTutors = (Skills, Username)
    argsStudents = (float(GPA), Username)

    g.conn.execute('UPDATE Users SET Password = (%s), RealName = (%s), Email = (%s), PhoneNumber= (%s), RoutingNumber=(%s), BankAccount=(%s), AccountType=(%s) WHERE Username = (%s)', argsUsers)
    g.conn.execute('UPDATE Tutors SET Skills = (%s) WHERE Username = (%s)', argsTutors)
    g.conn.execute('UPDATE Students SET GPA =(%s) WHERE Username = (%s)',argsStudents)

  except Exception as e:
    context = {'message':e}
    return render_template('dashboard.html', **context)

  argsNotification = ("You just updated your profile!", Username)
  g.conn.execute('INSERT INTO NotificationBoxes_access (time, content, username) VALUES (now() AT TIME ZONE \'EST\', %s, %s)', argsNotification)
  context = {'message': 'Successsful update!'}
  return render_template('dashboard.html', **context)

@app.route('/VIP')
def VIP():
  Context = {'message': "Let's be a VIP member! " + session['Username']}
  return render_template('VIP.html', **Context)

@app.route('/VIPCheck', methods=['POST'])
def VIPCheck():
  try:
    # User input for end date
    endvip = request.form['endvip']
    # Arguments setup
    args = (endvip, session['Username'])
    args1 = (session['Username'])
    # SQL execute
    cursor = g.conn.execute('SELECT e.Username FROM VIPs_Enroll e WHERE e.Username = (%s)', args1)
    result = cursor.fetchone()
    # each user has only record in the VIPs_Enroll Table
    # here are two cases to consider
    cursor.close()
    #Case 1: if the user does not have a VIPs_Enroll record, new record will be inserted
    if result == None:
      g.conn.execute('INSERT INTO VIPs_Enroll(StartDate, EndDate, Username) VALUES (now() AT TIME ZONE \'EST\', %s, %s)', args)
    #Case 2: if there is exist a record for that user, only the end date will be updated
    else:
      g.conn.execute('UPDATE VIPs_Enroll SET EndDate = (%s) WHERE Username =  (%s)', args)

    #send Notification to the user
    argsNotification = ("You are a VIP member! Hope you enjoy it!", session['Username'])
    g.conn.execute('INSERT INTO NotificationBoxes_access (time, content, username) VALUES (now() AT TIME ZONE \'EST\', %s, %s)', argsNotification)
  except Exception as e:
    context = {'message':e} 
    return render_template('VIP.html', **context)
  context = {'message':"Congrats!You are a VIP now!"} 
  return render_template('Dashboard.html', **context)

@app.route('/SearchProfile', methods=["POST", "GET"])
def SearchProfile():
  cursor = g.conn.execute('SELECT Username from Users')
  result = cursor.fetchone()
  store = []
  document = {}
  while result != None:
    document['Username'] = result[0]
    store.append(document)
    document = {}
    result = cursor.fetchone()
  Context = {'store': store}
  cursor.close()
  return render_template('SearchProfile.html', **Context)

@app.route('/profile', methods=["POST", "GET"])
def retrieveProfile():
  PID = request.form['DUsersInput']
  cursor = g.conn.execute('SELECT Username from Users')
  result = cursor.fetchone()
  store = []
  document = {}
  while result != None:
    document['Username'] = result[0]
    store.append(document)
    document = {}
    result = cursor.fetchone()
  Context = {'store': store}
  cursor.close()
  args = (PID)
  cursor = g.conn.execute("SELECT u.Username, u.RealName, u.Email, t.Score, t.NumberRate,\
    t.Skills , s.GPA\
    FROM Users u, Tutors t, Students  s \
    where s.Username = t.Username and s.Username = u.Username and u.Username = (%s)",args)
  result = cursor.fetchone()
  store2 = []
  document = {}
  document['Username'] = result[0]
  document['RealName'] = result[1]
  document['Email'] = result[2]
  document['Score'] = result[3]
  document['NumberRate'] = result[4]
  document['Skills'] = result[5]
  document['GPA'] = result[6]
  store2.append(document)
  document = {}
  Context['store2'] = store2
  cursor.close()
  return render_template('SearchProfile.html', **Context)

#activeSessions
@app.route('/activeSessions', methods=["POST", "GET"])
def activeSessions():
  DID = request.form['DeptsInput']
  cursor = g.conn.execute('SELECT DepartmentID, DepartmentName from Departments')
  result = cursor.fetchone()
  store = []
  document = {}
  while result != None:
    document['DepartmentID'] = result[0]
    document['DepartmentName'] = result[1]
    store.append(document)
    document = {}
    result = cursor.fetchone()
  Context = {'store': store}
  cursor.close()
  args = (DID)
  cursor = g.conn.execute('SELECT AD.AdID, AD.Location, AD.AppointmentTime, AD.AvailableSeats, AD.Price, AD.Comments, AD.Username, D.DepartmentName, C.CourseName, C.CoureDescription \
    FROM Adertisements_manage_associate AD, Departments D, Courses_belongs C WHERE AD.DepartmentID = D.DepartmentID  AND AD.CourseID = C.CourseID AND \
    AD.DepartmentID = C.DepartmentID AND AppointmentTime >= now() AT TIME ZONE \'EST\' AND D.DepartmentID = (%s)', args)
  result = cursor.fetchone()
  store2 = []
  document = {}
  if result is None:
    Context['message']= 'No Available Sessions!'
  else:
    while result != None:
      document['AdID'] = result[0]
      document['Location'] = result[1]
      document['AppointmentTime'] = result[2]
      document['AvailableSeats'] = result[3]
      document['Price'] = result[4]
      document['Comments'] = result[5]
      document['Username'] = result[6]
      document['DepartmentName'] = result[7]
      document['CourseName'] = result[8]
      document['CoureDescription'] = result[9]
      result = cursor.fetchone()
      store2.append(document)
  document = {}
  Context['store2'] = store2
  cursor.close()
  return render_template('searchdepartment.html', **Context)


@app.route('/searchdepartment', methods=["POST", "GET"])
def searchdepartment():
  cursor = g.conn.execute('SELECT DepartmentID, DepartmentName from Departments')
  result = cursor.fetchone()
  store = []
  document = {}
  while result != None:
    document['DepartmentID'] = result[0]
    document['DepartmentName'] = result[1]
    store.append(document)
    document = {}
    result = cursor.fetchone()
  Context = {'store': store}
  cursor.close()
  return render_template('searchdepartment.html', **Context)

# Example of adding new data to the database
'''
@app.route('/add', methods=['POST'])
def add():
  name = request.form['name']
  g.conn.execute('INSERT INTO test(name) VALUES (%s)', name)
  return redirect('/')

@app.route('/login')
def login():
    abort(401)
    this_is_never_executed()
'''

if __name__ == "__main__":
  import click

  @click.command()
  @click.option('--debug', is_flag=True)
  @click.option('--threaded', is_flag=True)
  @click.argument('HOST', default='0.0.0.0')
  @click.argument('PORT', default=8111, type=int)
  def run(debug, threaded, host, port):
    """
    This function handles command line parameters.
    Run the server using:

        python3 server.py

    Show the help text using:

        python3 server.py --help

    """

    HOST, PORT = host, port
    print("running on %s:%d" % (HOST, PORT))
    app.run(host=HOST, port=PORT, debug=debug, threaded=threaded)

  run()

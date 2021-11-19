
"""
Columbia's COMS W4111.001 Introduction to Databases
Example Webserver
To run locally:
    python3 server.py
Go to http://localhost:8111 in your browser.
A debugger such as "pdb" may be helpful for debugging.
Read about it online.
"""

#importing packages
import os
import re
import datetime
from click.core import Context
from flask.globals import session
  # accessible as a variable in index.html:
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response
from werkzeug.datastructures import ContentSecurityPolicy

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
  # Login page
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
  # to display the dashboard page
  Context = {'message': "Welcome to dashboard " + session['Username']}
  return render_template('dashboard.html', **Context)

@app.route('/Registration', methods=['POST', 'GET'])
def registration():
  # to display the registration page
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
  # to check the user's inputs for registration
  try:
    #Getting inputs to prepare the parameters
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
    # update three tables related to the new user
    g.conn.execute('INSERT INTO Users VALUES (%s, %s, %s, %s, %s, %s, %s, %s)', argsUsers)
    g.conn.execute('INSERT INTO Tutors(Username, Skills) VALUES (%s, %s)', argsTutors)
    g.conn.execute('INSERT INTO Students(Username, GPA) VALUES (%s, %s)',argsStudents)
    # Send welcome notification to this user
    argsNotification = ("Welcome to Columbia Tutoring Center!", Username)
    g.conn.execute('INSERT INTO NotificationBoxes_access (time, content, username) VALUES (now() AT TIME ZONE \'EST\', %s, %s)', argsNotification)
    context = {'message': 'Register Successfully And Please Login!'}
  except Exception as e:
    context = {'message':"please check your input!"}
    return render_template('registration.html', **context)
  return render_template('index.html', **context)

@app.route('/Logout')
def Logout():
  # to enable the user to log out from the system
  session['Username'] = None
  Context = {'message': "Logout Successfully"}
  return render_template('index.html', **Context)

@app.route('/Advertisement')
def Advertisement():
  #feting all active advertisements
  cursor = g.conn.execute('SELECT AD.AdID, AD.Location, AD.AppointmentTime, AD.AvailableSeats, AD.Price, AD.Comments, AD.Username, D.DepartmentName, C.CourseName, C.CoureDescription \
    FROM Adertisements_manage_associate AD, Departments D, Courses_belongs C WHERE AD.DepartmentID = D.DepartmentID  AND AD.CourseID = C.CourseID AND \
    AD.DepartmentID = C.DepartmentID AND AD.AppointmentTime >= now() AT TIME ZONE \'EST\'')
  result = cursor.fetchone()
  store = []
  document = {}
  while result != None:
    #getting the output to prepare the parameters
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

@app.route('/OrderPlacing/<AdID>/<Username>/<Price>')
def OrderPlacing(AdID, Username, Price):
  # to place a new order 
  Context = {}
  args = (session["Username"], AdID)
  # obtaining the order ID of the current advertisement related to the current user
  cursor = g.conn.execute("SELECT OrderID FROM Orders_manage_link WHERE Username = (%s) AND AdID = (%s)", args)
  result = cursor.fetchone()
  if result != None:
    Context = {'message':'You cannot please multiple orders on this advertisement!'}
    return render_template('dashboard.html', **Context)
  # If it does not exist 
  # check if the current user enrolled in a VIP membership if so they will be offered 20% discount 
  cursor.close()
  cursor = g.conn.execute("SELECT VIPID FROM VIPs_Enroll WHERE EndDate >= now() AT TIME ZONE \'EST\' AND Username = %s", session["Username"])
  result = cursor.fetchone()
  if result == None:
    Context['Price'] = float(Price)
  else:
    Context['Price'] = float(Price) * 0.8
  Context['AdID'] = AdID
  cursor.close()
  return render_template('checkout.html', **Context)

@app.route('/checkout/<AdID>/<Price>')
def checkout(AdID, Price):
  # check the order information 
  args = (Price, 'Placed', session["Username"], AdID)
  # inserting into orders 
  g.conn.execute("INSERT INTO Orders_manage_link (OrderTime, Total, Status, UpdateTime, Username, AdID) \
    VALUES (now() AT TIME ZONE \'EST\', %s, %s, now() AT TIME ZONE \'EST\', %s, %s)", args)
  args = (AdID)
  #updating the advertisement 
  g.conn.execute("UPDATE Adertisements_manage_associate SET AvailableSeats = AvailableSeats - 1 WHERE AdID = %s", args)
  args = ('Your order has been successfully placed', session['Username'])
  #sending message to the current user 
  g.conn.execute('INSERT INTO NotificationBoxes_access (Time, Content, Username) VALUES (now() AT TIME ZONE \'EST\', %s, %s)', args)
  cursor = g.conn.execute("SELECT Username FROM Adertisements_manage_associate WHERE AdID = (%s)",AdID)
  result = cursor.fetchone()
  args = (f'One Student {session["Username"]} Registered in your advertisement ID {AdID}.', result[0])
  #sending message to the corresponding tutor 
  g.conn.execute('INSERT INTO NotificationBoxes_access (Time, Content, Username) VALUES (now() AT TIME ZONE \'EST\', %s, %s)', args)
  cursor.close()
  Context = {'message':'Order Placed Successfully'}
  return render_template('dashboard.html', **Context)

@app.route('/Orders', methods=['POST', 'GET'])
def MyOrder():
  # obtaining the expired orders' information related to the current user 
  cursor = g.conn.execute("SELECT o.AdID FROM Orders_manage_link o, Adertisements_manage_associate a WHERE o.AdID = a.AdID \
    AND a.AppointmentTime < now() AT TIME ZONE \'EST\' AND o.Username = (%s)", session["Username"])
  result = cursor.fetchone()
  while result != None:
    args = (result[0])
    # update the status of the expired orders
    g.conn.execute("UPDATE Orders_manage_link SET Status = 'SessionEnd' WHERE AdID = (%s)", args)
    result = cursor.fetchone()
  args = (session['Username'])
  # obtaining the orders' information related to the current user 
  cursor.close()
  cursor = g.conn.execute('SELECT o.OrderID, o.OrderTime, o.Total, o.Status, o.UpdateTime, o.AdID,\
    a.Username tutorUsername, a.Location, a.AppointmentTime, a.Comments, c.CourseName, d.DepartmentName\
    FROM Orders_manage_link o,  Adertisements_manage_associate a, Courses_belongs c, Departments d\
    WHERE d.DepartmentID = a.DepartmentID AND a.DepartmentID = c.DepartmentID AND a.CourseID = c.CourseID\
    AND o.AdID = a.AdID AND o.Username = (%s)', args)
  result = cursor.fetchone()
  store = []
  document = {}
  while result != None:
    # getting the output to prepare the paramaters
    document['OrderID'] = result[0]
    document['OrderTime'] = result[1]
    document['Total'] = result[2]
    document['Status'] = result[3]
    document['UpdateTime'] = result[4]
    document['AdID'] = result[5]
    document['tutorUsername'] = result[6]
    document['Location'] = result[7]
    document['AppointmentTime'] = result[8]
    document['Comments'] = result[9]
    document['CourseName'] = result[10]
    document['DepartmentName'] = result[11]
    store.append(document)
    document = {}
    result = cursor.fetchone()
  Context = {'store': store}
  cursor.close()
  return render_template('Orders.html', **Context)

@app.route('/OrderCancelling/<OID>')
def cancelOrder(OID):
  args = (OID)
  #obtaining the tutor information related to this order
  cursor = g.conn.execute("SELECT A.AdID, A.Username FROM Orders_manage_link O, Adertisements_manage_associate A \
    WHERE O.AdID = A.AdID AND OrderID = (%s)", args)
  #delete the order
  g.conn.execute("DELETE FROM Orders_manage_link WHERE OrderID = (%s)", args)
  result = cursor.fetchone()
  document= {}
  # getting the output to prepare the parameters
  document['AdID'] = result[0]
  document['Username'] = result[1]
  args = (document['AdID'])
  # update corresponding advertisement 
  g.conn.execute("UPDATE Adertisements_manage_associate SET AvailableSeats = AvailableSeats + 1 WHERE AdID = (%s)", args)
  cursor.close()
  args1 = ("An order has been cancelled successfully.",session['Username'])
  args2 = (f"Student {session['Username']} cancelled the registration of your session #{document['AdID']}", document['Username'])
  # send a notification message to the current user 
  g.conn.execute('INSERT INTO NotificationBoxes_access (Time, Content, Username) VALUES (now() AT TIME ZONE \'EST\', %s, %s)', args1)
  # send a notification message to the related tutor 
  g.conn.execute('INSERT INTO NotificationBoxes_access (Time, Content, Username) VALUES (now() AT TIME ZONE \'EST\', %s, %s)', args2)
  Context = {"message": "An order has been cancelled successfully."}
  return render_template('dashboard.html', **Context)

@app.route('/MyAdvertisement')
def MyAdvertisement():
  # obtaining the advertisements of the current user  
  args = (session['Username'])
  cursor = g.conn.execute('SELECT AD.AdID, AD.Location, AD.AppointmentTime, AD.AvailableSeats, AD.Price, AD.Comments, AD.Username, D.DepartmentName, C.CourseName, C.CoureDescription \
    FROM Adertisements_manage_associate AD, Departments D, Courses_belongs C WHERE AD.DepartmentID = D.DepartmentID  AND AD.CourseID = C.CourseID AND \
    AD.DepartmentID = C.DepartmentID AND AD.Username = (%s)', args)
  result = cursor.fetchone()
  store = []
  document = {}
  while result != None:
    # getting the output to prepare the parameters
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
  # obtain the current time
  cursor = g.conn.execute('SELECT now() AT TIME ZONE \'EST\'')
  # only one result, fetchone is enough
  nowTime = cursor.fetchone()
  Context['nowTime'] = nowTime[0]
  cursor.close()
  # Obtain the Departments and courses information
  cursor = g.conn.execute('SELECT C.DepartmentID, D.DepartmentName, C.CourseID, C.CourseName \
    FROM Departments D, Courses_belongs C WHERE D.DepartmentID = C.DepartmentID')
  result = cursor.fetchone()
  store = []
  document = {}
  while result != None:
    # getting the output to prepare the parameters
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
  try:
    #getting the input to prepare the parameterss
    location = request.form['LocationInput']
    AppointmentTime = request.form['AppointmentTimeDateInput'] + ' ' + request.form['AppointmentTimeTimeInput'] + ':00'
    AvailableSeats = request.form['AvailableSeatsInput']
    Price = request.form['PriceInput']
    CommentsInput = request.form['CommentsInput']
    DepartmentCourseInput = request.form['DepartmentCourseInput'].split('/')
    Department = DepartmentCourseInput[0]
    Course = DepartmentCourseInput[1]
    temp = datetime.datetime.strptime(AppointmentTime, '%Y-%m-%d %H:%M:%S')
    if temp < datetime.datetime.now():
      Context = {'message': 'Please input a future appoinment time'}
      return render_template('dashboard.html', **Context)
    args = (location, AppointmentTime, AvailableSeats, Price, CommentsInput, session['Username'], Department, Course)
    # insert new advertisement 
    g.conn.execute('INSERT INTO Adertisements_manage_associate (Location, AppointmentTime, AvailableSeats, Price, Comments, Username, DepartmentID, CourseID) VALUES\
      (%s, %s, %s, %s, %s, %s, %s, %s)', args)
    args = ('Your advertisement has been successfully placed', session['Username'])
    # insert new notification 
    g.conn.execute('INSERT INTO NotificationBoxes_access (Time, Content, Username) VALUES (now() AT TIME ZONE \'EST\', %s, %s)', args)
  except Exception as e:
    Context = {'message': "Please check your input!"}
    return render_template('dashboard.html', **Context)
  Context = {'message':'Advertisement Placed Successfully'}
  return render_template('dashboard.html', **Context)

# Update advertisement
@app.route('/MyAdvertisement/Delete/<AdID>')
def AdDelete(AdID):
  #retreive the username of the student related to that advertisement 
  cursor = g.conn.execute("SELECT Username FROM Orders_manage_link WHERE AdID = (%s)", AdID)
  result = cursor.fetchone()
  while result != None:
    args1 = (f"Session {AdID} is cancelled by its owner.", result[0])
    # sent a notification to each student
    g.conn.execute('INSERT INTO NotificationBoxes_access (Time, Content, Username) VALUES (now() AT TIME ZONE \'EST\', %s, %s)', args1)
    result = cursor.fetchone()
  args = (AdID)
  # delete this advertisement
  g.conn.execute("DELETE FROM Adertisements_manage_associate WHERE AdID = (%s)", args)
  args = ('Your advertisement has been successfully deleted.', session['Username'])
  # sent a notification to the current user
  g.conn.execute('INSERT INTO NotificationBoxes_access (Time, Content, Username) VALUES (now() AT TIME ZONE \'EST\', %s, %s)', args)
  Context = {'message':'Advertisement deleted Successfully'}
  cursor.close()
  return render_template('dashboard.html', **Context)


# Prepare for updating advertisement
@app.route('/MyAdvertisement/Update/<AdID>')
def AdUpdate(AdID):
  #prepare the parameters
  session['AdID'] = AdID
  Context = {}
  args = (AdID)
  #retreving the advertisement's information 
  cursor = g.conn.execute('SELECT AD.Location, AD.AppointmentTime, AD.AvailableSeats, AD.Price, AD.Comments \
    FROM Adertisements_manage_associate AD WHERE AD.AdID = (%s)', args)
  # Only one ad will be returned because AdID is a primary key
  result = cursor.fetchone()
  Context['Location'] = result[0]
  Context['AppointmentTime'] = result[1]
  Context['AvailableSeats'] = result[2]
  Context['Price'] = result[3]
  Context['Comments'] = result[4]
  cursor.close()
  # #retreving the departments' and courses' information
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
  #This to update the advertisement information
  try:
    # Getting the input to prepare the parameters
    AdID = session['AdID']
    location = request.form['LocationInput']
    AppointmentTime = request.form['AppointmentTimeDateInput'] + ' ' + request.form['AppointmentTimeTimeInput'] + ':00'
    AvailableSeats = request.form['AvailableSeatsInput']
    Price = request.form['PriceInput']
    CommentsInput = request.form['CommentsInput']
    DepartmentCourseInput = request.form['DepartmentCourseInput'].split('/')
    Department = DepartmentCourseInput[0]
    Course = DepartmentCourseInput[1]
    temp = datetime.datetime.strptime(AppointmentTime, '%Y-%m-%d %H:%M:%S')
    if temp < datetime.datetime.now():
      Context = {'message': 'Please input a future appoinment time'}
      return render_template('dashboard.html', **Context)
    # Argument set up
    args = (location, AppointmentTime, AvailableSeats, Price, CommentsInput, Department, Course, AdID)
    g.conn.execute('UPDATE Adertisements_manage_associate SET Location=(%s), AppointmentTime=(%s), AvailableSeats=(%s), Price=(%s), Comments=(%s),\
      DepartmentID=(%s), CourseID=(%s) WHERE AdID=(%s)',args)

    # message notification
    args = ('Your advertisement has been successfully updated', session['Username'])
    g.conn.execute('INSERT INTO NotificationBoxes_access (Time, Content, Username) VALUES (now() AT TIME ZONE \'EST\', %s, %s)', args)
    # Notify related students to check new information
    cursor = g.conn.execute("SELECT Username FROM Orders_manage_link WHERE AdID = (%s)", AdID)
    result = cursor.fetchone()
    while result != None:
      args = (f'Session #{AdID} is updated by your tutor please check it.', result[0])
      g.conn.execute('INSERT INTO NotificationBoxes_access (Time, Content, Username) VALUES (now() AT TIME ZONE \'EST\', %s, %s)', args)
      result = cursor.fetchone()
    Context = {'message':'Advertisement Updated Successfully'}
  except Exception as e:
    Context = {'message': "Please check your input!"}
    return render_template('dashboard.html', **Context)
  cursor.close()
  return render_template('dashboard.html', **Context)

@app.route('/MyProfile')
def MyProfiles():
  #This will display the profile of the current user showing his/her personal information that he/she can edit
  cursor = g.conn.execute("SELECT u.Password, u.RealName, u.Email, u.PhoneNumber, u.RoutingNumber, u.BankAccount, u.AccountType, t.Score, t.NumberRate,\
    t.Skills , s.GPA\
    FROM Users u, Tutors t, Students  s \
    where s.Username = t.Username and s.Username = u.Username and u.Username = (%s)",session['Username'])
  result = cursor.fetchone()
  Context = {}
  # Getting the output to prepare the paramters 
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
  cursor.close()
  return render_template('MyProfile.html', **Context)

@app.route('/Browse/<Username>')
# Browse tutor's personal information and how other people rate him/ her
def BrowseTutor(Username):
  # After the user clicks the user name, the profile of the corresponding user will be displayed
  PID = Username
  # Prepare for the drop down list
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
  # Prepare for that user's information
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
  store3 = []
  # Select how other people rate this specific user
  cursor = g.conn.execute("SELECT Score, Comments, Rate_time, Studentsusername, Tutorsusername FROM Rate_by WHERE Tutorsusername = (%s) ORDER BY Rate_time DESC", args)
  document = {}
  result = cursor.fetchone()
  while result != None:
    document["Score"] = result[0]
    document["Comments"] = result[1]
    document["Rate_time"] = result[2]
    document["Studentsusername"] = result[3]
    document["Tutorsusername"] = result[4]
    store3.append(document)
    document = {}
    result = cursor.fetchone()
  Context["store3"] = store3
  cursor.close()
  # Display results
  return render_template('SearchProfile.html', **Context)

@app.route('/profileCheck', methods = ['POST'])
def ProfileCheck():
  # this profile check for profile update 
  try:
    # take inputs to prepare parameters
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

    # update all three tables related to this user
    g.conn.execute('UPDATE Users SET Password = (%s), RealName = (%s), Email = (%s), PhoneNumber= (%s), RoutingNumber=(%s), BankAccount=(%s), AccountType=(%s) WHERE Username = (%s)', argsUsers)
    g.conn.execute('UPDATE Tutors SET Skills = (%s) WHERE Username = (%s)', argsTutors)
    g.conn.execute('UPDATE Students SET GPA =(%s) WHERE Username = (%s)',argsStudents)

    # create notification message
    argsNotification = ("You just updated your profile!", Username)
    g.conn.execute('INSERT INTO NotificationBoxes_access (time, content, username) VALUES (now() AT TIME ZONE \'EST\', %s, %s)', argsNotification)
    context = {'message': 'Successsful update!'}

  except Exception as e:
    context = {'message':"Please check your input!"}
    return render_template('dashboard.html', **context)
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
      g.conn.execute('UPDATE VIPs_Enroll SET StartDate = now() AT TIME ZONE \'EST\', EndDate = (%s) WHERE Username = (%s)', args)

    #send Notification to the user
    argsNotification = ("You are a VIP member! Hope you enjoy it!", session['Username'])
    g.conn.execute('INSERT INTO NotificationBoxes_access (time, content, username) VALUES (now() AT TIME ZONE \'EST\', %s, %s)', argsNotification)
  except Exception as e:
    context = {'message':"Please check your input!"} 
    return render_template('dashboard.html', **context)
  context = {'message':"Congrats!You are a VIP now!"} 
  return render_template('dashboard.html', **context)

@app.route('/Rating')
def Rating():
  # Fetch all the tutors who taught this user before
  cursor = g.conn.execute("SELECT A.Username FROM Orders_manage_link O, Adertisements_manage_associate A \
    WHERE O.AdID = A.AdID AND O.Status = 'SessionEnd' AND O.Username = (%s)", session['Username'])
  result = cursor.fetchone()
  store = []
  document = {}
  while result != None:
    document['Tutorname'] = result[0]
    store.append(document)
    document = {}
    result = cursor.fetchone()
  Context = {'store': store}
  cursor.close()
  # User can browse their own rating
  cursor = g.conn.execute("SELECT Score, Comments, Rate_time, Tutorsusername FROM Rate_by WHERE Studentsusername = (%s)", session['Username'])
  result = cursor.fetchone()
  store2 = []
  document = {}
  while result != None:
    document['Score'] = result[0]
    document['Comments'] = result[1]
    document['Rate_time'] = result[2]
    document['Tutorsusername'] = result[3]
    store2.append(document)
    document = {}
    result = cursor.fetchone()
  Context['store2'] = store2
  cursor.close()
  return render_template("rating.html", **Context)

@app.route('/RatingSubmit', methods=["POST", "GET"])
# insert or update the rating and also update tutor's score and NumberRate
def RatingSubmit():
  try:
    # taking user input and prepare parameters
    ScoreInput = request.form['ScoreInput']
    Comments = request.form['CommentsInput']
    Tutors = request.form['tutorsInput']
    args = (session['Username'], Tutors)
    # Checking the existence of the rating
    cursor = g.conn.execute("SELECT Score FROM Rate_by WHERE Studentsusername = (%s) AND Tutorsusername = (%s)", args)
    result = cursor.fetchone()
    # No exist, insert
    if result == None:
      args = [ScoreInput, Comments, session['Username'], Tutors]
      g.conn.execute("INSERT INTO Rate_by VALUES (%s,%s,now() AT TIME ZONE \'EST\', %s, %s)", args)
    # If exist, update
    else:
      args = [ScoreInput, Comments, session['Username'], Tutors]
      g.conn.execute("UPDATE Rate_by SET Score = (%s), Comments = (%s), Rate_time = now() AT TIME ZONE \'EST\' WHERE \
        Studentsusername = (%s) AND Tutorsusername = (%s)", args)
    # Computing average score and count records for the specific tutor
    cursor.close()
    cursor = g.conn.execute("SELECT Score FROM Rate_by WHERE Tutorsusername = (%s)", Tutors)
    result = cursor.fetchone()
    sumofScore = 0
    count = 0
    while result != None:
      sumofScore += int(result[0])
      count += 1
      result = cursor.fetchone()
    # average score computation
    averageScore = sumofScore / count
    totalrate = count
    args = [averageScore, totalrate, Tutors]
    # Update corresponding information of specific tutor
    g.conn.execute("UPDATE Tutors SET Score = (%s), NumberRate = (%s) WHERE Username = (%s)", args)
    # Display top 5 best tutors
    cursor.close()
    cursor = g.conn.execute('SELECT Username FROM Tutors ORDER BY Score DESC LIMIT 5')
    result = cursor.fetchone()
    Context = {}
    store = []
    document = {}
    # Prepare for message
    Context['message']= 'Thanks for your rating. Here are the five top rated tutors we recommended to you if you want to register another session.'
    # Not exist
    if result == None:
      Context['message']= 'No Available Tutors!'
    # If exist
    else:
      while result != None:
        document['Username'] = result[0]
        store.append(document)
        result = cursor.fetchone()
        document = {}
    Context['store'] = store
    cursor.close()
  # Exception handler
  except Exception as e:
    Context1 = {'message':'Please check your input'}
    return render_template('dashboard.html', **Context1)
  return render_template('topfive.html', **Context)

@app.route('/SearchProfile', methods=["POST", "GET"])
# Prepare for the user profile searching
def SearchProfile():
  # Fetching all usernames
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
  # Display results
  return render_template('SearchProfile.html', **Context)

@app.route('/profile', methods=["POST", "GET"])
# Fetch user profile of a user
def retrieveProfile():
  # Parameter preparation
  PID = request.form['DUsersInput']
  # Prepare for the drop down list
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
  # Fetch user profile of a user
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
  store3 = []
  # Fetch how other people rate this him/ her
  cursor = g.conn.execute("SELECT Score, Comments, Rate_time, Studentsusername, Tutorsusername FROM Rate_by WHERE Tutorsusername = (%s) ORDER BY Rate_time DESC", args)
  document = {}
  result = cursor.fetchone()
  while result != None:
    document["Score"] = result[0]
    document["Comments"] = result[1]
    document["Rate_time"] = result[2]
    document["Studentsusername"] = result[3]
    document["Tutorsusername"] = result[4]
    store3.append(document)
    document = {}
    result = cursor.fetchone()
  Context["store3"] = store3
  cursor.close()
  # Display results
  return render_template('SearchProfile.html', **Context)

#activeSessions
# Display all unexpired advertisements under a specific department
@app.route('/activeSessions', methods=["POST", "GET"])
def activeSessions():
  # Parameter preparation
  DID = request.form['DeptsInput']
  # Prepare for the drop down list
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
  # Obtain all unexpired advertisements under a specific department
  cursor = g.conn.execute('SELECT AD.AdID, AD.Location, AD.AppointmentTime, AD.AvailableSeats, AD.Price, AD.Comments, AD.Username, D.DepartmentName, C.CourseName, C.CoureDescription \
    FROM Adertisements_manage_associate AD, Departments D, Courses_belongs C WHERE AD.DepartmentID = D.DepartmentID  AND AD.CourseID = C.CourseID AND \
    AD.DepartmentID = C.DepartmentID AND AppointmentTime >= now() AT TIME ZONE \'EST\' AND D.DepartmentID = (%s)', args)
  result = cursor.fetchone()
  store2 = []
  document = {}
  # If no result
  if result is None:
    Context['message']= 'No Available Sessions!'
  # If results exist
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
      store2.append(document)
      document = {}
      result = cursor.fetchone()
  Context['store2'] = store2
  cursor.close()
  # Display results
  return render_template('searchdepartment.html', **Context)


@app.route('/Notification', methods=["POST", "GET"])
# Fetch notifications for user
def Notification():
  # Notifications fetching
  cursor = g.conn.execute('SELECT n.Time, n.Content from NotificationBoxes_access n where n.Username = (%s)',session['Username'])
  result = cursor.fetchone()
  store = []
  document = {}
  while result != None:
    document['Time'] = result[0]
    document['Content'] = result[1]
    store.append(document)
    document = {}
    result = cursor.fetchone()
  Context = {'store': store}
  cursor.close()
  # Return and display results
  return render_template('Notification.html', **Context)



@app.route('/searchdepartment', methods=["POST", "GET"])
# Prepare for search advertisements under a specific department
def searchdepartment():
  # Prepare the drop down menu
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
  # Display results
  return render_template('searchdepartment.html', **Context)

@app.route('/searchtutors', methods=["POST", "GET"])
# Prepare for search advertisements under a specific tutor
def searchtutors():
  # Prepare the drop down menu
  cursor = g.conn.execute('SELECT Username from Tutors')
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
  # Display results
  return render_template('searchtutors.html', **Context)

@app.route('/searchcourses', methods=["POST", "GET"])
# Prepare for search advertisements under a specific course
def searchcourses():
  # Prepare the drop down menu
  cursor = g.conn.execute('SELECT CourseName, CourseID, DepartmentID  FROM Courses_belongs')
  result = cursor.fetchone()
  store = []
  document = {}
  while result != None:
    document['CourseName'] = result[0]
    document['CourseID'] = result[1]
    document['DepartmentID'] = result[2]
    store.append(document)
    document = {}
    result = cursor.fetchone()
  Context = {'store': store}
  cursor.close()
  # Display the result
  return render_template('searchcourses.html', **Context)

#activeSessions
# Return all unexpired advertisements related to user-selected course
@app.route('/activeSessionsCourse', methods=["POST", "GET"])
def activeSessionsCourse():
  # Prepare for the parameters
  DCID = request.form['courseInput'].split('/')
  # DID: departmentID, CID: courseID
  DID = DCID[0]
  CID = DCID[1]
  # Prepare for the drop down list
  cursor = g.conn.execute('SELECT CourseName, CourseID, DepartmentID FROM Courses_belongs')
  result = cursor.fetchone()
  store = []
  document = {}
  while result != None:
    document['CourseName'] = result[0]
    document['CourseID'] = result[1]
    document['DepartmentID'] = result[2]
    store.append(document)
    document = {}
    result = cursor.fetchone()
  Context = {'store': store}
  cursor.close()
  args = (CID, DID)
  # Obtain all unexpired advertisements related to user-selected course
  cursor = g.conn.execute('SELECT AD.AdID, AD.Location, AD.AppointmentTime, AD.AvailableSeats, AD.Price, AD.Comments, AD.Username, D.DepartmentName, C.CourseName, C.CoureDescription \
    FROM Adertisements_manage_associate AD, Departments D, Courses_belongs C WHERE AD.DepartmentID = D.DepartmentID  AND AD.CourseID = C.CourseID AND \
    AD.DepartmentID = C.DepartmentID AND C.CourseID = (%s) AND AppointmentTime > now() AT TIME ZONE \'EST\' AND D.DepartmentID = (%s)', args)
  result = cursor.fetchone()
  store2 = []
  document = {}
  # If no session under that course
  if result is None:
    Context['message']= 'No Available Sessions!'
  # If there are sessions
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
      store2.append(document)
      document = {}
      result = cursor.fetchone()
  Context['store2'] = store2
  cursor.close()
  # Results display
  return render_template('searchcourses.html', **Context)

#activeSessions
# This function will return all unexpired sessions related to specific tutor
@app.route('/activeSessionsTutors', methods=["POST", "GET"])
def activeSessionsTutors():
  TID = request.form['tutorInput']
  # Prepare for the drop down box
  cursor = g.conn.execute('SELECT Username from Tutors')
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
  # Prepare for the all unexpired advertisements related to the selected tutor
  args = (TID)
  cursor = g.conn.execute('SELECT AD.AdID, AD.Location, AD.AppointmentTime, AD.AvailableSeats, AD.Price, AD.Comments, AD.Username, D.DepartmentName, C.CourseName, C.CoureDescription \
    FROM Adertisements_manage_associate AD, Departments D, Courses_belongs C WHERE AD.DepartmentID = D.DepartmentID  AND AD.CourseID = C.CourseID AND \
    AD.DepartmentID = C.DepartmentID AND AppointmentTime >= now() AT TIME ZONE \'EST\' AND AD.Username = (%s)', args)
  result = cursor.fetchone()
  store2 = []
  document = {}
  # If no advertisements exist
  if result is None:
    Context['message']= 'No Available Sessions!'
  # If he/ she has advertisements
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
      store2.append(document)
      document = {}
      result = cursor.fetchone()
  # Prepare for parameter
  Context['store2'] = store2
  cursor.close()
  return render_template('searchtutors.html', **Context)


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


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
  return render_template('another.html')

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
  return redirect('/DashBoard')

'''
@app.route('/another')
def another():
  return render_template("another.html")
'''

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

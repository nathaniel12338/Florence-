from flask import Flask, render_template, request, redirect, url_for, flash,session
from flaskext.mysql import MySQL
from flask_bcrypt import Bcrypt

app = Flask(__name__)
app.config['SECRET_KEY'] = 'hrhrhjrjrjrjrjrjr'  # Replace with a long, random string
mysql = MySQL(app)
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_DB'] = 'studentportal'
mysql.init_app(app)
bcrypt = Bcrypt(app)

def hash_password(password):
    return bcrypt.generate_password_hash(password).decode('utf-8')
@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '-1'
    return response    

@app.route('/')
def index():
    success_message = request.args.get('success_message', '')
    return render_template('index.html', success_message=success_message)

# ... (your existing code)

@app.route('/index', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        # Use parameterized query to prevent SQL injection
        cur = mysql.get_db().cursor()
        cur.execute("SELECT * FROM register WHERE email = %s AND password = %s", (email, password))
        user = cur.fetchone()
        cur.close()

        if user:
            # Email and password match, set user email in session
            session['user_email'] = email
           
            return redirect(url_for('dashboard'))
        else:
            # Email and password do not match
            flash("Invalid email or password. Please try again.", 'error')
            return render_template('index.html')

    success_message = request.args.get('success_message', '')
    return render_template('index.html', success_message=success_message)

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    # Fetch user email from session
    email = session.get('user_email', '')

    # Fetch username, gender, and class directly from the database based on the provided email
    cur = mysql.get_db().cursor()
    cur.execute("SELECT username, gender, class FROM register WHERE email = %s", (email,))
    user_data = cur.fetchone()

    # Check if there is data returned from the query
    if user_data:
        username, gender, user_class = user_data
    else:
        username, gender, user_class = None, None, None

    cur.close()

    success_message = request.args.get('success_message', '')

    # Fetch total number of registered students
    cur = mysql.get_db().cursor()
    cur.execute("SELECT COUNT(*) FROM register")
    total_students = cur.fetchone()[0]  # Fetch the count from the result
    cur.close()

    return render_template('dashboard.html', success_message=success_message, username=username, gender=gender, user_class=user_class, total_students=total_students)

# ... (your existing code)
@app.route('/checkresult', methods=['GET'])
def checkresult():
    success_message = request.args.get('success_message', '')
    return render_template('checkresult.html', success_message=success_message)

@app.route('/resulthostry', methods=['GET'])
def resulthostryt():
    success_message = request.args.get('success_message', '')
    return render_template('resulthostry.html', success_message=success_message)
@app.route('/announcement', methods=['GET'])
def announcement():
    success_message = request.args.get('success_message', '')
    return render_template('announcement.html', success_message=success_message)

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if request.method == 'POST':
        try:
            # Get the user's email from the session
            email = session.get('user_email', '')
            
            # Fetch user details based on the email
            cur = mysql.get_db().cursor()
            cur.execute("SELECT * FROM register WHERE email = %s", (email,))
            student_info = cur.fetchone()
            cur.close()

            if student_info:
                return render_template('profile.html', student_info=student_info)

        except Exception as e:
            print(f"Error during profile query: {str(e)}")
           
            return redirect(url_for('index'))

        
    return render_template('profile.html')
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        try:
            username = request.form.get('username')
            email = request.form.get('email')
            classd = request.form.get('class')
            gender = request.form.get('gender')
            password = request.form.get('password')
            
            # Check if any required field is empty
            if not (username and email and password and classd and gender):
               
                return render_template('register.html')

            # Insert the new user into the database
            cur = mysql.get_db().cursor()
            cur.execute("INSERT INTO register (username, email, class, gender, password) VALUES (%s, %s, %s, %s, %s)",
                        (username, email, classd, gender, password))
            mysql.get_db().commit()
            cur.close()

           
            return redirect(url_for('index'))

        except Exception as e:
            print(f"Error during registration: {str(e)}")
           
            return render_template('register.html', error_message=str(e))

    # If the request method is not POST, handle accordingly (e.g., redirect to the registration page)
    
    return render_template('register.html')

if __name__ == '__main__':
    app.config['DEBUG'] = True
    app.run(debug=True)

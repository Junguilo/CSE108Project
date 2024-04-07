from flask import Flask, redirect, url_for, request, render_template, jsonify
from flask_admin import Admin
from flask_sqlalchemy import SQLAlchemy
from flask_admin.contrib.sqla import ModelView
from flask_login import UserMixin, LoginManager, login_user, login_required, current_user, logout_user
#im scared abt the midterm
#me too :( I think i will fail 

app = Flask(__name__)
app.config['SECRET_KEY'] = 'super_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

#Database Information & Classes
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    is_teacher = db.Column(db.Boolean, default=False) 
    # is_admin = db.Column(db.Boolean, default = False) 

    def check_password(self, password):
        return self.password == password

class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    teacher = db.Column(db.String(100), nullable=False)
    time = db.Column(db.String(100), nullable=False)
    current_students = db.Column(db.Integer, default=0)
    capacity = db.Column(db.Integer, nullable=False)

    #relationShip with UserCourse
    #Usually the Parent will have this line rather than the children 
    #We can get all child objects(users) through this way 
    users = db.relationship("User", secondary="user_course" ,backref="Course")
    
class UserCourse(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    # is_teacher = db.Column(db.Boolean, default=False)  # Indicates if the user is the teacher of the course
    grade = db.Column(db.Integer)

    #define relationship to easily access objects
    user = db.relationship("User", backref="user_courses")
    course = db.relationship("Course", backref="course_users")

#Admin , we can go to the admin page with /admin
#We do not need any special html that comes with it
admin = Admin(app, name='Admin Panel', template_mode='bootstrap3')
admin.add_view(ModelView(User, db.session))
admin.add_view(ModelView(Course, db.session))
admin.add_view(ModelView(UserCourse, db.session))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
@app.route('/login')
def login_page():
    return render_template('loginP.html')

####################
# WORK HERE
####################
@app.route('/login', methods=['GET', 'POST'])
def login():
    # if current_user.is_authenticated:
    #     return redirect(url_for('courses'))
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            login_user(user)
            return redirect(url_for('courses'))
        else:
            return render_template('loginP.html', message='Invalid username or password')
    return render_template('loginP.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

# Add User to DB 
@app.route('/register')
def register():
    return render_template('createAcc.html')

@app.route('/register', methods=['POST'])
def register_post():
    data = request.json
    print("Received JSON data:", data)  
    username = data.get('username')
    password = data.get('password')
    is_teacher = data.get('is_teacher', False)
    if username is None or password is None:
        return jsonify({'error': 'Missing username or password'}), 400
    new_user = User(username=username, password=password, is_teacher = is_teacher)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'User added successfully'}), 201

#Show Enrolled courses by Students or Taught Courses by Professor
@app.route('/courses')
@login_required
def courses():
    user = User.query.filter_by(username=current_user.username).first()
    if user.is_teacher:
        # If the user is a teacher, render a different template
        courses = Course.query.filter_by(teacher=user.username).all()  # Query courses taught by the teacher
        return render_template('teachLog.html', courses=courses)
    else:
        # If the user is a student, render the studLog.html template

        #Takes all the courses that is enrolled by the user 
        user_courses = UserCourse.query.filter_by(user_id=user.id).all()

        #Takes all enrolled classes from enrolled student 
        courses = []
        for i in user_courses:
            #print(i) debug
            #Uses EnrolledID to compare to all courses
            course = Course.query.get(i.course_id)
            if course:  # Check if the course exists
                #print(course.name)
                courses.append(course)  # Append the Course object to the list
        return render_template('studLog.html', courses=courses)


#Show all courses
@app.route('/all-courses')
@login_required
def all_courses():
    courses = Course.query.all()
    return render_template('all_courses.html', courses=courses)

#AddStudent2Course Helper Functions
def getCourseID(course_name):
    course = Course.query.filter_by(name=course_name).first()
    if course:
        return course.id
    else:
        return None
    
def getUserID(username):
    user = User.query.filter_by(username=username).first()
    if user:
        return user.id
    else:
        return None
    
#Add Student To Course if logged in
@app.route('/enroll_course', methods=['POST'])
@login_required
def enrollCourse():
    courseID = request.form['course_id']
    userID = getUserID( current_user.username )
    courses = Course.query.all()
    
    #print(courseID)  Checking if our button returns the ids we want
    #print(getUserID(current_user.username))
    user = User.query.get(userID)
    course = Course.query.get(courseID)

    if course and user:
        #Check if we are already enrolled in course
        if user in course.users:
            #Del course from users if they are already enrolled
            course.users.remove(user)
            course.current_students -= 1
            course.capacity += 1
            db.session.commit()
            return render_template('all_courses.html', courses=courses, message="Removed User from Course")
        
        #add the user to the course
        course.users.append(user)
        course.current_students += 1
        course.capacity -= 1
        db.session.commit()
        return render_template('all_courses.html', courses=courses,message="User added to Course")
    else:
        return render_template('all_courses.html', courses=courses,message="User or Course not found")
    #return render_template('all_courses.html', courses=courses)

# Admins need to Create, Read, Update, Delete Data in DB

#Create Courses Page - For Admin
@app.route('/createCourses', methods=['GET','POST'])
def createCourse():

    #if will only run if we click button
    if request.method == 'POST':
        #Get all information added for course db
        courseName = request.form['name']
        teacher = request.form['teacher']
        time = request.form['time']
        currStudents = request.form['currStudents']
        capacity = request.form['capacity']

        newCourse = Course(name = courseName, teacher = teacher, time = time,
                            current_students = currStudents, capacity = capacity)
        db.session.add(newCourse)
        db.session.commit()
        #Sends us back to the website if successful
        return render_template('createCourse.html', message="Successfully added Course!")
    return render_template('createCourse.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)

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

#Database Information
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
#     students = db.relationship('User', secondary='enrollment', backref='courses')

# enrollment = db.Table('enrollment',
#     db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
#     db.Column('course_id', db.Integer, db.ForeignKey('course.id'), primary_key=True)
# )

class UserCourse(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    # is_teacher = db.Column(db.Boolean, default=False)  # Indicates if the user is the teacher of the course
    grade = db.Column(db.Integer)

admin = Admin(app, name='Admin Panel', template_mode='bootstrap3')
admin.add_view(ModelView(User, db.session))
admin.add_view(ModelView(Course, db.session))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

#Website
@app.route('/index')
@app.route('/')
# @login_required
def index():  # put application's code here
    return redirect('/login')

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
        user_courses = UserCourse.query.filter_by(user_id=user.id).all()
        courses = [uc.course for uc in user_courses]  # Extract courses associated with the student
        return render_template('studLog.html', courses=courses)



# @app.route('/all-courses')
# @login_required
# def all_courses():
#     courses = Course.query.all()
#     return render_template('all_courses.html', courses=courses)

#Admins need to Create, Read, Update, Delete Data in DB

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

#Add Student to Course
#@app.route('/addStudent', methods=['POST'])


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)

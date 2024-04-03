from flask import Flask, redirect, url_for, request, render_template
from flask_admin import Admin
from flask_sqlalchemy import SQLAlchemy
from flask_admin.contrib.sqla import ModelView
from flask_login import UserMixin, LoginManager, login_user, login_required, current_user, logout_user


app = Flask(__name__)
app.config['SECRET_KEY'] = 'super_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    is_teacher = db.Column(db.Boolean, default=False)  

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
    is_teacher = db.Column(db.Boolean, default=False)  # Indicates if the user is the teacher of the course
    grade = db.Column(db.Integer)

admin = Admin(app, name='Admin Panel', template_mode='bootstrap3')
admin.add_view(ModelView(User, db.session))
admin.add_view(ModelView(Course, db.session))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/index')
@app.route('/')
@login_required
def index():  # put application's code here
    return "You're logged in"

@app.route('/login')
def login_page():
    return render_template('loginP.html')

@app.route('/create-account')
def create_account():
    return render_template('createAcc.html')



@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            login_user(user)
            return redirect(url_for('index'))
        return render_template('login.html', message='Invalid username or password')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/courses')
@login_required
def courses():
    user = User.query.filter_by(username=current_user.username).first()
    if user.role == 'student':
        return render_template('student_courses.html', courses=user.courses)
    elif user.role == 'teacher':
        return render_template('teacher_courses.html', courses=user.courses)
    else:
        return redirect(url_for('admin.index'))

@app.route('/all-courses')
@login_required
def all_courses():
    courses = Course.query.all()
    return render_template('all_courses.html', courses=courses)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)


# create acct
# @app.route('/create-account')
# @login_required
# def create_account():
#     return render_template('createAcc.html')




# @app.route('/login', methods=['POST'])
# def login():
#     if current_user.is_authenticated:
#         return redirect(url_for('index'))
#     user = User.query.filter_by(username=request.form['username']).first()
#     if user is None or not user.check_password(request.form['password']):
#          return redirect(url_for('login'))
#     login_user(user)
#     return redirect(url_for('index'))


from flask import Flask, redirect, url_for, request, render_template
from flask_admin import Admin
from flask_sqlalchemy import SQLAlchemy
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user, login_user, login_required, LoginManager, UserMixin


app = Flask(__name__)

# set optional bootswatch theme
app.config['FLASK_ADMIN_SWATCH'] = 'cerulean'
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///example.sqlite"
app.secret_key = 'super secret key'
db = SQLAlchemy(app)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, unique=True, nullable=False)

    def check_password(self, password):
        return self.password == password


admin = Admin(app, name='microblog', template_mode='bootstrap3')
admin.add_view(ModelView(User, db.session))

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
  return User.query.get(user_id)
# create acct
# @app.route('/create-account')
# @login_required
# def create_account():
#     return render_template('createAcc.html')


@app.route('/create-account')
def create_account():
    return render_template('createAcc.html')


@app.route('/index')
@app.route('/')
@login_required
def index():  # put application's code here
    return "You're logged in"

@app.route('/login')
def login_page():
    return render_template('loginP.html')


@app.route('/login', methods=['POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    user = User.query.filter_by(username=request.form['username']).first()
    if user is None or not user.check_password(request.form['password']):
         return redirect(url_for('login'))
    login_user(user)
    return redirect(url_for('index'))



if __name__ == "__main__":
    app.run()

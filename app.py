from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from datetime import datetime
# from app import db, Distributor  # Replace with your actual import path
import pymysql  # Import pymysql to use with SQLAlchemy

# Set pymysql as the MySQL driver
pymysql.install_as_MySQLdb()

app = Flask(__name__)

# Flask Configuration
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/pharmacy_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Models
class User(db.Model):
    __tablename__ = 'user'
    U_Name = db.Column(db.String(80), unique=True, nullable=False)
    U_id = db.Column(db.Integer, primary_key=True)
    U_DOB = db.Column(db.String(120), nullable=False)
    U_Password = db.Column(db.String(120), nullable=False)
    U_Phone_no = db.Column(db.String(120), nullable=False)
    U_Address = db.Column(db.String(120), nullable=False)

    def set_password(self, password):
        self.U_Password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.U_Password, password)

class Customer(db.Model):
    __tablename__ = 'customers'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.String(20), nullable=True)
    gender = db.Column(db.String(20), nullable=True)
    email = db.Column(db.String(100), nullable=False, unique=True)
    phone = db.Column(db.String(20), nullable=True)
    address = db.Column(db.String(120), nullable=True)

class Drug(db.Model):
    __tablename__ = 'drug'
    Dr_Name = db.Column(db.String(100), nullable=False)
    Dr_Id = db.Column(db.Integer, primary_key=True)
    Dr_DOM = db.Column(db.String(100), nullable=False)
    Dr_DOE = db.Column(db.String(100), nullable=False)
    Dr_MRP = db.Column(db.Float, nullable=False)
    Dr_Cost_Price = db.Column(db.Float, nullable=False)
    Dr_Type = db.Column(db.String(100), nullable=False)
    Dr_Use = db.Column(db.String(100), nullable=False)
    Dr_Quantity = db.Column(db.Integer, nullable=False)
    D_ID = db.Column(db.Integer, nullable=False)
    U_ID = db.Column(db.Integer, nullable=False)

class Distributor(db.Model):
    __tablename__ = 'distributor'
    D_Name = db.Column(db.String(100), nullable=False)
    D_ID = db.Column(db.Integer, primary_key=True)
    D_Phone_no = db.Column(db.String(100), nullable=False)
    D_Address = db.Column(db.String(100), nullable=False)

# Authentication decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Routes



# @app.route('/')
# @login_required
# def index():
#     # return render_template('index.html')
#     pulse_data = [60, 65, 70, 75, 80, 85]  # Replace with actual data from the database
#     mood_data = [27, 37, 36]  # Replace with actual data from the database
#     return render_template('dashboard.html', pulse_data=pulse_data, mood_data=mood_data)

@app.route('/')
@login_required
def index():
    return render_template('index.html')



@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        dob = request.form['dob']  # Date should be in 'YYYY-MM-DD' format
        phone_no = request.form['phone_no']
        address = request.form['address']
        
        # Validate and format date
        try:
            dob = datetime.strptime(dob, '%d-%m-%Y').strftime('%Y-%m-%d')
        except ValueError:
            flash('Invalid date format. Please use DD-MM-YYYY.', 'danger')
            return redirect(url_for('signup'))
        
        # Check if the username already exists
        if User.query.filter_by(U_Name=username).first():
            flash('Username already exists', 'danger')
            return redirect(url_for('signup'))
        
        # Create a new user and add to the database
        new_user = User(U_Name=username, U_DOB=dob, U_Phone_no=phone_no, U_Address=address)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        
        flash('Sign up successful! You can now log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('signup.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(U_Name=username).first()
        if user and check_password_hash(user.U_Password, password):
            session['user_id'] = user.U_id
            return redirect(url_for('index'))
        flash('Invalid username or password')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))



@app.route('/customers')
@login_required
def customers():
    page = request.args.get('page', 1, type=int)
    customers = Customer.query.paginate(page=page, per_page=6)
    return render_template('customers.html', customers=customers)



@app.route('/add_customer', methods=['GET', 'POST'])
@login_required
def add_customer():
    if request.method == 'POST':
        name = request.form['name']
        age = request.form['age']
        gender = request.form['gender']
        email = request.form['email']
        phone = request.form['phone']
        address = request.form['address']
        new_customer = Customer(name=name, age=age, gender=gender, email=email, phone=phone, address=address)
        db.session.add(new_customer)
        db.session.commit()
        return redirect(url_for('customers'))
    return render_template('add_customer.html')

@app.route('/update_customer/<int:id>', methods=['GET', 'POST'])
@login_required
def update_customer(id):
    customer = Customer.query.get_or_404(id)
    if request.method == 'POST':
        customer.name = request.form['name']
        customer.age = request.form['age']
        customer.gender = request.form['gender']
        customer.email = request.form['email']
        customer.phone = request.form['phone']
        customer.address = request.form['address']
        db.session.commit()
        return redirect(url_for('customers'))
    return render_template('update_customer.html', customer=customer)

@app.route('/delete_customer/<int:id>')
@login_required
def delete_customer(id):
    customer = Customer.query.get_or_404(id)
    db.session.delete(customer)
    db.session.commit()
    return redirect(url_for('customers'))

@app.route('/drugs')
@login_required
def drugs():
    # Get the current page number from the URL, defaulting to 1 if not provided
    page = request.args.get('page', 1, type=int)
    
    # Paginate the query, returning 10 items per page
    drugs = Drug.query.paginate(page=page, per_page=5)
    
    # Pass the paginated drugs object to the template
    return render_template('drugs.html', drugs=drugs)

@app.route('/add_drug', methods=['GET', 'POST'])
@login_required
def add_drug():
    if request.method == 'POST':
        Dr_Name = request.form['Dr_Name']
        Dr_DOM = request.form['Dr_DOM']
        Dr_DOE = request.form['Dr_DOE']
        Dr_MRP = request.form['Dr_MRP']
        Dr_Cost_Price = request.form['Dr_Cost_Price']
        Dr_Type = request.form['Dr_Type']
        Dr_Use = request.form['Dr_Use']
        Dr_Quantity = request.form['Dr_Quantity']
        D_ID = request.form['D_ID']
        U_ID = request.form['U_ID']
        new_drug = Drug(Dr_Name=Dr_Name, Dr_DOM=Dr_DOM, Dr_DOE=Dr_DOE, Dr_MRP=Dr_MRP, 
                        Dr_Cost_Price=Dr_Cost_Price, Dr_Type=Dr_Type, Dr_Use=Dr_Use, 
                        Dr_Quantity=Dr_Quantity, D_ID=D_ID, U_ID=U_ID)
        db.session.add(new_drug)
        db.session.commit()
        return redirect(url_for('drugs'))
    return render_template('add_drug.html')

@app.route('/update_drug/<int:id>', methods=['GET', 'POST'])
@login_required
def update_drug(id):
    drug = Drug.query.get_or_404(id)
    if request.method == 'POST':
        drug.Dr_Name = request.form['Dr_Name']
        drug.Dr_DOM = request.form['Dr_DOM']
        drug.Dr_DOE = request.form['Dr_DOE']
        drug.Dr_MRP = request.form['Dr_MRP']
        drug.Dr_Cost_Price = request.form['Dr_Cost_Price']
        drug.Dr_Type = request.form['Dr_Type']
        drug.Dr_Use = request.form['Dr_Use']
        drug.Dr_Quantity = request.form['Dr_Quantity']
        drug.D_ID = request.form['D_ID']
        drug.U_ID = request.form['U_ID']
        db.session.commit()
        return redirect(url_for('drugs'))
    return render_template('update_drug.html', drug=drug)

@app.route('/delete_drug/<int:id>')
@login_required
def delete_drug(id):
    drug = Drug.query.get_or_404(id)
    db.session.delete(drug)
    db.session.commit()
    return redirect(url_for('drugs'))

@app.route('/distributors')
@login_required
def distributors():
    distributor_list = Distributor.query.all()  # Fetch all distributors from the database
    return render_template('distributors.html', distributors=distributor_list)

@app.route('/add_distributor', methods=['GET', 'POST'])
@login_required
def add_distributor():
    if request.method == 'POST':
        D_Name = request.form['D_Name']
        D_Phone_no = request.form['D_Phone_no']
        D_Address = request.form['D_Address']
        new_distributor = Distributor(D_Name=D_Name, D_Phone_no=D_Phone_no, D_Address=D_Address)
        db.session.add(new_distributor)
        db.session.commit()
        return redirect(url_for('distributors'))  # Updated to 'distributors'
    return render_template('add_distributor.html')


@app.route('/update_distributor/<int:id>', methods=['GET', 'POST'])
@login_required
def update_distributor(id):
    distributor = Distributor.query.get_or_404(id)
    if request.method == 'POST':
        distributor.D_Name = request.form['D_Name']
        distributor.D_Phone_no = request.form['D_Phone_no']
        distributor.D_Address = request.form['D_Address']
        db.session.commit()
        return redirect(url_for('distributors'))  # Updated to 'distributors'
    return render_template('update_distributor.html', distributor=distributor)


@app.route('/delete_distributor/<int:id>')
@login_required
def delete_distributor(id):
    distributor = Distributor.query.get_or_404(id)
    db.session.delete(distributor)
    db.session.commit()
    return redirect(url_for('distributors'))  # Updated to 'distributors'





if __name__ == '__main__':
    app.run(debug=True)

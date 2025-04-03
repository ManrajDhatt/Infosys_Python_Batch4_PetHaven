from unittest import result
import uuid, secrets
from flask import Flask, abort, jsonify, render_template, redirect, session, url_for, send_file,flash, request
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from sqlalchemy import func, text
from models import (
    Result, db, User, Event, Registration,
    Dogs, Cart, CartItem, Order, OrderDetail,
    Service, ServiceProvider, ServiceProviderStatus,
    PaymentStatus, Booking, BookingDetail,
    insert_initial_data, insert_seed_data,
    get_revenue_data, get_booking_data, 
    fetch_recent_bookings, generate_revenue_graph, 
    generate_booking_trend, get_stacked_revenue_data
)
from forms import RegistrationForm, LoginForm, EventForm, RegistrationEventForm, ResultForm
from config import Config
import os
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from collections import defaultdict
from sqlalchemy.sql import func
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from flask_mail import Message,Mail
from send_email import send_confirmation_email, send_update_email, send_email, send_password_reset_email
from dotenv import load_dotenv
import cloudinary.uploader
from flask_migrate import Migrate
from scheduler import start_scheduler
# from app import db
from datetime import datetime, timezone
# from app import db
from datetime import datetime, timezone, time


load_dotenv()  # Load environment variables from .env file



app = Flask(__name__)
app.config.from_object(Config)


UPLOAD_FOLDER = 'static/images'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER  

db.init_app(app)

bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

mail=Mail(app)
migrate = Migrate(app, db)

# Create database tables
with app.app_context():
    db.create_all()
    insert_initial_data()  #SEED THE DATABASE
    insert_seed_data()    # SEED THE DATABASE

 
    # Hardcoded Admin
    # ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD") 
    # hashed_pw = bcrypt.generate_password_hash(ADMIN_PASSWORD).decode('utf-8')
    registrations = Registration.query.filter(Registration.timestamp == None).all()

    for reg in registrations:
        reg.timestamp = datetime.now(timezone.utc)

    db.session.commit()
    # if not User.query.filter_by(email="admin@example.com").first():
    #     admin = User(username="admin", email="admin@example.com", password=hashed_pw, is_admin=True)
    #     db.session.add(admin)
    #     db.session.commit()



@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

def is_admin():
    return current_user.is_authenticated and current_user.user_type is None
def is_petOwner():
    return current_user.is_authenticated and current_user.user_type == 'Pet Owner'
def is_serviceProvider():
    return current_user.is_authenticated and current_user.user_type == 'Service Provider'

@app.route('/register', methods=['POST'])
def register():
    try:
        print(request.form,1234567)
        
        
        user_name = request.form['username']
        email = request.form['email']
        password = generate_password_hash(request.form['password'])
        user_type = request.form['user_type']

        existing_user = User.query.filter_by(email_id=email).first()
        if existing_user:
            return jsonify({"message": "Email already registered!", "status": "error"}), 400  # Return JSON

        # Create new user
        new_user = User(user_name=user_name, email_id=email, password=password, user_type=user_type)
        db.session.add(new_user)
        db.session.commit()

        send_email("Welcome to PetHaven", email, f"Hello {user_name}, your registration was successful!")

        if user_type == 'Service Provider':
            uploaded_file = request.files.get('document_folder') 
            if uploaded_file and uploaded_file.filename != '':
                filename = secure_filename(uploaded_file.filename)  # Secure the filename
                user_folder = os.path.join(app.config['UPLOAD_FOLDER'], email)
        
                if not os.path.exists(user_folder):
                    os.makedirs(user_folder)  # Create user-specific directory
        
                file_path = os.path.join(user_folder, filename)
                uploaded_file.save(file_path)  # Save the file to static/uploads/<email>/

            service_provider = ServiceProvider(
                user_id= new_user.user_id,
                service_name = request.form['service_id'],
                name=request.form['username'],
                address=request.form['state'] + ',' + request.form['city'],
                hourly_rate=request.form['hourly_rate'],
                experience=request.form['experience'],
                description=request.form['description'],
                document_folder=os.path.join(app.config['UPLOAD_FOLDER'], email),
                status='PENDING'
            )
            
            db.session.add(service_provider)
            db.session.commit()

            # send_email("Service Provider Registration Pending", email, "Your registration is pending admin approval.")
        
        return jsonify({"message": "Registration successful!", "status": "success", "redirect": url_for('reg') }), 200  # Return success JSON

    except Exception as e:
        return jsonify({"message": str(e), "status": "error"}), 500  # Handle errors



@app.route('/check_admin')
def check_admin():
    admin = User.query.filter_by(user_name="Admin@123").first()
    if admin:
        return f"Admin exists: {admin.user_name}, {admin.email_id}, user_type: {admin.user_type}"
    else:
        return "Admin does not exist"


# TEAM - 3
# @app.route('/register', methods=['GET', 'POST'])
# def register():
#     form = RegistrationForm()
#     if form.validate_on_submit():
#         existing_user = User.query.filter_by(email_id=form.email.data).first()  #Check if email exists
#         if existing_user:
#             flash('Email is already registered. Please log in.', 'danger')
#             return redirect(url_for('login'))  # Redirect to login if email exists
        
#         hashed_pw = generate_password_hash(form.password.data,method='scrypt')
#         user = User(
#             user_name=form.username.data,
#             email_id=form.email.data,
#             password=hashed_pw,
#           # **************NEED TO BE UPDATED**********
#             user_type='pet_owner'
#             )
#         db.session.add(user)
#         db.session.commit()
#         flash('Account created! You can now login.', 'success')
#         return redirect(url_for('login'))
#     return render_template('register.html', form=form)



# TEAM - 3
# @app.route('/', methods=['GET', 'POST'])
# def home():
#     return render_template('index.html')

@app.route('/', methods=['GET'])
def home():
    # return render_template('Auth.html')
    return render_template('index.html')



# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     if current_user.is_authenticated:  
#         return redirect(url_for('dashboard'))
    
#     form = LoginForm()
#     if form.validate_on_submit():
#         user = User.query.filter_by(email_id=form.email.data).first()
#         if user and check_password_hash(user.password, form.password.data):
#             login_user(user)
#             return redirect(url_for('dashboard'))
#         flash('Login failed. Check credentials.', 'danger')
#     return render_template('login.html', form=form)


@app.route('/reg')
def reg():
    return render_template('reg.html')


@app.route('/login', methods=['GET','POST'])
def login():

    session.pop('_flashes', None)

    email = request.form.get('email')
    password = request.form.get('password')

    user = User.query.filter_by(email_id=email).first()
    print(12345667)
    if user and check_password_hash(user.password, password):
        login_user(user)
        session['user_id'] = user.user_id
        session['user_type'] = user.user_type

        # send_email("Login Alert", email, f"Hello {user.user_name}, a login attempt was made on your account.")

        # Determine redirection URL based on user type
        if user.user_type == 'Pet Owner':
            # dashboard_url = url_for('customer_dashboard')
            dashboard_url = url_for('dashboard')
        elif user.user_type == 'Service Provider':
            dashboard_url = url_for('dashboard')
            
            # dashboard_url = url_for('service_provider_dashboard')
        else:
            dashboard_url = url_for('admin_dashboard')

            # dashboard_url = url_for('admin_dashboard')

        return jsonify({
            "status": "success",
            "message": "Login successful!",
            "redirect": dashboard_url
        }), 200
    else:
        return jsonify({
            "status": "error",
            "message": "Invalid credentials! Please try again."
        }), 401



@app.route('/admin_login', methods=['GET','POST'])
def admin_login():
    if '_flashes' in session:
        del session['_flashes']
    
    print("Login attempt received")
    print("Form data:", request.form)
    
    username = request.form.get('username')
    password = request.form.get('password')
    
    print(f"Attempting login with: {username}")
    
    admin = User.query.filter_by(user_name=username, user_type=None).first()
    print("Admin found:", admin)
    
    if admin and check_password_hash(admin.password, password):
        login_user(admin)
        session['user_id'] = admin.user_id
        session['user_type'] = 'Admin'
        
        return jsonify({
            "status": "success",
            "message": "Admin login successful!",
            "redirect": url_for('admin_dashboard')
        })
    
    return jsonify({
        "status": "error",
        "message": f"Invalid admin credentials! Username: {username}"
    })

#  ---------------------- RESET PASSWORD FEATURE ---------------------- #
def generate_reset_token():
    return secrets.token_urlsafe(20)

@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email']
        user = User.query.filter_by(email_id=email).first()
        
        if user:
            reset_token = generate_reset_token()
            session[f'reset_token_{email}'] = reset_token  # Store the token temporarily
            reset_link = url_for('reset_password', email=email, token=reset_token, _external=True)
            print(reset_link,123890)
            # Send reset email
            msg = Message("Password Reset Request", sender="your_email@gmail.com", recipients=[email])
            msg.body = f"Click the link below to reset your password: {reset_link}"
            mail.send(msg)
            
            flash("A password reset link has been sent to your email.")
        else:
            flash("Email not found!")
    
    return render_template('forgot_password.html')

@app.route('/reset_password/<email>/<token>', methods=['GET', 'POST'])
def reset_password(email, token):
    stored_token = session.get(f'reset_token_{email}')
    
    if stored_token != token:
        flash("Invalid or expired reset link!")
        return redirect(url_for('home'))
    
    user = User.query.filter_by(email_id=email).first()
    if not user:
        flash("Invalid reset request!")
        return redirect(url_for('home'))
    
    if request.method == 'POST':
        new_password = generate_password_hash(request.form['new_password'])
        user.password = new_password
        db.session.commit()
        session.pop(f'reset_token_{email}', None)  # Remove the token after use
        flash("Password reset successful! You can now log in.")
        return redirect(url_for('home'))
    
    return render_template('reset_password.html', email=email, token=token)

# ---------------------- ADMIN DASHBOARD ---------------------- #

@app.route('/admin/manage_service_providers')
def manage_service_providers():
    """ Show all pending service providers for admin approval """
    service_providers = ServiceProvider.query.filter_by(status='PENDING').all()
    for service_provider in service_providers:
        print(service_provider.documents)
    return render_template('manage_sp.html', service_providers=service_providers)
@app.route('/approve_service_provider/<sp_id>', methods=['POST'])
def approve_service_provider(sp_id):
    """ Approve a service provider and redirect them to their dashboard """
    # Use filter_by instead of get() for composite primary keys
    service_provider = ServiceProvider.query.filter_by(service_id=sp_id).first()
    
    if service_provider:
        from models import ServiceProviderStatus
        service_provider.status = ServiceProviderStatus.ACCEPTED
        db.session.commit()
        flash("Service Provider approved successfully!", "success")
        return '', 200
    return '', 400

@app.route('/reject_service_provider/<sp_id>', methods=['POST'])
def reject_service_provider(sp_id):
    """ Reject a service provider and redirect them to the Get Started page """
    # Use filter_by instead of get() for composite primary keys
    service_provider = ServiceProvider.query.filter_by(service_id=sp_id).first()
    
    if service_provider:
        from models import ServiceProviderStatus
        service_provider.status = ServiceProviderStatus.REJECTED
        db.session.commit()
        flash("Service Provider rejected!", "danger")
        return '', 200
    return '', 400

# @app.route('/customer_dashboard')
# def customer_dashboard():
#     return render_template('customer_dashboard.html')

@app.route('/service_provider_dashboard')
def service_provider_dashboard():
    return render_template('service_provider_dashboard.html')

# @app.route('/admin_dashboard')
# def admin_dashboard():
#     return render_template('admin_dashboard.html')

@app.route('/logout')
def logout():
    logout_user()
    session.clear()
    flash("Logged out successfully!")
    return redirect(url_for('home'))


@app.route('/manage_sp')
def manage_sp():
    service_providers = ServiceProvider.query.all()  # Fetch all service providers
    print(service_providers)
    # service_providers = ServiceProvider.query.filter_by(status='PENDING').all()
    return render_template('manage_sp.html', service_providers=service_providers)


@app.route('/competitions')
@login_required
def competitions():
    today = datetime.today().date()
    upcoming_events = Event.query.filter(Event.date >= today).all()

    # if current_user.is_admin:
    if is_admin():
        return render_template('admin_dashboard(team3).html', events=upcoming_events)
    
    # events = Event.query.all()
    # registered_events = Registration.query.filter_by(user_id=current_user.id).all()
    
    # registered_event_details = []
    # for reg in registered_events:
    #     event = Event.query.get(reg.event_id)
    #     if event:
    #         registered_event_details.append(event)
    registered_events = Registration.query.filter_by(user_id=current_user.user_id).all()
    registered_event_details = [Event.query.get(reg.event_id) for reg in registered_events]
    
    return render_template('user_dashboard.html', events=upcoming_events, registered_events=registered_event_details)


@app.route('/dashboard')
@login_required
def dashboard():
    return render_template("discover_team2.html", events=Event.query.all())


@app.route('/add_event', methods=['GET', 'POST'])
@login_required
def add_event():
    # if not current_user.is_admin:.
    if not is_admin():
        return redirect(url_for('competitions'))
    
    form = EventForm()  
    if form.validate_on_submit():
        # image_filename = "default.png"
        image_url="https://res.cloudinary.com/diyvaqnyj/image/upload/v1740916253/default_pgbdyf.png"

        if form.image.data:
            image_filename = secure_filename(form.image.data.filename)
            # Upload to Cloudinary
            upload_result = cloudinary.uploader.upload(form.image.data, folder="event_images")
            image_url = upload_result["secure_url"]  # Get Cloudinary image URL



        new_event = Event(
            title=form.title.data,
            description=form.description.data,
            date=form.date.data,
            location=form.location.data,
            prizes=form.prizes.data,
            eligibility=form.eligibility.data,
            fee=form.fee.data,
            image_filename=image_url 
        )
        db.session.add(new_event)
        db.session.commit()
        flash('Event added successfully!', 'success')
        return redirect(url_for('admin_dashboard'))  #Redirect after adding event
    return render_template('add_event.html', form=form)
    
    

@app.route('/register/<string:event_id>', methods=['GET', 'POST'])
@login_required
def register_event(event_id):
    if is_admin():  # Prevent admins from registering
        flash('Admins cannot register for events!', 'danger')
        return redirect(url_for('competitions'))
    
    existing_registration = Registration.query.filter_by(user_id=current_user.user_id, event_id=event_id).first()
    if existing_registration:
        flash('You have already registered for this event!', 'warning')
        return redirect(url_for('competitions'))

    event = Event.query.get_or_404(event_id)
    form = RegistrationEventForm()

    if form.validate_on_submit():
        registration = Registration(
            user_id=current_user.user_id,
            event_id=event_id,
            pet_name=form.pet_name.data,
            pet_type=form.pet_type.data,
            pet_age=form.pet_age.data,
            paid=False  # Assuming payment is done later
        )
        db.session.add(registration)
        db.session.commit()
        send_confirmation_email(current_user.email_id, current_user.user_name, event, form.pet_name.data, form.pet_type.data, form.pet_age.data)

        flash('Successfully registered!', 'success')
        return redirect(url_for('competitions'))

    return render_template('register_event.html', form=form, event=event)



@app.route('/admin_dashboard')
@login_required
def admin_dashboard():
    if not is_admin():
        return redirect(url_for('dashboard'))  # Restrict non-admin users
    events = Event.query.all()  #  Fetch all events
    return render_template('admin_dashboard(team3).html', events=events)

@app.route('/registrations')
@login_required
def registrations():
    registered_events = db.session.query(Registration, Event).join(Event, Registration.event_id == Event.id).filter(Registration.user_id == current_user.user_id).all()
    # Convert event dates to datetime objects for comparison
    current_date = datetime.now().date()
    processed_events = []
    for reg, event in registered_events:
        event_date = datetime.strptime(event.date, '%Y-%m-%d').date()
        can_edit = event_date > current_date
        processed_events.append((reg, event, can_edit))
    
    return render_template("registrations.html", registered_events=processed_events)

@app.route('/edit_registration/<string:registration_id>', methods=['GET', 'POST'])
@login_required
def edit_registration(registration_id):
    registration = Registration.query.get_or_404(registration_id)
    event = Event.query.get_or_404(registration.event_id)
    
    # Check if the registration belongs to the current user
    if registration.user_id != current_user.user_id:
        flash('You are not authorized to edit this registration.', 'danger')
        return redirect(url_for('registrations'))
    
    # Check if the event date has passed
    event_date = datetime.strptime(event.date, '%Y-%m-%d').date()
    if event_date < datetime.now().date():
        flash('Cannot edit registration for past events.', 'warning')
        return redirect(url_for('registrations'))
    
    form = RegistrationEventForm()
    
    if form.validate_on_submit():
        registration.pet_name = form.pet_name.data
        registration.pet_type = form.pet_type.data
        registration.pet_age = form.pet_age.data
        
        try:
            db.session.commit()
            flash('Registration details updated successfully!', 'success')
            return redirect(url_for('registrations'))
        except:
            db.session.rollback()
            flash('An error occurred while updating the registration.', 'danger')
    
    # Pre-fill form with current values
    if request.method == 'GET':
        form.pet_name.data = registration.pet_name
        form.pet_type.data = registration.pet_type
        form.pet_age.data = registration.pet_age
    
    return render_template('edit_registration.html', form=form, registration=registration, event=event)

@app.route('/settings')
@login_required
def settings():
    return render_template("settings.html")


@app.route('/edit_event/<string:event_id>', methods=['GET', 'POST'])
@login_required
def edit_event(event_id):
    if not current_user.is_admin:
        flash("You are not authorized to edit events.", "danger")
        return redirect(url_for('dashboard'))

    event = Event.query.get_or_404(event_id)
    form = EventForm(obj=event)  # Pre-fill form with event details

    if form.validate_on_submit():
        event.title = form.title.data
        event.description = form.description.data
        event.date = form.date.data
        event.location = form.location.data
        event.prizes = form.prizes.data
        event.eligibility = form.eligibility.data
        event.fee = form.fee.data

        # Handle image upload
        if form.image.data:
            image_filename = secure_filename(form.image.data.filename)
            upload_result = cloudinary.uploader.upload(form.image.data, folder="event_images")
            event.image_filename = upload_result["secure_url"]  
        
        try:
            db.session.commit()
            flash("Event updated successfully!", "success")

            # Send notifications if the checkbox is selected
            if 'send_notifications' in request.form:
                registrations = Registration.query.filter_by(event_id=event.id).all()
                for reg in registrations:
                    send_update_email(reg.user.email_id, reg.user.user_name, event)

            return redirect(url_for('admin_dashboard'))
        except:
            db.session.rollback()
            flash("Error updating event.", "danger")

    return render_template('edit_event.html', form=form, event=event)


@app.route('/all-registrations')
@login_required
def all_registrations():
    if not current_user.is_admin:
        flash("Unauthorized access!", "danger")
        return redirect(url_for('home'))

    registrations = Registration.query.all()  # Fetch all registrations
    return render_template('all_registrations.html', registrations=registrations)



@app.route('/pay/<string:registration_id>', methods=['GET', 'POST'])
@login_required
def pay_fee(registration_id):
    registration = Registration.query.get_or_404(registration_id)

    if registration.user_id != current_user.user_id:
        abort(403)  # Prevent unauthorized access

    registration.paid = True
    db.session.commit()

    flash("Payment successful!", "success")
    return redirect(url_for('registrations'))

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, (user_id))

@app.route('/verify_payment/<string:registration_id>', methods=['GET', 'POST'])
@login_required
def verify_payment(registration_id):
    if not current_user.is_admin:
        flash("Unauthorized access!", "danger")
        return redirect(url_for('home'))

    registration = Registration.query.get_or_404(registration_id)
    registration.paid = True
    db.session.commit()

    flash("Payment verified successfully!", "success")
    return redirect(url_for('all_registrations'))

@app.route('/delete_registration/<string:registration_id>', methods=['GET', 'POST'])
@login_required
def delete_registration(registration_id):
    if not current_user.is_admin:
        flash("Unauthorized access!", "danger")
        return redirect(url_for('home'))

    registration = Registration.query.get_or_404(registration_id)
    db.session.delete(registration)
    db.session.commit()

    flash("Registration deleted successfully!", "success")
    return redirect(url_for('all_registrations'))




@app.route('/admin/manage_results')
@login_required
def manage_results():
    if not current_user.is_admin:
        flash("Access denied! Only admins can manage results.", "danger")
        return redirect(url_for("home"))

    today = datetime.today().date()
    past_events = Event.query.filter(Event.date < today).all()

     # Check if each event has results
    for event in past_events:
        event.has_result = Result.query.join(Registration).filter(Registration.event_id == event.id).first() is not None


    return render_template('manage_results.html', past_events=past_events)



@app.route('/event/<string:event_id>/add_result', methods=['GET', 'POST'])
@login_required
def add_result(event_id):
    if not current_user.is_admin:
        flash("Access denied.", "danger")
        return redirect(url_for('home'))

    event = Event.query.get_or_404(event_id)
    registrations = Registration.query.filter_by(event_id=event_id).all()

    if request.method == 'POST':
        for reg in registrations:
            reg_id =reg.id
            attended = request.form.get(f'attended_{reg_id}') == "1"  # Checkbox handling
            position = request.form.get(f'position_{reg_id}', None) if attended else "-"
            points = request.form.get(f'points_{reg_id}', 0) if attended else "-"
            remarks = request.form.get(f'remarks_{reg_id}', "") if attended else "Absent - We missed you! Hope to see you next time! 😊"

            position = int(position) if attended and position else None
            points = float(points) if attended and points else None

            new_result = Result(
                registration_id=reg_id,
                attended=attended,
                position=position,
                points=points,
                remarks=remarks
            )
            db.session.add(new_result)

        db.session.commit()
        flash("Results added successfully!", "success")

        return redirect(url_for('view_results', event_id=event_id))

    return render_template('add_result.html', event=event, registrations=registrations)

@app.route('/event/<string:event_id>/update_result', methods=['GET', 'POST'])
@login_required
def update_result(event_id):
    if not current_user.is_admin:
        flash("Access denied.", "danger")
        return redirect(url_for('home'))

    event = Event.query.get_or_404(event_id)
    registrations = db.session.query(Registration, User).join(User, Registration.user_id == User.user_id).filter(Registration.event_id == event_id).all()
    results = {res.registration_id: res for res in Result.query.filter(Result.registration_id.in_([r[0].id for r in registrations])).all()}

    if not results:
        flash("No results found! Please add results first.", "warning")
        return redirect(url_for('add_result', event_id=event_id))

    if request.method == 'POST':
        for reg, user in registrations:
            reg_id = reg.id

            # Fix checkbox issue (it returns 'on' when checked)
            attended = request.form.get(f'attended_{reg_id}') == "on"

            # Fix handling of empty values
            position = request.form.get(f'position_{reg_id}', None)
            points = request.form.get(f'points_{reg_id}', None)
            remarks = request.form.get(f'remarks_{reg_id}', "").strip()

            # Convert types properly
            position = int(position) if attended and position and position.isdigit() else None
            try:
                points = float(points) if attended and points and points.replace(".", "", 1).isdigit() else None
            except ValueError:
                points = None

            if not attended:
                remarks = "Absent - We missed you! Hope to see you next time! 😊"

            existing_result = results.get(reg_id)
            if existing_result:
                print(f"Updating result for {reg_id}")
                print(f"  Before update: attended={existing_result.attended}, position={existing_result.position}, points={existing_result.points}")

                existing_result.attended = attended
                existing_result.position = position
                existing_result.points = points
                existing_result.remarks = remarks

                print(f"  After update: attended={existing_result.attended}, position={existing_result.position}, points={existing_result.points}")

        db.session.flush()  # Ensure SQLAlchemy detects changes
        db.session.commit()

        flash("Results updated successfully!", "success")
        return redirect(url_for('view_results', event_id=event_id))

    return render_template('update_result.html', event=event, registrations=registrations, results=results)



@app.route('/event/<string:event_id>/results')
@login_required
def view_results(event_id):
    if not current_user.is_admin:
        flash("Access denied.", "danger")
        return redirect(url_for('home'))

    event = Event.query.get_or_404(event_id)
    results = Result.query.join(Registration).filter(Registration.event_id== event_id).all()

    return render_template('view_results.html', event=event, results=results)




@app.route("/user/results")
@login_required
def user_results():
    user_id = current_user.user_id

    # Get all past events and their results for the user
    past_results = (
        db.session.query(
            Event.title,
            Event.date,
            Result.position,
            Result.attended,
            Result.remarks
        )
        .join(Registration, Event.id == Registration.event_id)
        .join(Result, Registration.id == Result.registration_id)
        .filter(Registration.user_id == user_id)
        .all()
    )

    # Convert event date (string) to datetime before passing it to the template
    formatted_results = []
    for result in past_results:
        try:
            event_date = datetime.strptime(result.date, "%Y-%m-%d")  # Change format as needed
        except ValueError:
            event_date = result.date  # Keep it as-is if conversion fails
        
        formatted_results.append({
            "title": result.title,
            "date": event_date,  
            "position": result.position,
            "attended": result.attended,
            "remarks": result.remarks,
        })

    return render_template("user_results.html", past_results=formatted_results)


# TEAM - 3
# @app.route('/logout')
# @login_required
# def logout():
#     logout_user()
#     # flash('you have been logged out.','info')
#     return redirect(url_for('login'))


@app.route('/admin/event_statistics')
@login_required
def event_statistics():
    if not current_user.is_admin:
        flash("Access denied.", "danger")
        return redirect(url_for('home'))

    # Fetch all events
    events = Event.query.all()
    event_stats = []

    # Overall Stats
    total_users = User.query.count()
    total_events = len(events)
    total_participants = Registration.query.count()
    total_revenue = db.session.query(func.sum(Event.fee)).join(Registration).scalar() or 0
    attendance_rate = db.session.query(func.avg(Result.attended)).scalar() * 100 if Result.query.count() > 0 else 0

    # Most Active Users
    most_active_users = (
        db.session.query(User.user_name, func.count(Registration.id).label("event_count"))
        .join(Registration)
        .group_by(User.user_id)
        .order_by(func.count(Registration.id).desc())
        .limit(5)
        .all()
    )

    # Event-wise Stats
    for event in events:
        total_participants = Registration.query.filter_by(event_id=event.id).count()
        total_results = Result.query.join(Registration).filter(Registration.event_id == event.id).all()
        total_fees_collected = total_participants * event.fee

        # Fetch top 3 winners
        winners = [
        {"username": winner.user_name, "position": winner.position} for winner in db.session.query(User.user_name, Result.position)
        .join(Registration, Registration.id == Result.registration_id)
        .join(User, Registration.user_id == User.user_id)
        .filter(Registration.event_id == event.id, Result.position.isnot(None))
        .order_by(Result.position.asc())
        .limit(3)
        .all()
    ]


        avg_points = db.session.query(func.avg(Result.points)).join(Registration).filter(Registration.event_id == event.id).scalar() or 0
        max_points = db.session.query(func.max(Result.points)).join(Registration).filter(Registration.event_id == event.id).scalar() or 0
        min_points = db.session.query(func.min(Result.points)).join(Registration).filter(Registration.event_id == event.id).scalar() or 0

        event_stats.append({
            "event_title": event.title,
            "total_participants": total_participants,
            "total_fees_collected": total_fees_collected,
            "winners": winners,
            "avg_points": round(avg_points, 2),
            "max_points": max_points,
            "min_points": min_points,
        })

    return render_template('event_statistics.html', event_stats=event_stats, 
                           total_users=total_users, total_events=total_events, 
                           total_participants=total_participants, total_revenue=total_revenue,
                           attendance_rate=round(attendance_rate, 2), 
                           most_active_users=most_active_users)




#################################################  TEAM - 2 ROUTES GOES HERE ####################################################################

# ********************************* Admin Dashboard Route *********************************
@app.route("/admin")
@login_required
def admin_dashboard_team2():
    if not current_user.is_admin:
        flash("Unauthorized access!", "danger")
        return redirect(url_for('home'))  
    return render_template("admin.html")

# ******************** Configuration for Image Uploads ********************
app.config["UPLOAD_FOLDER"] = "static/images"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ************************************* Route to Add a New Dog **********************************************
@app.route("/admin/dogs/add", methods=["POST"])
@login_required
def add_dog():
    if not current_user.is_admin:
        flash("Unauthorized access!", "danger")
        return redirect(url_for('home'))
    data = request.form
    name = data.get("name")
    breed = data.get("breed")
    age = data.get("age")
    price = data.get("price")
    vaccinated = data.get("vaccinated", "No")  # Default to 'No'
    description = data.get("description")

    # Fix: Check if all required fields are present
    if not all([name, breed, age, price, description]):
        return jsonify({"error": "Missing required fields"}), 400

    # Fix: Convert price to integer
    try:
        price = int(price)
    except ValueError:
        return jsonify({"error": "Invalid price value"}), 400

    # Fix: Ensure images directory exists
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    # Fix: Handle Image Upload
    image_filename = "default.jpg"
    image = request.files.get("image")

    if image and allowed_file(image.filename):
        image_filename = secure_filename(image.filename)
        image_path = os.path.join(app.config["UPLOAD_FOLDER"], image_filename)
        image.save(image_path)

    # Fix: Store Dog in DB
    new_dog = Dogs(
        name=name,
        breed=breed,
        age=age,
        price=price,
        vaccinated=vaccinated,
        description=description,
        image=f"static/images/{image_filename}"
    )

    db.session.add(new_dog)
    db.session.commit()

    return jsonify({"message": "Dog added successfully!", "dog_id": new_dog.dog_id})


# ******************** Route to Delete a Dog ********************
@app.route("/admin/dogs/delete/<string:dog_id>", methods=["DELETE"])
@login_required
def delete_dog(dog_id):
    if not current_user.is_admin:
        flash("Unauthorized access!", "danger")
        return redirect(url_for('home'))
    dog = Dogs.query.get(dog_id)
    if not dog:
        return jsonify({"error": "Dog not found"}), 404

    # Check if image exists before deleting
    if dog.image != "static/images/default.jpg" and os.path.exists(dog.image):
        try:
            os.remove(dog.image)
        except FileNotFoundError:
            print(f"Warning: File {dog.image} not found")  # Debugging info

    db.session.delete(dog)
    db.session.commit()

    return jsonify({"message": "Dog deleted successfully!"})


# ******************** Route to Edit a Dog ********************
@app.route("/admin/dogs/edit/<string:dog_id>", methods=["POST"])
@login_required
def edit_dog(dog_id):
    if not current_user.is_admin:
        flash("Unauthorized access!", "danger")
        return redirect(url_for('home'))
    dog = Dogs.query.get(dog_id)
    if not dog:
        return jsonify({"error": "Dog not found"}), 404

    # Handle JSON data properly
    if request.is_json:
        data = request.get_json()
        dog.name = data.get("name", dog.name)
        dog.price = int(data.get("price", dog.price))  # Convert to int

    db.session.commit()
    return jsonify({"message": "Dog updated successfully!"})

#************************************** Individual Dog Display route ****************************************

@app.route('/dogs/<string:dog_id>', methods=['GET'])
def dog_details(dog_id):
    dog = Dogs.query.get(dog_id)
    if not dog:
        return jsonify({"error": "Dog not found"}), 404
    return jsonify({
    "id": dog.dog_id,
    "name": dog.name,
    "breed": dog.breed,
    "age": dog.age,
    "price": dog.price,
    "image": dog.image,
    "vaccinated": dog.vaccinated,
    "description": dog.description
    })

#*************************************** routes for fectching all dog details *******************************
@app.route('/api/dogs', methods=['GET'])
def get_dogs():
    dogs = Dogs.query.all()
    dogs_data = [
        {
            "id": dog.dog_id,
            "name": dog.name,
            "breed": dog.breed,
            "age": dog.age,
            "price": dog.price,
            "image": dog.image,
            "vaccinated": dog.vaccinated,
            "description": dog.description
        }
        for dog in dogs
    ]
    return jsonify(dogs_data)

#******************************* Enable server-side sessions for cart storage *******************************
@app.route("/cart")
def cart_page():
    if "user_id" not in session:
        return redirect(url_for("login"))  # Redirect if not logged in

    user_id = session["user_id"]
    cart = Cart.query.filter_by(user_id=user_id).first()

    if not cart or not cart.cart_items:
        return render_template("cart.html", cart=[], total_price=0)

    # Fetch Dog Items in Cart
    cart_dogs = [
        {
            "id": item.dog.dog_id,
            "name": item.dog.name,
            "breed": item.dog.breed,
            "age": item.dog.age,
            "price": item.dog.price,
            "image": item.dog.image,
            "type": "dog"
        }
        for item in cart.cart_items if item.dog
    ]

    # Fetch Booking Items in Cart
    cart_bookings = [
        {
            "id": item.booking.booking_id,
            "service_name": item.booking.booking_details[0].service_name if item.booking.booking_details else "Unknown Service",  # Assuming Booking model has service_name
            "provider_id": item.booking.booking_details[0].service_id,     # Assuming provider details exist
            "date": item.booking.booking_date.strftime("%Y-%m-%d"),
            "duration": str(item.booking.duration),  
            "total_cost": item.booking.total_cost,
            "image": "static/images/istockphoto-1154973359-612x612.jpg",  # Placeholder image
            "type": "booking"
        }
        for item in cart.cart_items if item.booking
    ]

    print("Cart Dogs:", cart_dogs)
    print("Cart Bookings:", cart_bookings)
    # Combine dogs & bookings in one list
    cart_items = cart_dogs + cart_bookings
    total_price = sum(item["price"] if item["type"] == "dog" else item["total_cost"] for item in cart_items)

    return render_template("cart.html", cart=cart_items, total_price=total_price)

#**************************************** route for cart api ************************************************
@app.route("/api/cart", methods=["GET"])
def get_cart_items():
    """Fetch the current user's cart items from the database."""
    if "user_id" not in session:
        return jsonify({"error": "User not logged in"}), 401  # User must be logged in

    user_id = session["user_id"]
    cart = Cart.query.filter_by(user_id=user_id).first()

    if not cart or not cart.cart_items:
        return jsonify({"cart": []})  # Return empty list if no cart items

    # Fetch Dog Items in Order
    cart_dogs = [
        {
            "id": item.dog.dog_id,
            "name": item.dog.name,
            "breed": item.dog.breed,
            "age": item.dog.age,
            "price": item.dog.price,
            "image": item.dog.image,
            "type": "dog"
        }
        for item in cart.cart_items if item.dog
    ]

    # Fetch Booking Items in Order
    cart_bookings = [
        {
            "id": item.booking.booking_id,
            "service_name": item.booking.booking_details[0].service_name if item.booking.booking_details else "Unknown Service",
            "provider_id": item.booking.booking_details[0].service_id,
            "date": item.booking.booking_date.strftime("%Y-%m-%d"),
            "duration": item.booking.duration.strftime("%H:%M:%S"),
            "total_cost": item.booking.total_cost,
            "image": "static/images/istockphoto-1154973359-612x612.jpg",
            "type": "booking"
        }
        for item in cart.cart_items if item.booking
    ]

    for item in cart.cart_items:
        if item.booking:
            print(item.booking.duration.strftime("%H:%M:%S"))
    cart_items = cart_dogs + cart_bookings

    return jsonify({"cart": cart_items})

#******************************** route for add to cart functionality ***************************************
@app.route("/cart/add", methods=['POST'])
def add_to_cart():
    print("Add to cart request received")
    
    # Check if user is logged in
    if "user_id" not in session:
        print("User not logged in")
        return jsonify({"error": "User not logged in"}), 401

    try:
        data = request.get_json()
        if not data:
            print("No data provided in request")
            return jsonify({"error": "Invalid request - no data provided"}), 400
            
        dog_id = data.get("dog_id")
        booking_id = data.get("booking_id")
        user_id = session["user_id"]  # Fetch user_id from session

        print(f"Adding to cart - user_id: {user_id}, dog_id: {dog_id}, booking_id: {booking_id}")

        if not dog_id and not booking_id:
            print("No dog_id or booking_id provided")
            return jsonify({"error": "Invalid request - no dog_id or booking_id provided"}), 400

        # Check if the user already has a cart
        cart = Cart.query.filter_by(user_id=user_id).first()
        if not cart:
            print(f"Creating new cart for user {user_id}")
            cart = Cart(user_id=user_id, total_amount=0)
            db.session.add(cart)
            db.session.commit()
            print(f"Created new cart with ID: {cart.cart_id}")

        if dog_id:
            # Check if the dog is already in the cart
            cart_item = CartItem.query.filter_by(cart_id=cart.cart_id, dog_id=dog_id).first()
            if cart_item:
                print(f"Dog {dog_id} already in cart")
                return jsonify({"message": "Dog already in cart!", "cart_count": len(cart.cart_items)})

            # Check if dog exists
            dog = Dogs.query.get(dog_id)
            if not dog:
                print(f"Dog {dog_id} not found")
                return jsonify({"error": f"Dog with id {dog_id} not found"}), 404

            # Add dog to cart
            cart_item = CartItem(cart_id=cart.cart_id, dog_id=dog_id)
            db.session.add(cart_item)
            print(f"Added dog {dog_id} to cart {cart.cart_id}")

        elif booking_id:
            print(f"Processing booking_id: {booking_id}, type: {type(booking_id)}")
            
            # Verify booking exists
            booking = Booking.query.get(booking_id)
            if not booking:
                print(f"Booking {booking_id} not found")
                return jsonify({"error": f"Booking with id {booking_id} not found"}), 404
                
            # Check if booking belongs to user
            if booking.user_id != user_id:
                print(f"Booking {booking_id} belongs to user {booking.user_id}, not current user {user_id}")
                return jsonify({"error": "Unauthorized to add this booking to cart"}), 403
                
            # Check if the booking is already in the cart
            cart_item = CartItem.query.filter_by(cart_id=cart.cart_id, booking_id=booking_id).first()
            if cart_item:
                print(f"Booking {booking_id} already in cart")
                return jsonify({"message": "Booking already in cart!", "cart_count": len(cart.cart_items)})
                
            # Add booking to cart
            cart_item = CartItem(cart_id=cart.cart_id, booking_id=booking_id)
            db.session.add(cart_item)
            print(f"Added booking {booking_id} to cart {cart.cart_id}")
        
        db.session.commit()
        
        cart_count = len(cart.cart_items)
        print(f"Cart now has {cart_count} items")

        if dog_id:
            return jsonify({"message": "Dog added successfully!", "cart_count": cart_count})
        elif booking_id:
            return jsonify({"message": "Booking added successfully!", "cart_count": cart_count})
            
    except Exception as e:
        db.session.rollback()
        print(f"Error adding to cart: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"Failed to add to cart: {str(e)}"}), 500

#************************************ api for updating cart count ******************************************
@app.route("/api/cart_count", methods=["GET"])
def get_cart_count():
    if "user_id" not in session:
        return jsonify({"cart_count": 0})  # Return 0 if user not logged in

    user_id = session["user_id"]

    # Fetch the cart for the user
    cart = Cart.query.filter_by(user_id=user_id).first()

    if not cart:
        return jsonify({"cart_count": 0})  # No cart exists for the user

    cart_count = db.session.query(CartItem).filter_by(cart_id=cart.cart_id).count()
    
    return jsonify({"cart_count": cart_count})

#************************************* route for removing dog entry from the cart ***************************
@app.route("/cart/remove", methods=["POST"])
def remove_from_cart():
    if "user_id" not in session:
        return jsonify({"error": "User not logged in"}), 401

    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid request - no data provided"}), 400
            
        user_id = session["user_id"]

        # Find the user's cart
        cart = Cart.query.filter_by(user_id=user_id).first()
        if not cart:
            return jsonify({"error": "Cart not found"}), 404
        
        cart_item = None
        
        # Remove Dog from Cart
        if "dog_id" in data:
            dog_id = data["dog_id"]
            cart_item = CartItem.query.filter_by(cart_id=cart.cart_id, dog_id=dog_id).first()
            if cart_item:
                print(f"Removing dog {dog_id} from cart {cart.cart_id}")

        # Remove Booking from Cart
        elif "booking_id" in data:
            booking_id = data["booking_id"]
            cart_item = CartItem.query.filter_by(cart_id=cart.cart_id, booking_id=booking_id).first()
            if cart_item:
                print(f"Removing booking {booking_id} from cart {cart.cart_id}")
        else:
            return jsonify({"error": "Invalid request - no dog_id or booking_id provided"}), 400

        if not cart_item:
            return jsonify({"error": "Item not found in cart"}), 404
            
        # Delete the cart item
        db.session.delete(cart_item)
        db.session.commit()
        
        # Get updated cart items to calculate total
        cart_items = []
        
        # Fetch Dog Items in Cart
        for item in cart.cart_items:
            if item.dog:
                cart_items.append({"price": item.dog.price, "type": "dog"})
            elif item.booking:
                cart_items.append({"total_cost": item.booking.total_cost, "type": "booking"})
        
        # Recalculate total amount
        total_amount = sum(item["price"] if item["type"] == "dog" else item["total_cost"] for item in cart_items)
        cart.total_amount = total_amount  # Update cart total amount
        db.session.commit()
        
        cart_count = len(cart.cart_items)
        print(f"Cart now has {cart_count} items with total amount {total_amount}")

        return jsonify({
            "message": "Item removed from cart!",
            "cart_count": cart_count,
            "total_amount": total_amount
        })
    
    except Exception as e:
        db.session.rollback()
        print(f"Error removing from cart: {str(e)}")
        return jsonify({"error": f"Failed to remove from cart: {str(e)}"}), 500

#************************************* route for order summary ***********************************************

@app.route("/order")
def order_summary():
    if "user_id" not in session:
        return redirect(url_for("login"))  # Redirect if user not logged in

    user_id = session["user_id"]

    # Fetch the user's cart
    cart = Cart.query.filter_by(user_id=user_id).first()

    if not cart or not cart.cart_items:
        flash("Your cart is empty!", "warning")
        return redirect(url_for("cart_page"))  # Redirect to cart page if empty
    
    # Fetch Dog Items in Order
    cart_dogs = [
        {
            "id": item.dog.dog_id,
            "name": item.dog.name,
            "breed": item.dog.breed,
            "price": item.dog.price,
            "image": item.dog.image,
            "type": "dog"
        }
        for item in cart.cart_items if item.dog
    ]

    # Fetch Booking Items in Order
    cart_bookings = [
        {
            "id": item.booking.booking_id,
            "service_name": item.booking.booking_details[0].service_name if item.booking.booking_details else "Unknown Service",
            "provider_id": item.booking.booking_details[0].service_id,
            "date": item.booking.booking_date.strftime("%Y-%m-%d"),
            "duration": item.booking.duration.strftime("%H:%M:%S"),
            "total_cost": item.booking.total_cost,
            "image": "static/images/istockphoto-1154973359-612x612.jpg",
            "type": "booking"
        }
        for item in cart.cart_items if item.booking
    ]

    
    cart_items = cart_dogs + cart_bookings
    total_amount = sum(item["price"] if item["type"] == "dog" else item["total_cost"] for item in cart_items)  # Calculate total dynamically

    return render_template("order_summary.html", cart=cart_items, total_amount=total_amount)
    
#************************************* route for order confirm **********************************************

@app.route("/order-confirm", methods=["POST"])
def order_confirm():
    if "user_id" not in session:
        return jsonify({"error": "User not logged in"}), 401

    # Ensure request is JSON
    if not request.is_json:
        return jsonify({"error": "Invalid Content-Type. Expected application/json"}), 415

    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid JSON data"}), 400

    try:
        address = f"{data.get('address')}, {data.get('city')}, {data.get('state')} - {data.get('zip')}"
        user_id = session["user_id"]
        cart = Cart.query.filter_by(user_id=user_id).first()

        if not cart or not cart.cart_items:
            return jsonify({"error": "Your cart is empty!"}), 400

        # Calculate total amount
        total_amount = sum(item.dog.price if item.dog else item.booking.total_cost for item in cart.cart_items)

        # Create a new order
        order = Order(user_id=user_id, total_amount=total_amount, shipping_address=address, payment_status=PaymentStatus.SUCCESS)
        db.session.add(order)
        db.session.commit()

        # Move cart items to order details
        for cart_item in cart.cart_items:
            order_item = OrderDetail(order_id=order.order_id, dog_id=cart_item.dog_id, booking_id=cart_item.booking_id, quantity=cart_item.quantity)
            db.session.add(order_item)

        db.session.commit()
        # Clear the cart after order confirmation
        CartItem.query.filter_by(cart_id=cart.cart_id).delete()
        db.session.delete(cart)
        db.session.commit()

        return jsonify({
            "message": "Order confirmed successfully!",
            "order_id": order.order_id  # Send redirect URL
        })

    except Exception as e:
        db.session.rollback()  # Rollback in case of error
        return jsonify({"error": str(e)}), 500

#************************************* route for order confirmation page get request **************************************

@app.route("/order-confirm", methods=["GET"])
def order_confirm_page():
    if "user_id" not in session:
        return redirect(url_for("login"))  # Redirect if user not logged in

    order_id = request.args.get("order_id")  # Get order_id from query parameters
    if not order_id:
        flash("Invalid order ID!", "error")
        return redirect(url_for("home"))  # Redirect to home if no order_id

    # Fetch the order details from the database
    order = Order.query.filter_by(order_id=order_id, user_id=session["user_id"]).first()
    if not order:
        flash("Order not found!", "error")
        return redirect("petshop.html")  # Redirect if order not found

    # Fetch Dog Items in Order
    order_dogs = [
        {
            "id": item.dog.dog_id,
            "name": item.dog.name,
            "breed": item.dog.breed,
            "price": item.dog.price,
            "image": item.dog.image,
            "type": "dog"
        }
        for item in order.order_details if item.dog
    ]

    # Fetch Booking Items in Order
    order_bookings = [
        {
            "id": item.booking.booking_id,
            "service_name": item.booking.booking_details[0].service_name if item.booking.booking_details else "Unknown Service",
            "provider_id": item.booking.booking_details[0].service_id,
            "date": item.booking.booking_date.strftime("%Y-%m-%d"),
            "duration": item.booking.duration,
            "total_cost": item.booking.total_cost,
            "image": "static/images/istockphoto-1154973359-612x612.jpg",
            "type": "booking"
        }
        for item in order.order_details if item.booking
    ]

    # Combine into a single list
    order_items = order_dogs + order_bookings
    print("Order Items:", order_items)
    total_price = sum(item["price"] if item["type"] == "dog" else item["total_cost"] for item in order_items)

    return render_template("order_confirm.html", cart=order_items, total_price=total_price)

#*************************************** routes for service dashboard *******************************
@app.route('/services') # change name of the route to services from dashboard
def services():
    return render_template('Dashboard.html')


#*************************************** routes for fectching all services *******************************
@app.route('/api/services', methods=['GET']) # change name of the route to services from dashboard
def get_services():
    services = Service.query.all()
    services_data = [
        {
            "id": service.service_id,
            "name": service.service_name,
            "category": service.service_name.lower(),
            "description": service.description
        }
        for service in services
    ]
    return jsonify(services_data)


#*************************************** routes for service providers list *******************************
@app.route('/service-providers')
def service_providers():
    providers = ServiceProvider.query.filter_by(status=ServiceProviderStatus.ACCEPTED).all()
    return render_template('service_provider.html', providers=providers)


@app.route('/service-details/<service_id>')
def service_details(service_id):
    provider = ServiceProvider.query.get_or_404(service_id)
    # Convert the provider object to a dictionary
    provider_dict = {
        "service_id": provider.service_id,
        "name": provider.name,
        "service_name": provider.service_name,
        "address": provider.address,
        "hourly_rate": provider.hourly_rate,
        "experience": provider.experience,
        "description": provider.description,
        "status": provider.status.value,  # Convert Enum to string
        "document_folder": provider.document_folder
    }
    return render_template('service_details.html', provider=provider_dict)

#*************************************** routes for booking service providers *******************************
@app.route('/book-service', methods=['POST'])
def book_service():
    print("Book service request received")
    
    # Check if user is logged in
    if "user_id" not in session:
        print("User not logged in")
        return jsonify({"error": "User not logged in"}), 401  # Ensure user is logged in

    try:
        data = request.get_json()
        
        if not data:
            print("No data provided in request")
            return jsonify({"error": "Invalid data"}), 400  # Handle missing data

        user_id = session["user_id"]
        print(f"Processing booking for user: {user_id}")
        
        service_id = data.get("service_id")
        date = data.get("date")
        time_1 = data.get("time")
        duration = data.get("duration")
        total_cost = data.get("totalCost")
        
        print(f"Booking details: service_id={service_id}, date={date}, time={time_1}, duration={duration}, cost={total_cost}")
        
        # Ensure valid inputs
        if not all([service_id, date, time, duration, total_cost]):
            missing = []
            if not service_id: missing.append("service_id")
            if not date: missing.append("date")
            if not time: missing.append("time")
            if not duration: missing.append("duration")
            if not total_cost: missing.append("total_cost")
            print(f"Missing booking details: {', '.join(missing)}")
            return jsonify({"error": f"Missing booking details: {', '.join(missing)}"}), 400

        # Convert strings to appropriate types
        try:
            duration = int(duration)
            duration = time(hour=duration, minute=0, second=0)
            total_cost = int(total_cost)
        except (ValueError, TypeError) as e:
            print(f"Type conversion error: {str(e)}")
            return jsonify({"error": f"Invalid data format: {str(e)}"}), 400

        # Verify the service provider exists
        provider = ServiceProvider.query.get(service_id)
        if not provider:
            print(f"Service provider not found: {service_id}")
            return jsonify({"error": "Service provider not found"}), 404

        # Convert date and time to a proper format
        try:
            booking_datetime = datetime.strptime(f"{date} {time_1}", "%Y-%m-%d %H:%M")
            print(f"Parsed datetime: {booking_datetime}")
        except ValueError as e:
            print(f"Date/time parsing error: {str(e)}")
            return jsonify({"error": f"Invalid date or time format: {str(e)}"}), 400

        # Store Booking in `booking` Table
        booking = Booking(
            user_id=user_id,
            booking_date=booking_datetime,
            duration=duration,
            total_cost=total_cost
        )
        db.session.add(booking)
        db.session.commit()
        print(f"Created booking with ID: {booking.booking_id}")

        # Store Booking Details in `booking_detail` Table
        booking_detail = BookingDetail(
            booking_id=booking.booking_id,
            service_id=service_id,
            user_id=user_id,
            service_name=provider.service_name,
            service_price=total_cost
        )
        db.session.add(booking_detail)
        db.session.commit()
        print(f"Created booking detail with ID: {booking_detail.booking_detail_id}")

        return jsonify({
            "message": "Booking confirmed successfully!",
            "booking_id": booking.booking_id,
            "total_cost": total_cost
        })
    
    except Exception as e:
        db.session.rollback()
        print(f"Error in book_service: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"Failed to create booking: {str(e)}"}), 500

################################################     TEAM - 4 ROUTES GOES HERE  ###################################################################

@app.route('/analytics_dashboard')
@login_required
def analytics():
    return render_template('practice1.html')


@app.route('/monthly-trends')
def monthly_trends():
    return render_template('practice2.html')


# API endpoint for revenue data
@app.route('/data/revenue')
def revenue_data():
    data = get_revenue_data()
    return jsonify(data)

# API endpoint for booking trends data
@app.route('/data/booking')
def booking_data():
    data = get_booking_data()[0]
    print(data)
    return jsonify(data)

# API endpoint for recent bookings data
@app.route('/data/recent_bookings')
def recent_bookings():
    data = fetch_recent_bookings()
    return jsonify(data)

# API endpoint to get revenue graph
@app.route('/graph/revenue')
def revenue_graph():
    generate_revenue_graph()
    return send_file('static/revenue_graph.png', mimetype='image/png')

# API endpoint to get booking trend graph
@app.route('/graph/booking')
def booking_graph():
    generate_booking_trend()
    return send_file('static/booking_trend.png', mimetype='image/png')

@app.route('/api/get_stacked_revenue_data')
def stacked_revenue_api():
    """API endpoint that returns stacked revenue data for the chart"""
    try:
        data = get_stacked_revenue_data()
        if data and data.get('months') and data.get('revenue_per_service'):
            return jsonify(data)
        else:
            return jsonify({
                "error": "No data available",
                "months": [],
                "revenue_per_service": {}
            })
    except Exception as e:
        app.logger.error(f"Error in stacked_revenue_api: {str(e)}")
        return jsonify({
            "error": str(e),
            "months": [],
            "revenue_per_service": {}
        })




###################################################################################################################################################


if __name__ == '__main__':
    with app.app_context():
        start_scheduler(app)
        app.jinja_env.auto_reload = True
        app.config['TEMPLATES_AUTO_RELOAD'] = True    
        app.run(debug=True)

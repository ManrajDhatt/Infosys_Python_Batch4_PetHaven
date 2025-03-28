from unittest import result
import uuid
from flask import Flask, abort, jsonify, render_template, redirect, session, url_for, flash, request
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from sqlalchemy import func, text
from models import (
    Result, db, User, Event, Registration, ServiceProvider, 
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
from send_email import send_confirmation_email, send_update_email
from dotenv import load_dotenv
import cloudinary.uploader
from flask_migrate import Migrate
from scheduler import start_scheduler
# from app import db
from datetime import datetime, timezone


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

        # send_email("Welcome to PetHaven", email, f"Hello {user_name}, your registration was successful!")

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


from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_mail import Mail, Message
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import URLSafeTimedSerializer, SignatureExpired
import os, secrets
from werkzeug.utils import secure_filename

from user_models import db, init_db, User, Service, ServiceProvider, insert_initial_data

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app4.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads'

if not os.path.exists('static/uploads'):
    os.makedirs('static/uploads')

# Configure email
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'lavishverma84@gmail.com'
app.config['MAIL_PASSWORD'] = 'otka pvud gwph pjgt'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_DEFAULT_SENDER'] = 'lavishverma84@gmail.com'
mail = Mail(app)

s = URLSafeTimedSerializer(app.secret_key)

# Initialize database
init_db(app)
migrate = Migrate(app, db)

# Ensure tables exist before queries
with app.app_context():
    db.create_all()
    insert_initial_data()

# Function to send emails
def send_email(subject, recipient, body):
    msg = Message(subject, recipients=[recipient])
    msg.body = body
    mail.send(msg)

# ---------------------- ROUTES ---------------------- #
# @app.route('/')
# def home():
#     # return render_template('Auth.html')
#     return render_template('reg.html')

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

            send_email("Service Provider Registration Pending", email, "Your registration is pending admin approval.")
        
        return jsonify({"message": "Registration successful!", "status": "success", "redirect": url_for('home') }), 200  # Return success JSON

    except Exception as e:
        return jsonify({"message": str(e), "status": "error"}), 500  # Handle errors


# @app.route('/register', methods=['POST'])
# def register():
#     user_name = request.form['username']
#     email = request.form['email']
#     password = generate_password_hash(request.form['password'])
#     user_type = request.form['user_type']
#     print(user_type,232323)
#     existing_user = User.query.filter_by(email_id=email).first()
#     if existing_user:
#         flash('Email already registered!')
#         return redirect(url_for('home'))
    
#     # if user_type!='Service Provider':
#     new_user = User(user_name=user_name, email_id=email, password=password, user_type=user_type)
#     db.session.add(new_user)
#     db.session.commit()
    
#     if user_type == 'Service Provider':
#         service_provider = ServiceProvider(
#             service_id=request.form['service_id'],
#             user_id=new_user.user_id,
#             state=request.form['state'],
#             city=request.form['city'],
#             hourly_rate=request.form['hourly_rate'],
#             experience=request.form['experience'],
#             description=request.form['description'],
#             document_folder=os.path.join(app.config['UPLOAD_FOLDER'], email),
#             status='Pending'
#         )
#         db.session.add(service_provider)
#         db.session.commit()
    
#     flash('Registration successful!')
#     return redirect(url_for('home'))

# @app.route('/login', methods=['POST'])
# def login():
#     email = request.form.get('email')
#     password = request.form.get('password')

#     user = User.query.filter_by(email_id=email).first()
#     print(12345667)
#     if user and check_password_hash(user.password, password):
#         session['user_id'] = user.user_id
#         session['user_type'] = user.user_type

#         send_email("Login Alert", email, f"Hello {user.user_name}, a login attempt was made on your account.")

#         # Determine redirection URL based on user type
#         if user.user_type == 'Pet Owner':
#             dashboard_url = url_for('customer_dashboard')
#         elif user.user_type == 'Service Provider':
            
#             dashboard_url = url_for('service_provider_dashboard')
#         else:
#             dashboard_url = url_for('admin_dashboard')

#         return jsonify({
#             "status": "success",
#             "message": "Login successful!",
#             "redirect": dashboard_url
#         }), 200
#     else:
#         return jsonify({
#             "status": "error",
#             "message": "Invalid credentials! Please try again."
#         }), 401

# @app.route('/login', methods=['POST'])
# def login():
#     email = request.form['email']
#     password = request.form['password']
    
#     user = User.query.filter_by(email_id=email).first()
#     if user and check_password_hash(user.password, password):
#         session['user_id'] = user.user_id
#         session['user_type'] = user.user_type
        
#         if user.user_type == 'Pet Owner':
#             return redirect(url_for('customer_dashboard'))
#         elif user.user_type == 'Service Provider':
#             return redirect(url_for('service_provider_dashboard'))
#         else:
#             return redirect(url_for('admin_dashboard'))
#     else:
#         flash('Invalid credentials!')
#         return redirect(url_for('home'))



# @app.route('/admin_login', methods=['POST'])
# def admin_login():
#     username = request.form['username']
#     password = request.form['password']
    
#     admin = User.query.filter_by(user_name=username, user_type=None).first()
#     print(admin)
#     if admin and check_password_hash(admin.password, password):
#         session['user_id'] = admin.user_id
#         session['user_type'] = 'Admin'
        
#         return jsonify({
#             "status": "success",
#             "message": "Admin login successful!",
#             "redirect": url_for('admin_dashboard')
#         })
    
#     return jsonify({
#         "status": "error",
#         "message": "Invalid admin credentials!"
#     })


# @app.route('/admin_login', methods=['POST'])
# def admin_login():
#     username = request.form['username']
#     password = request.form['password']
    
#     admin = User.query.filter_by(user_name=username, user_type=None).first()
#     if admin and check_password_hash(admin.password, password):
#         session['user_id'] = admin.user_id
#         session['user_type'] = 'Admin'
#         return redirect(url_for('admin_dashboard'))
#     else:
#         flash('Invalid admin credentials!')
#         return redirect(url_for('home'))

# ---------------------- RESET PASSWORD FEATURE ---------------------- #

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

# @app.route('/admin/manage_service_providers')
# def manage_service_providers():
#     """ Show all pending service providers for admin approval """
#     service_providers = ServiceProvider.query.filter_by(status='PENDING').all()
#     for service_provider in service_providers:
#         print(service_provider.documents)
#     return render_template('manage_sp.html', service_providers=service_providers)

# ---------------------- APPROVE SERVICE PROVIDER ---------------------- #

# @app.route('/admin/approve_service_provider/<sp_id>', methods=['POST'])
# def approve_service_provider(sp_id):
#     """ Approve a service provider and redirect them to their dashboard """
#     service_provider = ServiceProvider.query.get(sp_id)
#     if service_provider:
#         service_provider.status = 'ACCEPTED'
#         db.session.commit()
#         flash("Service Provider approved successfully!", "success")
#         return '', 200  # AJAX success response
#     return '', 400  # AJAX failure response

# ---------------------- REJECT SERVICE PROVIDER ---------------------- #

# @app.route('/admin/reject_service_provider/<sp_id>', methods=['POST'])
# def reject_service_provider(sp_id):
#     """ Reject a service provider and redirect them to the Get Started page """
#     service_provider = ServiceProvider.query.get(sp_id)
#     if service_provider:
#         service_provider.status = 'REJECTED'
#         db.session.commit()
#         flash("Service Provider rejected!", "danger")
#         return '', 200  # AJAX success response
#     return '', 400  # AJAX failure response


# @app.route('/customer_dashboard')
# def customer_dashboard():
#     return render_template('customer_dashboard.html')

# @app.route('/service_provider_dashboard')
# def service_provider_dashboard():
#     return render_template('service_provider_dashboard.html')

# @app.route('/admin_dashboard')
# def admin_dashboard():
#     return render_template('admin_dashboard.html')

@app.route('/logout')
def logout():
    session.clear()
    flash("Logged out successfully!")
    return redirect(url_for('home'))

# #added newly 
# @app.route('/manage_sp')
# def manage_sp():
#     service_providers = ServiceProvider.query.all()  # Fetch all service providers
#     return render_template('manage_sp.html', service_providers=service_providers)

# ---------------------- MAIN ---------------------- #
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=False)

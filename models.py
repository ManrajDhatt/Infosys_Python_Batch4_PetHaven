from werkzeug.security import generate_password_hash
import uuid
import enum
import random
from datetime import datetime, timezone, timedelta, time
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from flask import current_app as app , jsonify
from sqlalchemy import text, func  # Add this func also from db
import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd
from collections import defaultdict

db = SQLAlchemy()

db = SQLAlchemy()
    
#******************************************* Dogs Ownership Table (Many-to-Many) **********************************
dog_ownership = db.Table(
    "dog_ownership",
    db.Column("user_id", db.String(36), db.ForeignKey("user.user_id"), primary_key=True),
    db.Column("dog_id", db.String(36), db.ForeignKey("dogs.dog_id"), primary_key=True)
)

#*************************************** User and ServiceProvider (Many-to-Many) Relationship ****************
user_service_provider = db.Table(
    "user_service_provider",
    db.Column("user_id", db.String(36), db.ForeignKey("user.user_id"), primary_key=True),
    # db.Column("service_id", db.Integer, db.ForeignKey("service_provider.service_id"), primary_key=True)   OLD CODE
    db.Column("service_id", db.String(36), db.ForeignKey("service_provider.service_id"), primary_key=True)
)


class User(db.Model,UserMixin): # OLD CODE -> Works 
# class User(db.Model): -> NEW CODE  -> NOT WORKING
    __tablename__ = 'user'
    user_id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))  # Use UUID
    user_name = db.Column(db.String(50), nullable=False, unique=True)
    email_id = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)  # Storing hashed password
    phone_number = db.Column(db.String(10), nullable=True)
    address = db.Column(db.String(50), nullable=True)
    user_type = db.Column(db.String(20), nullable=True)  # NULL for Admin, 'Pet Owner' or 'Service Provider' for users
    is_active = db.Column(db.Boolean, default=True)

    # Relationships
    orders = db.relationship("Order", backref="user", lazy=True)
    carts = db.relationship("Cart", backref="user", lazy=True)
    bookings = db.relationship("Booking", backref="user", lazy=True)
    service_providers = db.relationship("ServiceProvider", secondary=user_service_provider, back_populates="users")
    dogs = db.relationship("Dogs", secondary=dog_ownership, back_populates="owners")
    
    @property
    def is_admin(self):
        return self.user_type is None 
    @property
    def is_petOwner(self):
        return self.user_type == "Pet Owner"

    @property
    def is_serviceProvider(self):
        return self.user_type == "Service Provider"

    def get_id(self):  
        return str(self.user_id)
    def __repr__(self):
        return f"<User {self.user_type} - {self.user_name}>"


class Service(db.Model):
    __tablename__ = 'services'
    service_id = db.Column(db.Integer, primary_key=True)
    service_name = db.Column(db.String(50))
    description = db.Column(db.Text)  # Added description column



# ****************************************** Dogs Table (Renamed from Dog) *******************************************
class Dogs(db.Model):
    __tablename__ = "dogs"

    dog_id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(60), nullable=False)
    breed = db.Column(db.String(60), nullable=False)
    age = db.Column(db.String(20), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    vaccinated = db.Column(db.String(3), nullable=False)
    description = db.Column(db.String(255), nullable=False)
    image = db.Column(db.String(200), nullable=False)

    order_details = db.relationship("OrderDetail", backref="dogs", lazy=True)
    cart_items = db.relationship("CartItem", back_populates="dog", lazy=True)
    owners = db.relationship("User", secondary=dog_ownership, back_populates="dogs")

    def __repr__(self):
        return f"<Dogs {self.name} - {self.breed}>"

# ****************************************** Service Provider Table *******************************************
class ServiceProviderStatus(enum.Enum):
    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"

class ServiceProvider(db.Model):
    __tablename__ = "service_provider"
    service_id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey("user.user_id"), nullable=False, default=lambda: str(uuid.uuid4()))

    # service_id = db.Column(db.Integer, db.ForeignKey('services.service_id'), primary_key=True) -> OLD CODE
    # user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), primary_key=True)    

    # user_id = db.Column(db.String(36), db.ForeignKey('user.user_id'), primary_key=True) -> OLD CODE
    name = db.Column(db.String(100), nullable=False)
    service_name = db.Column(db.String(60), nullable=False)
    address = db.Column(db.String(255), nullable=False)
    hourly_rate = db.Column(db.Integer, nullable=False)
    experience = db.Column(db.String(30), nullable=False)
    description = db.Column(db.String(255), nullable=False)
    status = db.Column(db.Enum(ServiceProviderStatus), default=ServiceProviderStatus.PENDING, nullable=False)
    document_folder = db.Column(db.String(255), nullable=False)

    # Many-to-Many Relationship with Users
    users = db.relationship("User", secondary=user_service_provider, back_populates="service_providers")

    def __repr__(self):
        return f"<ServiceProvider {self.name}>"


# ****************************************** Booking Table ****************************************************
class Booking(db.Model):
    __tablename__ = "booking"

    booking_id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey("user.user_id"), nullable=False)
    booking_date = db.Column(db.DateTime, default=db.func.current_timestamp())
    duration = db.Column(db.Time, nullable=False)
    total_cost = db.Column(db.Integer, nullable=False)

    booking_details = db.relationship("BookingDetail", backref="booking", lazy=True)
    order_details = db.relationship("OrderDetail", back_populates="booking", lazy=True)
    cart_items = db.relationship("CartItem", back_populates="booking", lazy=True)

    def __repr__(self):
        return f"<Booking {self.booking_id} - User {self.user_id}>"

# ****************************************** Booking Details Table *******************************************
class BookingDetail(db.Model):
    __tablename__ = "booking_detail"

    booking_detail_id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    booking_id = db.Column(db.String(36), db.ForeignKey("booking.booking_id"), nullable=False)
    service_id = db.Column(db.String(36), nullable=False)
    user_id = db.Column(db.String(36), nullable=False)
    service_name = db.Column(db.String(100), nullable=False)
    service_price = db.Column(db.Integer, nullable=False)

    _table_args_ = (
        db.ForeignKeyConstraint(
            ['service_id', 'user_id'],
            ['service_provider.service_id', 'service_provider.user_id']
        ),
    )

    def __repr__(self):
        return f"<BookingDetail {self.booking_detail_id} - Booking {self.booking_id}>"

# ********************************************* Order Table **************************************************
class PaymentStatus(enum.Enum):
    PENDING = "Pending"
    SUCCESS = "Success"

class Order(db.Model):
    __tablename__ = "order"

    order_id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey("user.user_id"), nullable=False)
    total_amount = db.Column(db.Integer, nullable=False)
    shipping_address = db.Column(db.String(255), nullable=False)
    payment_status = db.Column(db.Enum(PaymentStatus), default=PaymentStatus.PENDING, nullable=False)
    order_date = db.Column(db.DateTime, default=db.func.current_timestamp())

    order_details = db.relationship("OrderDetail", back_populates="order", lazy=True)

    def __repr__(self):
        return f"<Order {self.order_id} - {self.total_amount}>"

# ****************************************** Order Details Table *******************************************
class OrderDetail(db.Model):
    __tablename__ = "order_detail"

    order_detail_id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    order_id = db.Column(db.String(36), db.ForeignKey("order.order_id"), nullable=False)
    dog_id = db.Column(db.String(36), db.ForeignKey("dogs.dog_id"), nullable=True)
    booking_id = db.Column(db.String(36), db.ForeignKey("booking.booking_id"), nullable=True)
    quantity = db.Column(db.Integer, nullable=False, default=1)

    booking = db.relationship("Booking", back_populates="order_details", lazy=True)
    dog = db.relationship("Dogs", back_populates="order_details", lazy=True, overlaps="dogs")
    order = db.relationship("Order", back_populates="order_details", lazy=True)

    def __repr__(self):
        return f"<OrderDetail {self.order_detail_id} - {self.quantity}>"

# ********************************************* Cart Table ***************************************************
class Cart(db.Model):
    __tablename__ = "cart"

    cart_id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey("user.user_id"), nullable=False)
    total_amount = db.Column(db.Integer, nullable=False)
    order_date = db.Column(db.DateTime, default=db.func.current_timestamp())

    cart_items = db.relationship("CartItem", back_populates="cart", lazy=True)

    def __repr__(self):
        return f"<Cart {self.cart_id} - {self.total_amount}>"

# ******************************************** Cart Items Table **********************************************
class CartItem(db.Model):
    __tablename__ = "cart_item"

    cart_item_id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    cart_id = db.Column(db.String(36), db.ForeignKey("cart.cart_id"), nullable=False)
    dog_id = db.Column(db.String(36), db.ForeignKey("dogs.dog_id"), nullable=True)
    booking_id = db.Column(db.String(36), db.ForeignKey("booking.booking_id"), nullable=True)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    booking = db.relationship("Booking", back_populates="cart_items", lazy=True)
    dog = db.relationship("Dogs", back_populates="cart_items", lazy=True)
    cart = db.relationship("Cart", back_populates="cart_items", lazy=True)
    def __repr__(self):
        return f"<CartItem {self.cart_item_id} - {self.quantity}>"


class Event(db.Model):
    # id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4())) -> OLD CODE
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    date = db.Column(db.String(50), nullable=False)
    location=db.Column(db.String(250),nullable=False)
    prizes=db.Column(db.String(200),nullable=False)
    eligibility=db.Column(db.String(250),nullable=False)
    fee = db.Column(db.Float, default=500)
    image_filename = db.Column(db.String(200), nullable=False, default="default.jpg") 


class Registration(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    # id = db.Column(db.Integer, primary_key=True, autoincrement=True)  NEW CODE -> NOT WORKING
    user_id = db.Column(db.String(36), db.ForeignKey('user.user_id'), nullable=False)
    event_id = db.Column(db.String(36), db.ForeignKey('event.id'), nullable=False)
    # user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False) NEW CODE -> NOT WORKING 
    # event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False) NEW CODE -> NOT WORKING
    pet_name = db.Column(db.String(100), nullable=False)
    pet_type = db.Column(db.String(100), nullable=False)
    pet_age=db.Column(db.Integer,nullable=False)
    paid = db.Column(db.Boolean, default=False)
    timestamp = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))  
    
     # Relationship with Event
    event = db.relationship('Event', backref=db.backref('registrations', lazy=True))

    # Relationship with User 
    user = db.relationship('User', backref=db.backref('registrations', lazy=True))



class Result(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    registration_id = db.Column(db.String(36), db.ForeignKey('registration.id'), nullable=False, unique=True)
    # id = db.Column(db.Integer, primary_key=True)  NEW CODE -> NOT WORKING
    # registration_id = db.Column(db.Integer, db.ForeignKey('registration.id'), nullable=False, unique=True) NEW CODE -> NOT WORKING
    attended = db.Column(db.Boolean, default=False, nullable=False)  # Present or Absent
    position = db.Column(db.Integer, nullable=True)  # 1,2,...
    points = db.Column(db.Float, default=0)  # Optional: Track performance points
    remarks = db.Column(db.Text, nullable=True)  # Any comments (e.g., "Great performance")

    # Relationship with Registration
    registration = db.relationship('Registration', backref=db.backref('result', uselist=False, lazy=True))


class Transaction(db.Model):
    __tablename__ = 'transaction'

    t_id = db.Column(db.String(50), primary_key=True)
    date = db.Column(db.DateTime, nullable=False)
    
    # Foreign key to the 'User' table
    user_id = db.Column(db.String(36), db.ForeignKey('user.user_id'), nullable=False)  

    # Composite foreign key (service_id, user_id) referencing ServiceProvider table
    service_id = db.Column(db.Integer, nullable=False)
    # provider_user_id = db.Column(db.Integer, nullable=False)
    provider_user_id = db.Column(db.String(36), nullable=False)

    __table_args__ = (
        db.ForeignKeyConstraint(
            ['service_id', 'provider_user_id'],
            ['service_provider.service_id', 'service_provider.user_id']
        ),
    )

    # Relationships
    user = db.relationship("User", backref="transactions", lazy=True)  
    service_provider = db.relationship("ServiceProvider", backref="transactions", lazy=True)

    def __repr__(self):
        return f"<Transaction {self.t_id} - User {self.user_id} - Service {self.service_id}>"

# Function to insert predefined data including admin
def insert_initial_data():
    if Service.query.count() == 0:
        services_data = [
            (1, "Grooming", "Keep your furry friends looking and feeling their best with our professional grooming services."),
            (2, "Therapies", "Enhance your pet’s well-being with specialized therapy services like physiotherapy and hydrotherapy."),
            (3, "Health", "Comprehensive health services including check-ups, vaccinations, and nutritional guidance."),
            (4, "Training", "Expert training programs for obedience, behavior correction, and skill development."),
            (5, "Spa", "Luxurious spa services including soothing baths, fur conditioning, and aromatherapy."),
        ]
        for service in services_data:
            db.session.add(Service(service_id=service[0], service_name=service[1], description=service[2]))
        db.session.commit()
        print("Inserted initial service data.")

    # Insert admin directly into User table
    admin_username = "Admin@123"
    admin_email = "admin@example.com"
    admin_password = "password@123"

    admin_user = User.query.filter_by(user_name=admin_username).first()
    if not admin_user:
        hashed_password = generate_password_hash(admin_password)
        admin = User(
            user_name=admin_username,
            email_id=admin_email,
            password=hashed_password,
            phone_number=None,
            address=None,
            user_type=None,  # NULL for Admin
            is_active=True
        )
        db.session.add(admin)
        db.session.commit()
        print("Inserted default admin user.")
        


def insert_seed_data():
    if User.query.count() == 0:
        users = [
            
            User(user_name="john_doe", email_id="john.doe@example.com", password=generate_password_hash("johnpass"), phone_number="9876543210", address="101 Elm St", user_type="Pet Owner", is_active=True),
            User(user_name="jane_smith", email_id="jane.smith@example.com", password=generate_password_hash("jane1234"), phone_number="8765432109", address="202 Oak St", user_type="Service Provider", is_active=True),
            User(user_name="peter_parker", email_id="peter.parker@example.com", password=generate_password_hash("spiderman"), phone_number="7654321098", address="303 Maple St", user_type="Pet Owner", is_active=True),
            User(user_name="bruce_wayne", email_id="bruce.wayne@example.com", password=generate_password_hash("batman"), phone_number="6543210987", address="404 Wayne Manor", user_type="Pet Owner", is_active=True),
            User(user_name="clark_kent", email_id="clark.kent@example.com", password=generate_password_hash("superman"), phone_number="5432109876", address="505 Metropolis St", user_type="Pet Owner", is_active=True),
            User(user_name="tony_stark", email_id="tony.stark@example.com", password=generate_password_hash("ironman"), phone_number="4321098765", address="606 Stark Tower", user_type="Service Provider", is_active=True),
            User(user_name="diana_prince", email_id="diana.prince@example.com", password=generate_password_hash("wonderwoman"), phone_number="3210987654", address="707 Themyscira", user_type="Pet Owner", is_active=True),
            User(user_name="steve_rogers", email_id="steve.rogers@example.com", password=generate_password_hash("captain"), phone_number="2109876543", address="808 Brooklyn St", user_type="Service Provider", is_active=True),
            User(user_name="natasha_romanoff", email_id="natasha.romanoff@example.com", password=generate_password_hash("blackwidow"), phone_number="1098765432", address="909 Red Room", user_type="Pet Owner", is_active=True),
            User(user_name="thor_odinson", email_id="thor.odinson@example.com", password=generate_password_hash("mjolnir"), phone_number="1987654321", address="Asgard", user_type="Service Provider", is_active=True),
            User(user_name="loki_laufeyson", email_id="loki.laufeyson@example.com", password=generate_password_hash("trickster"), phone_number="2876543210", address="Jotunheim", user_type="Pet Owner", is_active=False),
            User(user_name="wanda_maximoff", email_id="wanda.maximoff@example.com", password=generate_password_hash("scarletwitch"), phone_number="3765432109", address="Westview", user_type="Pet Owner", is_active=True),
            User(user_name="vision", email_id="vision@example.com", password=generate_password_hash("mindstone"), phone_number="4654321098", address="Avengers Compound", user_type="Service Provider", is_active=True),
            User(user_name="bruce_banner", email_id="bruce.banner@example.com", password=generate_password_hash("hulk"), phone_number="5543210987", address="Gamma Lab", user_type="Pet Owner", is_active=True),
            User(user_name="stephen_strange", email_id="stephen.strange@example.com", password=generate_password_hash("sorcerer"), phone_number="6432109876", address="Sanctum Sanctorum", user_type="Service Provider", is_active=True),
            User(user_name="peter_quill", email_id="peter.quill@example.com", password=generate_password_hash("starlord"), phone_number="7321098765", address="Milano", user_type="Pet Owner", is_active=True),
            User(user_name="gamora", email_id="gamora@example.com", password=generate_password_hash("deadliestwoman"), phone_number="8210987654", address="Knowhere", user_type="Pet Owner", is_active=True),
            User(user_name="rocket_raccoon", email_id="rocket@example.com", password=generate_password_hash("boom"), phone_number="9109876543", address="Guardians Ship", user_type="Service Provider", is_active=True),
            User(user_name="groot", email_id="groot@example.com", password=generate_password_hash("iamgroot"), phone_number="0198765432", address="Guardians Ship", user_type="Pet Owner", is_active=True),
        ]

        db.session.add_all(users)
    if Dogs.query.count() == 0:
        dogs = [
            { 'name': "Buddy", 'breed': "Labrador", 'age': "Puppy", 'price': 1500, 'image': "static/images/buddy.jpg", 'vaccinated': "Yes", 'description': "Friendly and energetic, loves to play and is great with families." },
            { 'name': "Bella", 'breed': "Bulldog", 'age': "Adult", 'price': 2000, 'image': "static/images/bella.jpg", 'vaccinated': "Yes", 'description': "Loyal and protective, perfect for an indoor pet with moderate activity." },
            { 'name': "Charlie", 'breed': "Poodle", 'age': "Senior", 'price': 1200, 'image': "static/images/charlie.jpg", 'vaccinated': "Yes", 'description': "Intelligent and obedient, enjoys companionship and learning new tricks." },
            { 'name': "Max", 'breed': "Labrador", 'age': "Adult", 'price': 1800, 'image': "static/images/max.avif", 'vaccinated': "Yes", 'description': "Labradors are loving and sociable, ideal for families and outdoor activities." },
            { 'name': "Lucy", 'breed': "Bulldog", 'age': "Puppy", 'price': 2200, 'image': "static/images/Lucy.webp", 'vaccinated': "No", 'description': "Playful and affectionate, enjoys snuggling and short walks." },
            { 'name': "Daisy", 'breed': "Poodle", 'age': "Adult", 'price': 2500, 'image': "static/images/daisy.jpg", 'vaccinated': "Yes", 'description': "Lively and intelligent, thrives on mental stimulation and companionship." },
            { 'name': "Max", 'breed': "Beagle", 'age': "Young", 'price': 7000, 'image': "static/images/beagle.jpg", 'vaccinated': "No", 'description': "Curious and energetic, Beagles are great scent hounds and family pets." },
            { 'name': "Charlie", 'breed': "Labrador", 'age': "Adult", 'price': 9000, 'image': "static/images/labrador.jpg", 'vaccinated': "Yes", 'description': "Loyal and friendly, loves swimming and fetching games." },
            { 'name': "Rocky", 'breed': "German Shepherd", 'age': "Mature", 'price': 12000, 'image': "static/images/germanShepherd.jpg", 'vaccinated': "Yes", 'description': "Intelligent and protective, excellent as a guard dog and working companion." },
            { 'name': "Bella", 'breed': "Poodle", 'age': "Puppy", 'price': 8000, 'image': "static/images/poodle.jpg", 'vaccinated': "No", 'description': "Charming and elegant, Poodles are highly trainable and affectionate." },
            { 'name': "Daisy", 'breed': "Golden Retriever", 'age': "Adult", 'price': 11000, 'image': "static/images/goldenretriever.jpg", 'vaccinated': "Yes", 'description': "Loyal and loving, enjoys outdoor activities and socializing with humans." },
            { 'name': "Oscar", 'breed': "Bulldog", 'age': "Young", 'price': 7500, 'image': "static/images/bulldog.jpg", 'vaccinated': "No", 'description': "Calm and dignified, Bulldogs are easy-going and affectionate pets." },
            { 'name': "Lucy", 'breed': "Shih Tzu", 'age': "Puppy", 'price': 6500, 'image': "static/images/shihtzu.jpg", 'vaccinated': "Yes", 'description': "Sweet and friendly, perfect for small living spaces and gentle playtime." },
            { 'name': "Milo", 'breed': "Dachshund", 'age': "Young", 'price': 6800, 'image': "static/images/dachshund.jpg", 'vaccinated': "Yes", 'description': "Brave and curious, Dachshunds are great for adventurous and playful owners." },
            { 'name': "Bailey", 'breed': "Rottweiler", 'age': "Mature", 'price': 13000, 'image': "static/images/rottweiler.jpg", 'vaccinated': "Yes", 'description': "Strong and confident, Rottweilers are excellent guard dogs and family protectors." },
            { 'name': "Teddy", 'breed': "Pomeranian", 'age': "Puppy", 'price': 6000, 'image': "static/images/pomeranian.jpg", 'vaccinated': "No", 'description': "Tiny but bold, Pomeranians are playful, energetic, and love attention." },
            { 'name': "Coco", 'breed': "Husky", 'age': "Adult", 'price': 14000, 'image': "static/images/husky.jpg", 'vaccinated': "Yes", 'description': "Energetic and independent, Huskies thrive in active households." },
            { 'name': "Buddy", 'breed': "Dalmatian", 'age': "Young", 'price': 8500, 'image': "static/images/dalmatian.jpg", 'vaccinated': "Yes", 'description': "Dalmatians are playful and athletic, with a striking spotted coat." },
            { 'name': "Buster", 'breed': "Border Collie", 'age': "Mature", 'price': 10000, 'image': "static/images/border_collie.jpg", 'vaccinated': "Yes", 'description': "Highly intelligent and active, ideal for training and herding activities." },
            { 'name': "Duke", 'breed': "Corgi", 'age': "Puppy", 'price': 9500, 'image': "static/images/corgi.jpg", 'vaccinated': "No", 'description': "Short but sturdy, Corgis are playful, friendly, and great companions." },
            { 'name': "Zoe", 'breed': "Samoyed", 'age': "Adult", 'price': 13500, 'image': "static/images/samoyed.jpg", 'vaccinated': "Yes", 'description': "Fluffy and friendly, Samoyeds are gentle giants who love people." },
            { 'name': "Luna", 'breed': "Maltese", 'age': "Young", 'price': 7200, 'image': "static/images/maltese.jpg", 'vaccinated': "Yes", 'description': "Elegant and affectionate, Maltese dogs are ideal lap dogs and companions." },
            { 'name': "Hunter", 'breed': "Doberman", 'age': "Mature", 'price': 12500, 'image': "static/images/doberman.jpg", 'vaccinated': "Yes", 'description': "Athletic and protective, Dobermans are intelligent and loyal guardians." },
            { 'name': "Rex", 'breed': "Saint Bernard", 'age': "Senior", 'price': 15000, 'image': "static/images/saintBernard.jpg", 'vaccinated': "Yes", 'description': "Gentle giants, Saint Bernards are affectionate and protective family dogs." },
            { 'name': "Lily", 'breed': "Chihuahua", 'age': "Puppy", 'price': 5800, 'image': "static/images/chihuahua.jpg", 'vaccinated': "No", 'description': "Small and lively, Chihuahuas are feisty companions with big personalities." },
            { 'name': "Jack", 'breed': "Akita", 'age': "Adult", 'price': 11000, 'image': "static/images/akita.jpg", 'vaccinated': "Yes", 'description': "Strong and dignified, Akitas are fiercely loyal and protective." },
            { 'name': "Nala", 'breed': "Great Dane", 'age': "Mature", 'price': 14500, 'image': "static/images/greatDane.jpg", 'vaccinated': "Yes", 'description': "Gentle giants, Great Danes are friendly and affectionate family pets." },
            { "name": "Leo", "breed": "Shiba Inu", "age": "Young", "price": 9500, "image": "static/images/shibainu.jpg", "vaccinated": "Yes", "description": "Leo is an energetic and intelligent Shiba Inu who loves to explore. With his playful nature and strong personality, he's perfect for active owners." },
            { "name": "Jasper", "breed": "Alaskan Malamute", "age": "Adult", "price": 13000, "image": "static/images/alaskanMalamute.jpg", "vaccinated": "Yes", "description": "Jasper is a strong and friendly Alaskan Malamute. He enjoys cold weather, long hikes, and spending time with his family." },
            { "name": "Penny", "breed": "Papillon", "age": "Young", "price": 6700, "image": "static/images/papillon.jpg", "vaccinated": "No", "description": "Penny is a small but lively Papillon with a friendly and affectionate personality. She loves to play and is highly trainable." },
            { "name": "Benny", "breed": "Basset Hound", "age": "Adult", "price": 7700, "image": "static/images/bassethound.jpg", "vaccinated": "Yes", "description": "Benny is a calm and lovable Basset Hound. With his droopy ears and soulful eyes, he's perfect for families who love gentle and affectionate dogs." },
            { "name": "Nova", "breed": "Cane Corso", "age": "Mature", "price": 13700, "image": "static/images/caneCorso.jpg", "vaccinated": "Yes", "description": "Nova is a powerful and protective Cane Corso, perfect for experienced dog owners looking for a loyal guardian." },
            { "name": "Hazel", "breed": "Irish Setter", "age": "Adult", "price": 8800, "image": "static/images/irishSetter.jpg", "vaccinated": "No", "description": "Hazel is a graceful and energetic Irish Setter, known for her affectionate personality and love for running in open fields." },
            { "name": "Rusty", "breed": "Weimaraner", "age": "Young", "price": 9200, "image": "static/images/weimaraner.jpg", "vaccinated": "Yes", "description": "Rusty is a sleek and athletic Weimaraner, always ready for adventure. He’s a great companion for active families." },
            { "name": "Sky", "breed": "Newfoundland", "age": "Senior", "price": 15500, "image": "static/images/newfoundland.jpg", "vaccinated": "Yes", "description": "Sky is a gentle and loving Newfoundland, known for his calm demeanor and excellent swimming ability. Great for families with kids."},
        ]
        for dog in dogs:
            new_dog = Dogs(**dog)
            db.session.add(new_dog)
    if ServiceProvider.query.count() == 0:
        service_providers = [
            ServiceProvider(service_id=1, name="John Doe", service_name="Grooming", address="101 Elm St", hourly_rate=50, experience="5 years", description="Expert in pet grooming.", status=ServiceProviderStatus.ACCEPTED, document_folder="docs/john_doe"),
            ServiceProvider(service_id=2, name="Jane Smith", service_name="Therapies", address="202 Oak St", hourly_rate=60, experience="7 years", description="Certified pet therapist.", status=ServiceProviderStatus.PENDING, document_folder="docs/jane_smith"),
            ServiceProvider(service_id=3, name="Peter Parker", service_name="Health", address="303 Maple St", hourly_rate=80, experience="10 years", description="Veterinarian specializing in dogs.", status=ServiceProviderStatus.ACCEPTED, document_folder="docs/peter_parker"),
            ServiceProvider(service_id=4, name="Bruce Wayne", service_name="Training", address="404 Wayne Manor", hourly_rate=70, experience="8 years", description="Professional dog trainer.", status=ServiceProviderStatus.REJECTED, document_folder="docs/bruce_wayne"),
            ServiceProvider(service_id=5, name="Clark Kent", service_name="Spa", address="505 Metropolis St", hourly_rate=65, experience="6 years", description="Relaxing spa for pets.", status=ServiceProviderStatus.ACCEPTED, document_folder="docs/clark_kent"),
            ServiceProvider(service_id=6, name="Tony Stark", service_name="Grooming", address="606 Stark Tower", hourly_rate=75, experience="9 years", description="Luxury grooming services.", status=ServiceProviderStatus.PENDING, document_folder="docs/tony_stark"),
            ServiceProvider(service_id=7, name="Diana Prince", service_name="Therapies", address="707 Themyscira", hourly_rate=85, experience="12 years", description="Holistic therapies for pets.", status=ServiceProviderStatus.ACCEPTED, document_folder="docs/diana_prince"),
            ServiceProvider(service_id=8, name="Steve Rogers", service_name="Health", address="808 Brooklyn St", hourly_rate=90, experience="15 years", description="Veterinary care specialist.", status=ServiceProviderStatus.PENDING, document_folder="docs/steve_rogers"),
            ServiceProvider(service_id=9, name="Natasha Romanoff", service_name="Training", address="909 Red Room", hourly_rate=55, experience="4 years", description="Basic and advanced pet training.", status=ServiceProviderStatus.ACCEPTED, document_folder="docs/natasha_romanoff"),
            ServiceProvider(service_id=10, name="Thor Odinson", service_name="Spa", address="Asgard", hourly_rate=95, experience="10 years", description="Luxury spa treatments for pets.", status=ServiceProviderStatus.REJECTED, document_folder="docs/thor_odinson"),
            ServiceProvider(service_id=11, name="Loki Laufeyson", service_name="Grooming", address="Jotunheim", hourly_rate=50, experience="3 years", description="Cool grooming styles.", status=ServiceProviderStatus.ACCEPTED, document_folder="docs/loki_laufeyson"),
            ServiceProvider(service_id=12, name="Wanda Maximoff", service_name="Therapies", address="Westview", hourly_rate=70, experience="6 years", description="Calming therapies for anxious pets.", status=ServiceProviderStatus.PENDING, document_folder="docs/wanda_maximoff"),
            ServiceProvider(service_id=13, name="Vision", service_name="Health", address="Avengers Compound", hourly_rate=85, experience="8 years", description="Cutting-edge medical care.", status=ServiceProviderStatus.ACCEPTED, document_folder="docs/vision"),
            ServiceProvider(service_id=14, name="Bruce Banner", service_name="Training", address="Gamma Lab", hourly_rate=60, experience="5 years", description="Gentle but effective training.", status=ServiceProviderStatus.REJECTED, document_folder="docs/bruce_banner"),
            ServiceProvider(service_id=15, name="Stephen Strange", service_name="Spa", address="Sanctum Sanctorum", hourly_rate=95, experience="9 years", description="Mystical pet relaxation.", status=ServiceProviderStatus.ACCEPTED, document_folder="docs/stephen_strange"),
            ServiceProvider(service_id=16, name="Peter Quill", service_name="Grooming", address="Milano", hourly_rate=45, experience="2 years", description="Fun and stylish grooming.", status=ServiceProviderStatus.PENDING, document_folder="docs/peter_quill"),
            ServiceProvider(service_id=17, name="Gamora", service_name="Therapies", address="Knowhere", hourly_rate=80, experience="7 years", description="Deep relaxation therapies.", status=ServiceProviderStatus.ACCEPTED, document_folder="docs/gamora"),
            ServiceProvider(service_id=18, name="Rocket Raccoon", service_name="Health", address="Guardians Ship", hourly_rate=100, experience="12 years", description="Top-tier medical diagnostics.", status=ServiceProviderStatus.PENDING, document_folder="docs/rocket_raccoon"),
            ServiceProvider(service_id=19, name="Groot", service_name="Training", address="Guardians Ship", hourly_rate=50, experience="3 years", description="Patient and fun training.", status=ServiceProviderStatus.ACCEPTED, document_folder="docs/groot"),
            ServiceProvider(service_id=20, name="Bucky Barnes", service_name="Spa", address="Wakanda", hourly_rate=90, experience="10 years", description="Luxury spa sessions.", status=ServiceProviderStatus.REJECTED, document_folder="docs/bucky_barnes"),
        ]
        db.session.add_all(service_providers)

        
        # After service_providers check and before printing "Service providers added successfully!"
    if Booking.query.count() == 0:
        bookings = []
        booking_details = []

        for i in range(1, 21):
            user_id = str(random.randint(1, 15))  # Random user from your existing users
            booking_id = str(uuid.uuid4())
            booking_date = datetime.now() - timedelta(days=random.randint(1, 90))
            random_hours = random.randint(0, 5)
            random_minutes = random.randint(0, 59)
            duration = time(random_hours, random_minutes)
            total_cost = random.randint(50, 300)

            booking = Booking(
                booking_id=booking_id,
                user_id=user_id,
                booking_date=booking_date,
                duration=duration,
                total_cost=total_cost
            )
            bookings.append(booking)

            # Creating BookingDetail entry
            service_id = random.randint(1, 5)
            service_name = random.choice(["Grooming", "Therapies", "Health", "Training", "Spa"])
            service_price = random.randint(50, 200)

            booking_detail = BookingDetail(
                booking_detail_id=str(uuid.uuid4()),
                booking_id=booking_id,
                service_id=str(service_id),
                user_id=user_id,
                service_name=service_name,
                service_price=service_price
            )
            booking_details.append(booking_detail)

        db.session.add_all(bookings)
        db.session.add_all(booking_details)

    if Order.query.count() == 0:
        orders = []
        order_details = []

        for i in range(1, 21):
            user_id = str(i)
            order_id = str(uuid.uuid4())
            total_amount = random.randint(100, 1000)
            shipping_address = f"{random.randint(100, 999)} Main St, City {i}"
            payment_status = random.choice([PaymentStatus.PENDING, PaymentStatus.SUCCESS])
            order_date = datetime.now() - timedelta(days=random.randint(1, 30))

            order = Order(
                order_id=order_id,
                user_id=user_id,
                total_amount=total_amount,
                shipping_address=shipping_address,
                payment_status=payment_status,
                order_date=order_date
            )
            orders.append(order)

            # Creating OrderDetail entry
            dog_id = str(uuid.uuid4()) if random.choice([True, False]) else None
            booking_id = str(uuid.uuid4()) if dog_id is None else None  # Either a dog or a booking, not both
            quantity = random.randint(1, 3)

            order_detail = OrderDetail(
                order_detail_id=str(uuid.uuid4()),
                order_id=order_id,
                dog_id=dog_id,
                booking_id=booking_id,
                quantity=quantity
            )
            order_details.append(order_detail)

        db.session.add_all(orders)
        db.session.add_all(order_details)
       

    # List of service providers
    service_providers = [
        {"service_id": 1,"user_id": 11,"name": "John Smith", "service_name": "Dog Grooming", "address": "123 Pet Street, NY", "hourly_rate": 500, "experience": "5 years", "description": "Professional dog grooming services.", "status": ServiceProviderStatus.ACCEPTED, "document_folder": "static/documents/john_smith_docs"},
        {"service_id": 2,"user_id": 12,"name": "Emily Davis", "service_name": "Veterinary Care", "address": "456 Healthy Pets Ave, CA", "hourly_rate": 1000, "experience": "8 years", "description": "Certified veterinary specialist.", "status": ServiceProviderStatus.ACCEPTED, "document_folder": "static/documents/emily_davis_docs"},
        {"service_id": 3,"user_id": 13,"name": "Michael Johnson", "service_name": "Pet Sitting", "address": "789 Cozy Lane, TX", "hourly_rate": 300, "experience": "3 years", "description": "Reliable pet sitting service at your home.", "status": ServiceProviderStatus.ACCEPTED, "document_folder": "static/documents/michael_johnson_docs"},
        {"service_id": 4,"user_id": 14,"name": "Sarah Brown", "service_name": "Dog Training", "address": "101 Training Blvd, FL", "hourly_rate": 700, "experience": "6 years", "description": "Expert in obedience and behavior training.", "status": ServiceProviderStatus.ACCEPTED, "document_folder": "static/documents/sarah_brown_docs"},
        {"service_id": 5,"user_id": 15,"name": "David Wilson", "service_name": "Pet Boarding", "address": "202 Safe Haven, IL", "hourly_rate": 600, "experience": "4 years", "description": "Safe and comfortable boarding services.", "status": ServiceProviderStatus.ACCEPTED, "document_folder": "static/documents/david_wilson_docs"},
        {"service_id": 6,"user_id": 16,"name": "Jessica Taylor", "service_name": "Pet Photography", "address": "303 Pawsome St, CO", "hourly_rate": 800, "experience": "7 years", "description": "Professional pet photography sessions.", "status": ServiceProviderStatus.ACCEPTED, "document_folder": "static/documents/jessica_taylor_docs"},
        {"service_id": 7,"user_id": 17,"name": "Daniel Martinez", "service_name": "Dog Walking", "address": "404 Walkway, WA", "hourly_rate": 200, "experience": "2 years", "description": "Daily walks for dogs of all sizes.", "status": ServiceProviderStatus.ACCEPTED, "document_folder": "static/documents/daniel_martinez_docs"},
        {"service_id": 8,"user_id": 18,"name": "Laura Anderson", "service_name": "Pet Grooming", "address": "505 Fluffy Road, NJ", "hourly_rate": 550, "experience": "4 years", "description": "Affordable and friendly pet grooming.", "status": ServiceProviderStatus.ACCEPTED, "document_folder": "static/documents/laura_anderson_docs"},
        {"service_id": 9,"user_id": 19,"name": "Robert King", "service_name": "Exotic Pet Care", "address": "606 Wild Ave, OR", "hourly_rate": 1200, "experience": "9 years", "description": "Specialized care for exotic pets.", "status": ServiceProviderStatus.ACCEPTED, "document_folder": "static/documents/robert_king_docs"},
        {"service_id": 10,"user_id": 122,"name": "Sophia Lopez", "service_name": "Dog Training", "address": "707 Bark Lane, GA", "hourly_rate": 750, "experience": "5 years", "description": "Puppy training and behavior correction.", "status": ServiceProviderStatus.ACCEPTED, "document_folder": "static/documents/sophia_lopez_docs"},
        {"service_id": 11,"user_id": 133,"name": "Ethan Parker", "service_name": "Pet Taxi", "address": "808 Ride Blvd, TX", "hourly_rate": 350, "experience": "3 years", "description": "Safe transportation for your pets.", "status": ServiceProviderStatus.ACCEPTED, "document_folder": "static/documents/ethan_parker_docs"},
        {"service_id": 12,"user_id": 144,"name": "Olivia Hall", "service_name": "Dog Therapy", "address": "909 Calm St, MA", "hourly_rate": 950, "experience": "6 years", "description": "Therapeutic sessions for dogs with anxiety.", "status": ServiceProviderStatus.ACCEPTED, "document_folder": "static/documents/olivia_hall_docs"},
        {"service_id": 13,"user_id": 155,"name": "Lucas Scott", "service_name": "Pet Rehabilitation", "address": "1001 Heal Dr, AZ", "hourly_rate": 1100, "experience": "10 years", "description": "Rehabilitation services for injured pets.", "status": ServiceProviderStatus.ACCEPTED, "document_folder": "static/documents/lucas_scott_docs"},
        {"service_id": 14,"user_id": 166,"name": "Ella Walker", "service_name": "Pet Nutritionist", "address": "1112 Wellness Rd, CA", "hourly_rate": 900, "experience": "7 years", "description": "Customized diet plans for pets.", "status": ServiceProviderStatus.ACCEPTED, "document_folder": "static/documents/ella_walker_docs"},
        {"service_id": 15,"user_id": 177,"name": "Henry Carter", "service_name": "Fish Tank Maintenance", "address": "1213 Aqua St, NY", "hourly_rate": 450, "experience": "5 years", "description": "Aquarium cleaning and maintenance.", "status": ServiceProviderStatus.ACCEPTED, "document_folder": "static/documents/henry_carter_docs"}
    ]

    dogs = [
        {
            "name": "Leo",
            "breed": "Shiba Inu",
            "age": "Young",
            "price": 9500,
            "image": "static/images/shibainu.jpg",
            "vaccinated": "Yes",
            "description": "Leo is an energetic and intelligent Shiba Inu who loves to explore. With his playful nature and strong personality, he's perfect for active owners."
        },
        {
            "name": "Jasper",
            "breed": "Alaskan Malamute",
            "age": "Adult",
            "price": 13000,
            "image": "static/images/alaskanMalamute.jpg",
            "vaccinated": "Yes",
            "description": "Jasper is a strong and friendly Alaskan Malamute. He enjoys cold weather, long hikes, and spending time with his family."
        },
        {
            "name": "Penny",
            "breed": "Papillon",
            "age": "Young",
            "price": 6700,
            "image": "static/images/papillon.jpg",
            "vaccinated": "No",
            "description": "Penny is a small but lively Papillon with a friendly and affectionate personality. She loves to play and is highly trainable."
        },
        {
            "name": "Benny",
            "breed": "Basset Hound",
            "age": "Adult",
            "price": 7700,
            "image": "static/images/bassethound.jpg",
            "vaccinated": "Yes",
            "description": "Benny is a calm and lovable Basset Hound. With his droopy ears and soulful eyes, he's perfect for families who love gentle and affectionate dogs."
        },
        {
            "name": "Nova",
            "breed": "Cane Corso",
            "age": "Mature",
            "price": 13700,
            "image": "static/images/caneCorso.jpg",
            "vaccinated": "Yes",
            "description": "Nova is a powerful and protective Cane Corso, perfect for experienced dog owners looking for a loyal guardian."
        },
        {
            "name": "Hazel",
            "breed": "Irish Setter",
            "age": "Adult",
            "price": 8800,
            "image": "static/images/irishSetter.jpg",
            "vaccinated": "No",
            "description": "Hazel is a graceful and energetic Irish Setter, known for her affectionate personality and love for running in open fields."
        },
        {
            "name": "Rusty",
            "breed": "Weimaraner",
            "age": "Young",
            "price": 9200,
            "image": "static/images/weimaraner.jpg",
            "vaccinated": "Yes",
            "description": "Rusty is a sleek and athletic Weimaraner, always ready for adventure. He’s a great companion for active families."
        },
        {
            "name": "Sky",
            "breed": "Newfoundland",
            "age": "Senior",
            "price": 15500,
            "image": "static/images/newfoundland.jpg",
            "vaccinated": "Yes",
            "description": "Sky is a gentle and loving Newfoundland, known for his calm demeanor and excellent swimming ability. Great for families with kids."
        }
    ]
    #Create users with specific UUIDs first
    user_map = {}
    for provider in service_providers:
        user_id = str(provider["user_id"])
        if not User.query.get(user_id):
            user = User(
                user_id=user_id,  # Use the ID from service provider
                user_name=f"provider_{provider['service_id']}",
                email_id=f"provider{provider['service_id']}@example.com",
                password=generate_password_hash("password123"),
                user_type="Service Provider"
            )
            db.session.add(user)
            user_map[provider["service_id"]] = user_id
    
    db.session.commit()

    if ServiceProvider.query.count() == 0:
        for provider in service_providers:
            new_provider = ServiceProvider(
                service_id=provider["service_id"],
                user_id=provider["user_id"],
                name=provider["name"],
                service_name=provider["service_name"],
                address=provider["address"],
                hourly_rate=provider["hourly_rate"],
                experience=provider["experience"],
                description=provider["description"],
                status=provider["status"],
                document_folder=provider["document_folder"]
            )
            db.session.add(new_provider)
        print("Service providers added successfully!")
        
        for dog in dogs:
            new_dog = Dogs(**dog)
            db.session.add(new_dog)
        
        db.session.commit()
        print("Database seeded successfully!")
            
def get_revenue_data():
    """
    Fetches revenue insights using raw SQL queries.
    """
    with app.app_context():
        # Total revenue
        total_revenue = db.session.execute(text("SELECT SUM(service_price) FROM booking_detail")).scalar() or 0
        # Most frequently booked service
        most_booked_service = db.session.execute(
            text("SELECT service_name FROM booking_detail GROUP BY service_name ORDER BY COUNT(booking_detail_id) DESC LIMIT 1")
        ).scalar()
        # Least frequently booked service
        least_booked_service = db.session.execute(
            text("SELECT service_name FROM booking_detail GROUP BY service_name ORDER BY COUNT(booking_detail_id) ASC LIMIT 1")
        ).scalar()
        # Revenue generated by each service
        service_revenue = db.session.execute(
            text("SELECT service_name, SUM(service_price) AS total_revenue FROM booking_detail GROUP BY service_name ORDER BY total_revenue DESC")
        ).fetchall()
        # Formatting the result
        revenue_per_service = {service: revenue for service, revenue in service_revenue}
        return {
            "total": int(total_revenue),
            "max_service": most_booked_service,
            "min_service": least_booked_service,
            "revenue_per_service": revenue_per_service
        }
    
def generate_revenue_graph():
    result = get_revenue_data()
    # Given revenue data
    revenue_per_service = result["revenue_per_service"]
    # Extract service names and revenues
    services = list(revenue_per_service.keys())
    revenues = list(revenue_per_service.values())
    
    # Plot bar chart
    plt.figure(figsize=(10, 5))
    plt.bar(services, revenues, color='skyblue')
    
    # Add labels and title
    plt.xlabel('Service')
    plt.ylabel('Revenue ($)')
    plt.title('Top 5 Revenue-Generating Services')
    plt.xticks(rotation=45)
    plt.savefig('static/revenue_graph.png')
    plt.close()




def get_stacked_revenue_data():
    try:
        # No app.app_context() here - it's already in an app context when called from a route
        revenue_query = (
            db.session.query(
                func.strftime('%Y-%m', Booking.booking_date).label('month'),
                BookingDetail.service_name,
                func.sum(BookingDetail.service_price).label('total_revenue')
            )
            .join(Booking, BookingDetail.booking_id == Booking.booking_id)
            .group_by(func.strftime('%Y-%m', Booking.booking_date), BookingDetail.service_name)
            .order_by(func.strftime('%Y-%m', Booking.booking_date))
            .all()
        )

        # Return empty data if no results
        if not revenue_query:
            return {
                "months": [],
                "revenue_per_service": {}
            }

        # Rest of your function remains the same
        revenue_data = defaultdict(lambda: defaultdict(int))
        months_set = set()
        
        for month, service_name, total_revenue in revenue_query:
            revenue_data[service_name][month] = total_revenue
            months_set.add(month)

        months = sorted(months_set)
        
        return {
            "months": months,
            "revenue_per_service": {service: [revenue_data[service].get(m, 0) for m in months] for service in revenue_data}
        }
    except Exception as e:
        print(f"Error in get_stacked_revenue_data: {e}")
        return {"months": [], "revenue_per_service": {}}



def generate_stacked_revenue_graph():
    try:
        data = get_stacked_revenue_data()  # Fetch revenue data

        if not data or "months" not in data or "revenue_per_service" not in data:
            print("❌ No data available for the graph!")
            return

        months = data["months"]
        revenue_per_service = data["revenue_per_service"]

        services = list(revenue_per_service.keys())  # Extract service names
        month_count = len(months)

        # Initialize revenue matrix for stacking
        revenue_matrix = np.zeros((len(services), month_count))

        for i, service in enumerate(services):
            for j, month in enumerate(months):
                revenue = revenue_per_service[service].get(month, 0)  # Ensure it's a number
                if isinstance(revenue, dict):  # Fix if data is nested
                    revenue = sum(revenue.values())
                revenue_matrix[i, j] = revenue  # Store revenue

        # Create stacked bar chart
        fig, ax = plt.subplots(figsize=(12, 6))
        bottom_values = np.zeros(month_count)  # Initialize bottom for stacking

        colors = ["#3498db", "#e67e22", "#2ecc71", "#f1c40f", "#9b59b6", "#1abc9c", "#e74c3c"]

        for i, service in enumerate(services):
            ax.bar(months, revenue_matrix[i], label=service, bottom=bottom_values, color=colors[i % len(colors)])
            bottom_values += revenue_matrix[i]  # Update bottom for next stack

        ax.set_xlabel("Month")
        ax.set_ylabel("Revenue ($)")
        ax.set_title("Monthly Revenue Breakdown by Service")
        ax.legend()
        plt.xticks(rotation=45)

        # Save the generated graph
        output_path = 'static/stacked_revenue_graph.png'
        os.makedirs(os.path.dirname(output_path), exist_ok=True)  # Ensure directory exists
        plt.savefig(output_path)
        plt.close()

        print(f"✅ Graph successfully saved at: {output_path}")

    except Exception as e:
        print(f"❌ Error generating graph: {e}")

def get_booking_data():
    with app.app_context():
        sql_query = text("""
            SELECT 
                strftime('%Y', booking_date) AS year,
                strftime('%m', booking_date) AS month,
                COUNT(booking_id) AS total_bookings
            FROM booking
            GROUP BY year, month
            ORDER BY year, month;
        """)

        result = db.session.execute(sql_query).fetchall()

        # Convert result to a Pandas DataFrame
        df = pd.DataFrame(result, columns=["year", "month", "total_bookings"])

        # Convert month number to month name (Jan, Feb, etc.)
        df["month"] = df["month"].astype(int)  # Convert to integer for sorting
        df["month_name"] = df["month"].apply(lambda x: pd.to_datetime(f"2024-{x}-01").strftime("%b"))  # Get month abbreviation
        print(jsonify(df.to_dict(orient="records")))
        return df.to_dict(orient="records"), df

def generate_booking_trend():
    df = get_booking_data()[1]

    plt.figure(figsize=(10, 5))

    # Grouping by year to plot multiple lines if needed
    for year in df["year"].unique():
        yearly_data = df[df["year"] == year]
        plt.plot(yearly_data["month_name"], yearly_data["total_bookings"], marker="o", linestyle="-", label=f"Year {year}")

    # Labels and title
    plt.xlabel("Month")
    plt.ylabel("Total Bookings")
    plt.title("Monthly Booking Trends")
    plt.xticks(["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"])  # Fixed order
    plt.legend()
    plt.grid(True)
    plt.savefig('static/booking_trend.png')
    # Show plot
    plt.show()

def fetch_recent_bookings():
    with app.app_context():
        sql_query = text("""
            SELECT bd.booking_detail_id, bd.booking_id, bd.service_name, b.user_id, b.booking_date
            FROM booking_detail bd
            JOIN booking b ON bd.booking_id = b.booking_id
            ORDER BY b.booking_date DESC
            LIMIT 5;
        """)

        result = db.session.execute(sql_query)
        last_5_bookings = result.fetchall()

        user_ids = [row.user_id for row in last_5_bookings]

        if user_ids:
            user_id_placeholders = ", ".join([f":id{i}" for i in range(len(user_ids))])

            user_query = text(f"""
                SELECT user_id, user_name
                FROM user
                WHERE user_id IN ({user_id_placeholders});
            """)

            user_params = {f"id{i}": user_id for i, user_id in enumerate(user_ids)}
            user_result = db.session.execute(user_query, user_params)

            # Debugging: Print column names
            for row in user_result:
                print(row._asdict())  # ✅ Correct way to print row contents

            # Creating user mapping correctly
            user_map = {row["user_id"]: row["user_name"] for row in user_result.mappings().all()}

            final_data = [
                {
                    "user_name": row.user_id,
                    "service_name": row.service_name,
                    "booking_date": row.booking_date,
                }
                for row in last_5_bookings
            ]
        else:
            final_data = []

        return final_data



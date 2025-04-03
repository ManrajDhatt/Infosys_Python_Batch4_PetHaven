from flask import current_app
from flask_mail import Message, Mail

mail = Mail()

def send_confirmation_email(email, username, event, pet_name, pet_type, pet_age):
    with current_app.app_context():
        subject = f"🎉 Registration Confirmation for {event.title}!"

        message_body = f"""
        <div style="font-family: Arial, sans-serif; background-color: #f4f4f4; padding: 20px;">
            <div style="background-color: #ffffff; padding: 20px; border-radius: 10px; box-shadow: 0px 0px 10px rgba(0,0,0,0.1); max-width: 600px; margin: auto;">

                <h1 style="color: #4374E0; text-align: center;">🎊 {event.title} 🎊</h1>

                <p style="font-size: 16px; color: #333; text-align: center;">
                    Hi <strong>{username}</strong>,<br> 
                    You have successfully registered for <strong>{event.title}</strong>. Below are the details of your registration.
                </p>

                <!-- Two-column layout -->
                <div style="display: flex; align-items: center; justify-content: space-between; padding: 15px;">
                    <div style="width: 50%;">
                        <ul style="list-style-type: none; padding: 0; text-align: left;">
                            <li style="margin-bottom: 10px;"><strong>📅 Date:</strong> {event.date}</li>
                            <li style="margin-bottom: 10px;"><strong>📍 Location:</strong> {event.location}</li>
                            <li style="margin-bottom: 10px;"><strong>💰 Entry Fee:</strong> ₹{event.fee:.2f}</li>
                            <li style="margin-bottom: 10px;"><strong>🏆 Prizes:</strong> {event.prizes}</li>
                            <li style="margin-bottom: 10px;"><strong>✔ Eligibility:</strong> {event.eligibility}</li>
                        </ul>
                    </div>
                    <div style="width: 45%; text-align: right;">
                        <img src="{event.image_filename}" alt="Event Image" width="230" 
                             style="border-radius: 10px; box-shadow: 0px 0px 8px rgba(0,0,0,0.1);">
                    </div>
                </div>

                <p style="font-size: 14px; color: #555; text-align: center;">
                    <em>{event.description}</em>
                </p>

                <hr style="border: 1px solid #ddd; margin: 20px 0;">

                <!-- Full-width Pet Details -->
                <h2 style="color: #4374E0; text-align: center;">🐶 Your Pet Details</h2>
                <ul style="list-style-type: none; padding: 0; text-align: center;">
                    <li><strong>📛 Name:</strong> {pet_name}</li>
                    <li><strong>🦴 Type:</strong> {pet_type}</li>
                    <li><strong>🎂 Age:</strong> {pet_age} years</li>
                </ul>

                <hr style="border: 1px solid #ddd; margin: 20px 0;">

                <!-- Payment Information -->
                <h2 style="color: #4374E0; text-align: center;">💳 Payment Instructions</h2>
                <p style="text-align: center; font-size: 16px; color: #333;">
                    Please complete your payment of <strong>₹{event.fee:.2f}</strong> to confirm your participation.
                </p>

                <div style="text-align: center; margin-top: 10px;">
                    
                </div>

                <hr style="border: 1px solid #ddd; margin: 20px 0;">

                <!-- Full-width Call-to-Action (CTA) Button -->
                <div style="text-align: center; margin-top: 20px;">
                   
                </div>

                <p style="text-align: center; font-size: 14px; color: #666; margin-top: 20px;">
                    📩 If you have any questions, feel free to contact us!
                </p>

                <p style="text-align: center; font-size: 16px; font-weight: bold; color: #333;">
                    Best Regards, <br>
                    🐾 Pet Haven Team 🐾
                </p>
            </div>
        </div>
        """

        msg = Message(
            subject=subject,
            sender=current_app.config['MAIL_DEFAULT_SENDER'],
            recipients=[email],
            html=message_body
        )

        mail.send(msg)  # Send the email


def send_update_email(email, username, event):
    with current_app.app_context():
        subject = f"🔔 Update for {event.title}"

        message_body = f"""
        <div style="font-family: Arial, sans-serif; background-color: #f4f4f4; padding: 20px;">
            <div style="background-color: #ffffff; padding: 20px; border-radius: 10px; box-shadow: 0px 0px 10px rgba(0,0,0,0.1); max-width: 600px; margin: auto;">

                <h1 style="color: #4374E0; text-align: center;">🔔 {event.title} Update</h1>

                <p style="font-size: 16px; color: #333; text-align: center;">
                    Hi <strong>{username}</strong>,<br> 
                    There have been some updates to the event <strong>{event.title}</strong>. Below are the updated details.
                </p>

                <!-- Two-column layout -->
                <div style="display: flex; align-items: center; justify-content: space-between; padding: 15px;">
                    <div style="width: 50%;">
                        <ul style="list-style-type: none; padding: 0; text-align: left;">
                            <li style="margin-bottom: 10px;"><strong>📅 Date:</strong> {event.date}</li>
                            <li style="margin-bottom: 10px;"><strong>📍 Location:</strong> {event.location}</li>
                            <li style="margin-bottom: 10px;"><strong>💰 Entry Fee:</strong> ₹{event.fee:.2f}</li>
                            <li style="margin-bottom: 10px;"><strong>🏆 Prizes:</strong> {event.prizes}</li>
                            <li style="margin-bottom: 10px;"><strong>✔ Eligibility:</strong> {event.eligibility}</li>
                        </ul>
                    </div>
                    <div style="width: 45%; text-align: right;">
                        <img src="{event.image_filename}" alt="Event Image" width="230" 
                             style="border-radius: 10px; box-shadow: 0px 0px 8px rgba(0,0,0,0.1);">
                    </div>
                </div>

                <p style="font-size: 14px; color: #555; text-align: center;">
                    <em>{event.description}</em>
                </p>

                <hr style="border: 1px solid #ddd; margin: 20px 0;">

                <p style="text-align: center; font-size: 14px; color: #666; margin-top: 20px;">
                    📩 If you have any questions, feel free to contact us!
                </p>

                <p style="text-align: center; font-size: 16px; font-weight: bold; color: #333;">
                    Best Regards, <br>
                    🐾 Pet Haven Team 🐾
                </p>
            </div>
        </div>
        """

        msg = Message(
            subject=subject,
            sender=current_app.config['MAIL_DEFAULT_SENDER'],
            recipients=[email],
            html=message_body
        )

        mail.send(msg)  # Send the email


def send_reminder_email(email, username, event):
    with current_app.app_context():
        subject = f"⏰ Reminder: {event.title} is Coming Up!"

        message_body = f"""
        <div style="font-family: Arial, sans-serif; background-color: #f4f4f4; padding: 20px;">
            <div style="background-color: #ffffff; padding: 20px; border-radius: 10px; box-shadow: 0px 0px 10px rgba(0,0,0,0.1); max-width: 600px; margin: auto;">

                <h1 style="color: #4374E0; text-align: center;">⏰ {event.title} Reminder</h1>

                <p style="font-size: 16px; color: #333; text-align: center;">
                    Hi <strong>{username}</strong>,<br> 
                    This is a reminder that <strong>{event.title}</strong> is coming up soon. Below are the details of the event.
                </p>

                <!-- Event Details -->
                <div style="display: flex; align-items: center; justify-content: space-between; padding: 15px;">
                    <div style="width: 50%;">
                        <ul style="list-style-type: none; padding: 0; text-align: left;">
                            <li style="margin-bottom: 10px;"><strong>📅 Date:</strong> {event.date}</li>
                            <li style="margin-bottom: 10px;"><strong>📍 Location:</strong> {event.location}</li>
                            <li style="margin-bottom: 10px;"><strong>💰 Entry Fee:</strong> ₹{event.fee:.2f}</li>
                            <li style="margin-bottom: 10px;"><strong>🏆 Prizes:</strong> {event.prizes}</li>
                            <li style="margin-bottom: 10px;"><strong>✔ Eligibility:</strong> {event.eligibility}</li>
                        </ul>
                    </div>
                    <div style="width: 45%; text-align: right;">
                        <img src="{event.image_filename}" alt="Event Image" width="230" 
                             style="border-radius: 10px; box-shadow: 0px 0px 8px rgba(0,0,0,0.1);">
                    </div>
                </div>

                <p style="font-size: 14px; color: #555; text-align: center;">
                    <em>{event.description}</em>
                </p>

                <hr style="border: 1px solid #ddd; margin: 20px 0;">

                <p style="text-align: center; font-size: 14px; color: #666; margin-top: 20px;">
                    📩 If you have any questions, feel free to contact us!
                </p>

                <p style="text-align: center; font-size: 16px; font-weight: bold; color: #333;">
                    Best Regards, <br>
                    🐾 Pet Haven Team 🐾
                </p>
            </div>
        </div>
        """

        msg = Message(
            subject=subject,
            sender=current_app.config['MAIL_DEFAULT_SENDER'],
            recipients=[email],
            html=message_body
        )

        mail.send(msg)  # Send the email

def send_password_reset_email(email, reset_link):
    with current_app.app_context():
        sender_email = current_app.config.get('MAIL_DEFAULT_SENDER')

        subject = "🔑 Password Reset Request"

        message_body = f"""
        <div style="font-family: Arial, sans-serif; background-color: #f4f4f4; padding: 20px;">
            <div style="background-color: #ffffff; padding: 20px; border-radius: 10px; box-shadow: 0px 0px 10px rgba(0,0,0,0.1); max-width: 600px; margin: auto;">

                <h1 style="color: #4374E0; text-align: center;">🔑 Reset Your Password</h1>

                <p style="font-size: 16px; color: #333; text-align: center;">
                    Hi, <br> You have requested to reset your password. Please click the button below to set a new password:
                </p>

                <div style="text-align: center; margin-top: 20px;">
                    <a href="{reset_link}" style="background-color: #4374E0; color: #fff; padding: 10px 20px; border-radius: 5px; text-decoration: none; font-size: 16px;">
                        Reset Password
                    </a>
                </div>

                <p style="text-align: center; font-size: 14px; color: #666; margin-top: 20px;">
                    If you did not request this, please ignore this email.
                </p>

                <p style="text-align: center; font-size: 16px; font-weight: bold; color: #333;">
                    Best Regards, <br>
                    🐾 Pet Haven Team 🐾
                </p>
            </div>
        </div>
        """

        msg = Message(subject=subject, sender=sender_email, recipients=[email], html=message_body)

        mail.send(msg)  # Send the email


def send_email(subject, recipient, body):
    try:
        with current_app.app_context():
            msg = Message(
                subject=subject,
                sender=current_app.config['MAIL_DEFAULT_SENDER'],  # Fixed syntax
                recipients=[recipient]  # Use the correct parameter name
            )
            msg.body = body  # Plain text content
            
            mail.send(msg)
            print(f"Email sent successfully to {recipient}")
    except Exception as e:
        print(f"Failed to send email: {str(e)}")
# app.py
from flask import Flask, render_template, request, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
import os
from datetime import datetime
import json

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///medicare.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Email configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_USERNAME')

db = SQLAlchemy(app)
mail = Mail(app)

# Database Models
class Doctor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    specialty = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    image = db.Column(db.String(200), nullable=False)
    rating = db.Column(db.Float, nullable=False)
    reviews = db.Column(db.Integer, default=0)
    availability = db.Column(db.String(100), nullable=False)
    likes = db.Column(db.Integer, default=0)

class Service(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    icon = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, nullable=False)
    price_range = db.Column(db.String(100), nullable=False)
    likes = db.Column(db.Integer, default=0)
    long_description = db.Column(db.Text)
    procedures = db.Column(db.Text)  # JSON string
    duration = db.Column(db.String(50))
    preparation = db.Column(db.Text)
    recovery_time = db.Column(db.String(100))
    success_rate = db.Column(db.String(50))
    faqs = db.Column(db.Text)  # JSON string

class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    doctor = db.Column(db.String(100), nullable=False)
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.String(50), nullable=False)
    message = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class ContactMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    subject = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    department = db.Column(db.String(100), default='General Inquiry')
    is_urgent = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Initialize database
with app.app_context():
    db.create_all()
    
    # Add sample data if empty
    if Doctor.query.count() == 0:
        doctors = [
            Doctor(
                name='Dr. Sarah Smith',
                specialty='Cardiologist',
                description='Cardiologist with 15+ years in cardiovascular care and preventive medicine.',
                image='https://images.unsplash.com/photo-1559839734-2b71ea197ec2?auto=format&fit=crop&w=500&q=80',
                rating=4.5,
                reviews=128,
                availability='Mon, Wed, Fri: 9AM - 5PM',
                likes=124
            ),
            Doctor(
                name='Dr. Michael Johnson',
                specialty='Neurologist',
                description='Expert neurologist specializing in brain and spinal cord disorders.',
                image='https://images.unsplash.com/photo-1622253692010-333f2da6031d?auto=format&fit=crop&w=500&q=80',
                rating=4.0,
                reviews=95,
                availability='Tue, Thu, Sat: 10AM - 6PM',
                likes=98
            ),
            Doctor(
                name='Dr. Emily Williams',
                specialty='Pediatrician',
                description='Pediatrician with a passion for child wellness and development.',
                image='https://images.unsplash.com/photo-1594824476967-48c8b964273f?auto=format&fit=crop&w=500&q=80',
                rating=5.0,
                reviews=210,
                availability='Mon-Fri: 8AM - 4PM',
                likes=156
            )
        ]
        db.session.bulk_save_objects(doctors)
        db.session.commit()
    
    if Service.query.count() == 0:
        services = [
            Service(
                name='Cardiology',
                icon='fas fa-heartbeat',
                description='Comprehensive heart care including diagnostics, treatment, and rehabilitation.',
                price_range='150-500',
                likes=245,
                long_description='Our cardiology department provides state-of-the-art care for all heart conditions. We offer advanced diagnostic tools, minimally invasive procedures, and comprehensive rehabilitation programs.',
                procedures=json.dumps([
                    'Electrocardiogram (ECG)',
                    'Echocardiogram',
                    'Stress Testing',
                    'Cardiac Catheterization',
                    'Angioplasty and Stenting'
                ]),
                duration='30-90 minutes depending on procedure',
                preparation='Fasting for 8 hours before most tests',
                recovery_time='Varies from same-day to several weeks',
                success_rate='95% for most procedures',
                faqs=json.dumps([
                    {
                        'question': 'How often should I get my heart checked?',
                        'answer': 'Adults over 40 should have annual heart checkups, or more frequently if risk factors exist.'
                    },
                    {
                        'question': 'Are these procedures covered by insurance?',
                        'answer': 'Most diagnostic and therapeutic procedures are covered, but check with your provider.'
                    }
                ])
            ),
            Service(
                name='Neurology',
                icon='fas fa-brain',
                description='Diagnosis and treatment of brain and nervous system disorders.',
                price_range='200-600',
                likes=189,
                long_description='Our neurology specialists provide expert care for conditions affecting the brain, spinal cord, and peripheral nerves using the latest diagnostic and treatment technologies.',
                procedures=json.dumps([
                    'EEG (Electroencephalogram)',
                    'EMG (Electromyography)',
                    'Nerve Conduction Studies',
                    'Botulinum Toxin Therapy',
                    'Deep Brain Stimulation'
                ]),
                duration='45-120 minutes',
                preparation='Some tests require no special preparation',
                recovery_time='Typically minimal',
                success_rate='Varies by condition (80-95%)',
                faqs=json.dumps([
                    {
                        'question': 'What are signs I should see a neurologist?',
                        'answer': 'Persistent headaches, dizziness, numbness, or movement problems warrant evaluation.'
                    }
                ])
            )
        ]
        db.session.bulk_save_objects(services)
        db.session.commit()

# Routes
@app.route('/')
def home():
    doctors = Doctor.query.all()
    testimonials = [
        {
            'text': 'The care I received at MediCare was exceptional. Dr. Smith took the time to explain everything clearly.',
            'author': 'Rahul Sharma',
            'rating': 5
        },
        {
            'text': 'Clean facility and friendly staff. My appointment was on time and the doctor was very thorough.',
            'author': 'Priya Patel',
            'rating': 4
        },
        {
            'text': 'The pediatric department is amazing with kids. My daughter actually looks forward to her checkups!',
            'author': 'Anjali Mehta',
            'rating': 5
        }
    ]
    return render_template('hospital.html', doctors=doctors, testimonials=testimonials)

@app.route('/doctors')
def doctors():
    doctors = Doctor.query.all()
    return render_template('doctors.html', doctors=doctors)

@app.route('/services')
def services():
    services = Service.query.all()
    return render_template('services.html', services=services)

@app.route('/contact')
def contact():
    departments = [
        {'name': 'Appointments', 'icon': 'fas fa-calendar-check'},
        {'name': 'Billing', 'icon': 'fas fa-file-invoice-dollar'},
        {'name': 'Medical Records', 'icon': 'fas fa-file-medical'},
        {'name': 'General Inquiry', 'icon': 'fas fa-question-circle'},
        {'name': 'Feedback', 'icon': 'fas fa-comment-alt'}
    ]
    
    faqs = [
        {
            'question': 'How do I schedule an appointment?',
            'answer': 'You can schedule an appointment online through our website, by calling our office, or by visiting in person.'
        },
        {
            'question': 'What insurance plans do you accept?',
            'answer': 'We accept most major insurance plans. Please contact our billing department for specific information about your plan.'
        },
        {
            'question': 'What should I bring to my first appointment?',
            'answer': 'Please bring your insurance card, photo ID, list of current medications, and any relevant medical records.'
        },
        {
            'question': 'Do you offer telehealth services?',
            'answer': 'Yes, we offer telehealth services for many types of appointments. Please call to see if your visit can be conducted virtually.'
        }
    ]
    
    return render_template('contact.html', departments=departments, faqs=faqs)

# API Routes
@app.route('/api/appointment', methods=['POST'])
def create_appointment():
    try:
        data = request.get_json()
        
        appointment = Appointment(
            name=data['name'],
            email=data['email'],
            phone=data['phone'],
            doctor=data['doctor'],
            date=datetime.strptime(data['date'], '%Y-%m-%d'),
            time=data['time'],
            message=data.get('message', '')
        )
        
        db.session.add(appointment)
        db.session.commit()
        
        # Send confirmation email
        msg = Message('Appointment Confirmation - MediCare',
                     recipients=[data['email']])
        msg.body = f"""
        Dear {data['name']},
        
        Thank you for booking an appointment with MediCare.
        
        Appointment Details:
        - Doctor: {data['doctor']}
        - Date: {data['date']}
        - Time: {data['time']}
        
        We will contact you shortly to confirm your appointment.
        
        Best regards,
        MediCare Team
        """
        
        mail.send(msg)
        
        return jsonify({'success': True, 'message': 'Appointment booked successfully!'})
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400

@app.route('/api/contact', methods=['POST'])
def submit_contact():
    try:
        data = request.get_json()
        
        contact_message = ContactMessage(
            name=data['name'],
            email=data['email'],
            subject=data['subject'],
            message=data['message'],
            department=data.get('department', 'General Inquiry'),
            is_urgent=data.get('is_urgent', False)
        )
        
        db.session.add(contact_message)
        db.session.commit()
        
        # Send notification email
        msg = Message(f'New Contact Message: {data["subject"]}',
                     recipients=['admin@medicare.com'])
        msg.body = f"""
        New contact message received:
        
        From: {data['name']} ({data['email']})
        Department: {data.get('department', 'General Inquiry')}
        Subject: {data['subject']}
        Urgent: {'Yes' if data.get('is_urgent', False) else 'No'}
        
        Message:
        {data['message']}
        """
        
        mail.send(msg)
        
        return jsonify({'success': True, 'message': 'Message sent successfully!'})
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400

@app.route('/api/doctor/<int:doctor_id>/like', methods=['POST'])
def like_doctor(doctor_id):
    try:
        doctor = Doctor.query.get_or_404(doctor_id)
        doctor.likes += 1
        db.session.commit()
        
        return jsonify({'success': True, 'likes': doctor.likes})
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400

@app.route('/api/service/<int:service_id>/like', methods=['POST'])
def like_service(service_id):
    try:
        service = Service.query.get_or_404(service_id)
        service.likes += 1
        db.session.commit()
        
        return jsonify({'success': True, 'likes': service.likes})
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True)
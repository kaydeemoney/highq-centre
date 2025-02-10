from flask import Flask, Blueprint, render_template, request, redirect, url_for, flash, session
from flask_wtf import FlaskForm
from PIL import Image
from flask_sqlalchemy import SQLAlchemy
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField, DateField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo, Optional
import uuid, json
from config import Config
from datetime import datetime, timedelta
#this is for the validation efficiency of the wtf form you must always include it
from flask_wtf.csrf import CSRFProtect
from sqlalchemy.exc import IntegrityError
import os
from werkzeug.utils import secure_filename
from PIL import Image, ImageDraw

app = Flask(__name__, static_folder='static')
app.config.from_object(Config)
db = SQLAlchemy(app)

UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
MAX_CONTENT_LENGTH = 300 * 1024  # 300KB
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH


#wtf form validation, for form input sending
csrf = CSRFProtect(app)
app.config['WTF_CSRF_ENABLED'] = True
app.config['WTF_CSRF_SECRET_KEY'] = '7caa483b-e1c7-4a65-b901-beae2633e028'

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

#model definition for the database
class student_info(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(50), nullable=False)
    secondname = db.Column(db.String(50), nullable=False)
    surname = db.Column(db.String(50), nullable=False)
    course_enrolled = db.Column(db.String(50), nullable=False)
    linkedin_url = db.Column(db.String(100))
    phone = db.Column(db.String(15), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    address = db.Column(db.String(200), nullable=False)
    password = db.Column(db.String(60), nullable=False)
    profile_pic_name = db.Column(db.String(50), nullable=False)
    student_status = db.Column(db.String(50), nullable=False)
    student_level = db.Column(db.String(50), nullable=False)
    date_created = db.Column(db.String(50), nullable=False)
    grad_date = db.Column(db.String(50), nullable=False)
    student_task_id = db.Column(db.String(50), nullable=False)

class admin_info(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    admin_id = db.Column(db.String(50), nullable=False)
    admin_name = db.Column(db.String(50), nullable=False)
    phone = db.Column(db.String(15), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    address = db.Column(db.String(200), nullable=False)
    password = db.Column(db.String(60), nullable=False)
    date_created = db.Column(db.String(50), nullable=False)

class project_table(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.String(50), nullable=False)
    project_title = db.Column(db.String(500), nullable=False)
    project_keywords = db.Column(db.String(500), nullable=False)
    project_concept = db.Column(db.String(500), nullable=False)
    project_resources = db.Column(db.String(500), nullable=False)
    project_requirements = db.Column(db.String(500), nullable=False)
    project_objectives = db.Column(db.String(500), nullable=False)
    course_enrolled = db.Column(db.String(50), nullable=False)
    date_created = db.Column(db.String(50), nullable=False)
    deadline=db.Column(db.String(50), nullable=False)
    public = db.Column(db.Integer, nullable=True)
    

class theory_questions(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.String(100), nullable=False)
    course_enrolled = db.Column(db.String(100), nullable=False)
    deadline = db.Column(db.Date, nullable=False)
    question = db.Column(db.String(500), nullable=False) 
    
class objective_questions(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.String(100), nullable=False)
    course_enrolled = db.Column(db.String(100), nullable=False)
    deadline = db.Column(db.Date, nullable=False)
    question = db.Column(db.String(500), nullable=False)  # Setting size to 500
    opt_a = db.Column(db.String(500), nullable=False)
    opt_b = db.Column(db.String(500), nullable=False)
    opt_c = db.Column(db.String(500), nullable=False)
    opt_d = db.Column(db.String(500), nullable=False)
    answer = db.Column(db.String(500), nullable=False)  # Assuming answer is one of 'A', 'B', 'C', 'D'

class notifications(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_task_id = db.Column(db.String(50), nullable=False)
    message = db.Column(db.String(500), nullable=False)
    status = db.Column(db.String(10), nullable=False)
    note_type = db.Column(db.String(10), nullable=False)
    date_created = db.Column(db.Date, nullable=False)
    
#models definition for student registration form
class Student_reg_form(FlaskForm):
    firstname= StringField('firstname', validators=[DataRequired(), Length(min=5, max =50)])
    secondname= StringField('secondname', validators=[DataRequired(), Length(min=5, max =50)])
    surname= StringField('surname', validators=[DataRequired(), Length(min=5, max =50)])
    course_enrolled = SelectField('Course You Want to Enroll', choices=[
        ('facebook-marketing', 'Facebook Marketing'),
        ('instagram-marketing', 'Instagram Marketing'),
        ('twitter-marketing', 'Twitter Marketing'),
        ('email-marketing', 'Email Marketing')])
    linkedin_url= StringField('linkedin_url', validators=[DataRequired(), Length(min=5, max =50)])
    phone= StringField('phone', validators=[DataRequired(), Length(min=11, max =12)])
    email= StringField('email', validators=[DataRequired(), Length(min=5, max =50)])
    address= StringField('address', validators=[DataRequired(), Length(min=5, max =80)])
    password = PasswordField('password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('SUBMIT!')


class NotificationForm(FlaskForm):
    filtering = SelectField('Filter By',
        choices=[
            ('course', 'Course'),
            ('student', 'Student Name'),
            ('all', 'All Students')
        ],
        validators=[DataRequired()]
    )
    course = SelectField(
        'Select Course',
        choices=[
            ('facebook-marketing', 'Facebook Marketing'),
            ('instagram-marketing', 'Instagram Marketing'),
            ('twitter-marketing', 'Twitter Marketing'),
            ('email-marketing', 'Email Marketing')
        ],
        validators=[Optional()]  # Optional because it depends on the filter
    )
    student_name = StringField('Student Name', validators=[Optional()])
    notification = TextAreaField('Post Notification', validators=[DataRequired()])
    submit = SubmitField('Post Notification')




class ManageStudentForm(FlaskForm):
    filtering = SelectField('Filter By',
        choices=[
            ('all', 'All Students'),
            ('course', 'Course'),
            ('student', 'Student Name')
            
        ],
        validators=[DataRequired()]
    )
    course = SelectField(
        'Select Course',
        choices=[
            ('facebook-marketing', 'Facebook Marketing'),
            ('instagram-marketing', 'Instagram Marketing'),
            ('twitter-marketing', 'Twitter Marketing'),
            ('email-marketing', 'Email Marketing')
        ],
        validators=[Optional()]  # Optional because it depends on the filter
    )
    student_name = StringField('Student Name', validators=[Optional()])
    
    submit = SubmitField('Search For Student')

#models definition for admin registration form
class Admin_reg_form(FlaskForm):
    admin_name= StringField('Full Name', validators=[DataRequired(), Length(min=5, max =50)])
    phone= StringField('phone', validators=[DataRequired(), Length(min=11, max =12)])
    email= StringField('email', validators=[DataRequired(), Length(min=5, max =50)])
    address= StringField('address', validators=[DataRequired(), Length(min=5, max =80)])
    password = PasswordField('password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('sign up!')

#admin initial upload page model, was done so the details of the id and all can be transferred
class ProjectUploadForm(FlaskForm):
    course_enrolled = SelectField('Course Enrolled', choices=[
        ('facebook-marketing', 'Facebook Marketing'),
        ('instagram-marketing', 'Instagram Marketing'),
        ('twitter-marketing', 'Twitter Marketing'),
        ('email-marketing', 'Email Marketing')],
        validators=[DataRequired()])
    project_title = StringField('Project Title', validators=[DataRequired()])
    project_keywords = TextAreaField('Include Keywords (....seperate them by commas)', validators=[DataRequired()])
    project_concept = TextAreaField('Concepts eg Stacks and queues <www.stackoverflow/stacks> (.....seperate each concept by commas)', validators=[DataRequired()])
    project_resources = TextAreaField('Resources To Watch/Read eg Linked Lists <www.highgrade/linkedlists> (....seperate them by commas)', validators=[DataRequired()])
    project_objectives = TextAreaField('Learning Objectives (....seperate them by commas)', validators=[DataRequired()])
    project_requirements = StringField('General Requirements (....seperate them by commas)', validators=[DataRequired()])
    deadline = DateField('Deadline', validators=[DataRequired()])    
    submit_theory = SubmitField('Proceed With Theory')
    submit_obj = SubmitField('Proceed With Objectives')

class Objupload(FlaskForm):
    question = StringField('Question', validators=[DataRequired()])
    opt_a = StringField('Option A', validators=[DataRequired()])
    opt_b = StringField('Option B', validators=[DataRequired()])
    opt_c = StringField('Option C', validators=[DataRequired()])
    opt_d = StringField('Option D', validators=[DataRequired()])
    answer = StringField('answer', validators=[DataRequired()])
    submit = SubmitField('submit this!')

class Theoryupload(FlaskForm):
    question = StringField('Project Tasks', validators=[DataRequired()])
    submit = SubmitField('Add')
#defining model for the student sign in form
class general_login_form(FlaskForm):
    email= StringField('email', validators=[DataRequired(), Length(min=5, max =50)])
    password = PasswordField('password', validators=[DataRequired()])
    submit = SubmitField('Login')

class quick_search_form(FlaskForm):
    student_name= StringField('Enter Student Surname For QuickSearch', validators=[DataRequired(), Length(min=5, max =50)])
    submit = SubmitField('Search')
#using a slight flash message to our student forms
#these are the routes for pages pertaining to the landing page    
@app.route("/")
def index():
    return render_template('index.html')
@app.route("/video_info_landing")
def video_info():
    return render_template('video_info.html')
@app.route("/fb_info_landing")
def fb_info():
    return render_template('fb_info.html')
@app.route("/ig_info_landing")
def ig_info():
    return render_template('ig_info.html')
@app.route("/twitter_info_landing")
def twitter_info():
    return render_template('twitter_info.html')
@app.route("/email_info_landing")
def email_info():
    return render_template('email_info.html')
#these are the routes for functions and methods i.e API
@app.route("/student_reg_page", methods=['GET', 'POST'])
def student_reg_page():
    form = Student_reg_form()
    if form.validate_on_submit():
        # Handle file upload
        file = request.files.get('file')
        if file and allowed_file(file.filename):
            # Process the file
            joint_id = uuid.uuid4()
            profile_pic_name = joint_id
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], f"{profile_pic_name}.{filename.rsplit('.', 1)[1]}")
            file.save(filepath)

            # Image processing: Make the image round (as an example)
            img = Image.open(filepath)
            img = img.convert("RGBA")
            size = (200, 200)  # Set the size of the image
            img = img.resize(size, Image.Resampling.LANCZOS)  # Correct method for Pillow 10+
            mask = Image.new("L", size, 0)
            draw = ImageDraw.Draw(mask)
            draw.ellipse((0, 0, size[0], size[1]), fill=255)
            img.putalpha(mask)

            if filename.rsplit('.', 1)[1].lower() in ['jpeg', 'jpg']:
                img = img.convert("RGB")
                filepath = os.path.splitext(filepath)[0] + ".jpg"
                img.save(filepath, "JPEG")
            else:
                img.save(filepath, "PNG")

            # Save student details in the database
            student = student_info(
                firstname=form.firstname.data,
                secondname=form.secondname.data,
                surname=form.surname.data,
                course_enrolled=form.course_enrolled.data,
                linkedin_url=form.linkedin_url.data,
                phone=form.phone.data,
                email=form.email.data,
                address=form.address.data,
                password=form.password.data,
                profile_pic_name=profile_pic_name,
                student_status="student",
                student_level="stage_1",
                date_created=datetime.now(),
                grad_date=datetime.now() + timedelta(days=90),
                student_task_id=profile_pic_name
            )

            try:
                db.session.add(student)
                db.session.commit()
                flash(f"Account created for {form.surname.data}, click to dismiss this message", 'success')
                return redirect(url_for('general_login_page'))
            except IntegrityError:
                db.session.rollback()
                flash('An error occurred while saving the student details', 'danger')
                return redirect(request.url)

        else:
            flash('Invalid file or no file selected', 'danger')
            return redirect(request.url)

    return render_template('student_reg_page.html', form=form)
@app.route("/admin_reg_page", methods=['GET', 'POST'])
def admin_reg_page():
    admin_id= uuid.uuid4()
    date_created= datetime.now()
    form = Admin_reg_form()
    if form.validate_on_submit():
        admin_name=form.admin_name.data
        phone=form.phone.data
        email=form.email.data
        address=form.address.data
        password=form.password.data
        admin = admin_info(admin_name= admin_name, phone=phone, email=email, address=address, password=password, 
        date_created=date_created, admin_id =admin_id)
        try:
            db.session.add(admin)
            db.session.commit()
            flash(f"Account Created For {{form.surname.data}}", 'success')
            return redirect(url_for('general_login_page'))
        except IntegrityError:
            # Rollback the session in case of an error
            db.session.rollback()
            return render_template('admin_reg_page.html', title="Administrator Application", form=form) 
    if not form.validate_on_submit():
        print(form.errors)
    return render_template('admin_reg_page.html', title="Administrator Application", form=form) 

@app.route("/general_login_page", methods=['GET', 'POST'])
def general_login_page():
    form = general_login_form()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        # Fetch student or admin email from the database
        got_student_email = student_info.query.filter_by(email=email).first()
        got_admin_email = admin_info.query.filter_by(email=email).first()
        # Check if the email exists in student_info
        if got_student_email:
            full_details = got_student_email
            pic_id=full_details.student_task_id
            if full_details.password == password:  # Direct password comparison
                print("going to student")
                return redirect(url_for('student_dashboard', email=form.email.data))
            else:
                flash("Invalid student credentials", "danger")
                return render_template('general_login_page.html', form=form)
        # Check if the email exists in admin_info
        elif got_admin_email:
            full_details = got_admin_email
            if full_details.password == password:  # Direct password comparison
                print("going to admin")
                return redirect(url_for('admin_dashboard'))
            else:
                flash("Invalid admin credentials", "danger")
                return render_template('general_login_page.html', form=form)       
        # If neither student nor admin email is found
        else:
            flash("Email not found", "danger")
            return render_template('general_login_page.html', form=form) 
    return render_template('general_login_page.html', form=form)

@app.route("/student_dashboard" , methods=['GET', 'POST'])
def student_dashboard():
    email = request.args.get('email')
    student_details=student_info.query.filter_by(email=email).first()
    firstname=student_details.firstname
    surname=student_details.surname
    student_status=student_details.student_status
    pic_id=student_details.student_task_id
    print(pic_id)
    uploads_folder = os.path.join(app.static_folder, 'uploads')
    path_list=os.listdir(uploads_folder)
    for file_name in path_list:
        if file_name.startswith(pic_id):
            profile_picture=file_name
            student_details.profile_pic_name=profile_picture
            db.session.commit()
        else:
            print("nothing here found")
            profile_picture="noname.png"
    return render_template('student_dashboard.html', 
    firstname=firstname, surname=surname, student_status=student_status, profile_picture=profile_picture, email=email)

@app.route("/admin_dashboard")
def admin_dashboard():
    form=quick_search_form()
    student_no = student_info.query.all()
    fb_no=student_info.query.filter_by(course_enrolled="facebook-marketing").all()
    insta_no=student_info.query.filter_by(course_enrolled="instagram-marketing").all()
    email_no=student_info.query.filter_by(course_enrolled="email-marketing").all()
    twitter_no=student_info.query.filter_by(course_enrolled="twitter-marketing").all()
    headcount=0
    fb_count=0
    insta_count=0
    email_count=0
    twitter_count=0
    for student in student_no:
        headcount+=1
    for student in fb_no:
        fb_count+=1
    for student in insta_no:
        insta_count+=1
    for student in email_no:
        email_count+=1
    for student in twitter_no:
        twitter_count+=1
    return render_template('admin_dashboard.html', headcount=headcount, fb_count=fb_count, insta_count=insta_count, email_count=email_count,
    twitter_count=twitter_count, form=form)

@app.route("/admin_proj_general_page" , methods=['GET', 'POST'])
def admin_project_upload_page():
    pid=uuid.uuid4()
    project_id=pid
    form = ProjectUploadForm()
    if form.validate_on_submit():
        project_id=project_id
        project_title=form.project_title.data
        project_keywords=form.project_keywords.data
        project_concept=form.project_concept.data
        project_resources=form.project_resources.data
        project_objectives=form.project_objectives.data
        project_requirements=form.project_requirements.data
        course_enrolled=form.course_enrolled.data
        deadline=form.deadline.data
        date_created= datetime.now()
        project_check_title=project_table.query.filter_by(project_title=project_title).first()
        project_check_course=project_table.query.filter_by(course_enrolled=course_enrolled).first()
        if (project_check_course and project_check_title):
            print("record exists, no need to add new")
        else:
            project = project_table(project_id=project_id, project_title=project_title, 
            course_enrolled=course_enrolled,deadline=deadline, date_created=date_created, project_keywords= project_keywords,
            project_concept=project_concept, project_resources=project_resources, project_objectives=project_objectives,
            project_requirements=project_requirements )
            db.session.add(project)
            db.session.commit()

        if form.submit_obj:
            return redirect(url_for('admin_obj',project_id=project_id, course_enrolled=course_enrolled, project_title=project_title, 
             deadline=deadline))
        elif form.submit_theory:
            return redirect(url_for('admin_theory', project_id=project_id, course_enrolled=course_enrolled, project_title=project_title, 
             deadline=deadline))
    return render_template('admin_proj_general_page.html', form=form) 

@app.route('/admin_obj', methods=['GET', 'POST'])
def admin_obj():
    course_enrolled = request.args.get('course_enrolled')
    deadline = request.args.get('deadline')
    project_id=request.args.get('project_id')
    project_title=request.args.get('project_title')
    proj_details=project_table.query.filter_by(project_id=project_id).first()
    if course_enrolled is None:
        course_enrolled=proj_details.course_enrolled
        deadline=proj_details.deadline
    form = Objupload()
    #the former form, for we will be needing it at the return
    default_form = ProjectUploadForm()
    if form.validate_on_submit():
        question=form.question.data
        opt_a=form.opt_a.data
        opt_b=form.opt_b.data
        opt_c=form.opt_c.data
        opt_d=form.opt_d.data
        answer=form.answer.data
        objective_question = objective_questions( project_id=project_id, course_enrolled=course_enrolled, deadline=deadline, question=question,
        opt_a=opt_a, opt_b=opt_b, opt_c=opt_c, opt_d=opt_d, answer=answer)
        try:
            db.session.add(objective_question)
            db.session.commit()
            return redirect(url_for('admin_obj', project_id=project_id, course_enrolled=course_enrolled, deadline=deadline, project_title=project_title))
        except IntegrityError:
        # Rollback the session in case of an error
            print("integrity error")
            db.session.rollback()
            return render_template('admin_obj.html', form=form)
    if not form.validate_on_submit():
        print(form.errors)
    return render_template('admin_obj.html',  form=form) 

@app.route('/admin_theory', methods=['GET', 'POST'])
def admin_theory():
    project_id=request.args.get('project_id')
    course_enrolled = request.args.get('course_enrolled')
    deadline = request.args.get('deadline')
    project_title=request.args.get('project_title')
    form = Theoryupload()
    if form.validate_on_submit():
        question=form.question.data
        theory_question = theory_questions(project_id=project_id, course_enrolled=course_enrolled, deadline=deadline,
         question=question)
        try:
            db.session.add(theory_question)
            db.session.commit()
            return redirect(url_for('admin_theory', project_id=project_id, course_enrolled=course_enrolled, deadline=deadline))
        except IntegrityError:
        # Rollback the session in case of an error
            print("integrity error")
            db.session.rollback()
            return render_template('admin_theory.html', form=form)
    if not form.validate_on_submit():
        print(form.errors)
    return render_template('admin_theory.html',  form=form)

@app.route('/admin_edit_current', methods=['GET', 'POST'])
def admin_edit_current():
    project_id=request.args.get('project_id')
    print(project_id)
    obj_project_correct=objective_questions.query.filter_by(project_id=project_id).all()
    theory_project_correct=theory_questions.query.filter_by(project_id=project_id).all()
    for bad_question in obj_project_correct:
        question_to_correct= bad_question.question
        opt_a_edit=bad_question.opt_a
        opt_b_edit=bad_question.opt_b
        opt_c_edit=bad_question.opt_c
        opt_d_edit=bad_question.opt_d
        answer_edit=bad_question.answer

    for bad_theory in theory_project_correct:
        theory_edit=bad_theory.question
    return render_template('admin_edit_current.html', obj_project_correct=obj_project_correct, theory_project_correct=theory_project_correct) 

@app.route('/admin_delete_single_q', methods=['GET', 'POST'])
def admin_delete_single_q():
    project_id=request.args.get('project_id')
    project_correct=objective_questions.query.filter_by(project_id=project_id).all()
    bad_id=request.args.get('bad_id')
    question_to_delete=objective_questions.query.filter_by(id=bad_id).first()
    try:     
        db.session.delete(question_to_delete)
        db.session.commit()
        return redirect(url_for('admin_edit_current', project_id=project_id))
    except Exception as e:
        db.session.rollback()
        return f"An error occurred: {e}", 500
    return render_template('admin_edit_current.html', project_correct=project_correct) 

@app.route('/admin_edit_uploaded', methods=['GET', 'POST'])
def admin_edit_uploaded():
    uploaded_project=project_table.query.all()
    return render_template('admin_edit_uploaded.html', uploaded_project=uploaded_project) 

@app.route('/admin_delete_full', methods=['GET', 'POST'])
def admin_delete_full():
    project_id=request.args.get('project_id')
    project_to_delete=objective_questions.query.filter_by(project_id=project_id).all()
    title_to_delete=project_table.query.filter_by(project_id=project_id).all()
    try:
        for project in project_to_delete:
            db.session.delete(project)
        for project_title in title_to_delete:
            db.session.delete(project_title)
        db.session.commit()
        uploaded_project=project_table.query.all()
        return redirect(url_for('admin_edit_uploaded', uploaded_project=uploaded_project))
    except Exception as e:
        db.session.rollback()
        return render_template('admin_theory.html')
    return render_template('admin_edit_uploaded.html', project_correct=project_correct) 

@app.route('/edit_question_and_ans', methods=['GET', 'POST'])
def edit_question_and_ans():
    form=Objupload()
    project_id=request.args.get('project_id')
    bad_id=request.args.get('bad_id')
    question_to_edit=objective_questions.query.filter_by(id=bad_id).first()
    return render_template('admin_form_correction.html', question_to_edit=question_to_edit,
     project_id=project_id, bad_id=bad_id,form=form)

@app.route('/admin_submit_correction', methods=['GET', 'POST'])
def admin_submit_correction():
    if request.method == 'POST':
        project_id = request.args.get('project_id')  # From the query parameter
        bad_id=request.args.get('bad_id')
        question = request.form.get('question')
        opt_a = request.form.get('opt_a')
        opt_b = request.form.get('opt_b')
        opt_c = request.form.get('opt_c')
        opt_d = request.form.get('opt_d')
        answer = request.form.get('answer')
        new_question=objective_questions.query.filter_by(id=bad_id).first()
        new_question.question=question
        new_question.opt_a=opt_a
        new_question.opt_b=opt_b
        new_question.opt_c=opt_c
        new_question.opt_d=opt_d
        new_question.answer=answer
        project_correct=objective_questions.query.filter_by(project_id=project_id).all()
        try:
            db.session.commit()
            return render_template('admin_edit_current.html', project_correct=project_correct) 
        except Exception as e:
            db.session.rollback()
    return redirect(url_for('admin_project_upload_page'))  # Redirect for GET requests




@app.route('/edit_theory', methods=['GET', 'POST'])
def edit_theory():
    form=Theoryupload()
    project_id=request.args.get('project_id')
    bad_id=request.args.get('bad_id')
    question_to_edit=theory_questions.query.filter_by(id=bad_id).first()
    return render_template('theory_correction.html', question_to_edit=question_to_edit,
     project_id=project_id, bad_id=bad_id,form=form)

@app.route("/theory_submit_correction" , methods=['GET', 'POST'])
def theory_submit_correction():
    if request.method == 'POST':
        project_id=request.args.get('project_id')
        bad_id=request.args.get('bad_id')
        correction = request.form.get('question')
        affected_question=theory_questions.query.filter_by(id=bad_id).first()
        try:
            affected_question.question=correction
            db.session.commit()
            return redirect(url_for('admin_edit_current', project_id=project_id))
        except IntegrityError:
        # Rollback the session in case of an error
            print("integrity error")
            db.session.rollback()
    return render_template('admin_dashboard.html')



@app.route('/delete_theory_question', methods=['GET', 'POST'])
def delete_theory_question():
    project_id=request.args.get('project_id')
    project_correct=objective_questions.query.filter_by(project_id=project_id).all()
    bad_id=request.args.get('bad_id')
    question_to_delete=theory_questions.query.filter_by(id=bad_id).first()
    try:     
        db.session.delete(question_to_delete)
        db.session.commit()
        return redirect(url_for('admin_edit_current', project_id=project_id))
    except Exception as e:
        db.session.rollback()
        return f"An error occurred: {e}", 500
    return render_template('admin_edit_current.html', project_correct=project_correct) 

@app.route('/add_more_to_present', methods=['GET', 'POST'])
def add_more_to_present():
    project_id=request.args.get('project_id')
    project_type=request.args.get('project_type')
    project_details=project_table.query.filter_by(project_id=project_id).first()
    course_enrolled=project_details.course_enrolled
    project_title=project_details.project_title
    deadline=project_details.deadline

    if project_type=="obj":
        return redirect(url_for('admin_obj',project_id=project_id, course_enrolled=course_enrolled, project_title=project_title, 
             deadline=deadline))
    elif project_type=="theory":
        return redirect(url_for('admin_theory',project_id=project_id, course_enrolled=course_enrolled, project_title=project_title, 
             deadline=deadline))

@app.route("/notification", methods=["GET", "POST"])
def notification():
    # For GET: Populate JSON for student names
    std_details = student_info.query.all()
    student_full = [f"{s.firstname} {s.surname}" for s in std_details]
    with open("static/data.json", "w") as json_file:
        json.dump(student_full, json_file)
    return render_template('notification.html', form=NotificationForm())

@app.route("/notification_action", methods=["GET", "POST"])
def notification_action():
    if request.method == 'POST':
        filtering = request.form.get('filtering')
        course = request.form.get('course')
        student_name = request.form.get('student_name')
        notification = request.form.get('notification')
        date_created= datetime.now()
        if filtering == "all":
            all_student = student_info.query.all()
            for student_id in all_student:
                each_student_id=student_id.student_task_id
                present_state = notifications.query.filter_by(student_task_id=each_student_id).first()
                # we will not need to use session.add whever we are just updating a record, to avoid confusion
                # and also we wont need to have an instance of the whole code again, just what we wanna correct
                if present_state:
                    old_message=present_state.message
                    message=old_message+">"+notification
                    present_state.message=message
                    db.session.commit()
                else:
                    message = notification
                    data= notifications(student_task_id=each_student_id, message=message, status="project", note_type="general", date_created=date_created)
                    db.session.add(data)
                    db.session.commit()
                flash(f"Notification Added Successfully")
                return redirect(url_for('admin_dashboard'))
            
        elif filtering == "student":
            name_filter=student_name.split(" ")
            firstname = name_filter[0]
            surname = name_filter[1]
            student_row = student_info.query.filter(student_info.firstname == firstname,
            student_info.surname == surname).first()
            each_student_id = student_row.student_task_id
            present_state = notifications.query.filter_by(student_task_id=each_student_id).first()
            if present_state:
                old_message=present_state.message
                message=old_message+">"+notification
                present_state.message=message
                db.session.commit()
            else:
                message = notification
                data= notifications(student_task_id=each_student_id, message=message, status="project", note_type="general", date_created=date_created)
                db.session.add(data)
                db.session.commit()
            flash("added for " + surname + " " + firstname)
            return redirect(url_for('admin_dashboard'))
        else:
            student_row=student_info.query.filter_by(course_enrolled=course).all()
            for student in student_row:
                each_student_id = student.student_task_id
                present_state = notifications.query.filter_by(student_task_id=each_student_id).first()
                if present_state:
                    old_message=present_state.message
                    message=old_message+">"+notification
                    present_state.message=message
                    db.session.commit()
                else:
                    message = notification
                    data= notifications(student_task_id=each_student_id, message=message, status="project", note_type="general", date_created=date_created)
                    db.session.add(data)
                    db.session.commit()
            
            flash("posted successfully for " + course )
            return redirect(url_for('admin_dashboard'))
            
        return "Notification posted successfully!"
    else:
        return "an error occured"

@app.route("/admin_student_edit", methods=["GET", "POST"])
def admin_student_edit():
    course = request.args.get('course') 
    student_list=student_info.query.filter_by(course_enrolled=course).all()
    return render_template('admin_student_edit.html', student_list=student_list, course=course)

@app.route("/delete_module", methods=["GET", "POST"])
def delete_module():
    if request.method == 'GET':
        student_id = request.args.get('student_id')
        student_list = request.args.get('student_list')
        course=request.args.get('course')
        student_to_delete=student_info.query.filter_by(student_task_id=student_id).first()
        try:     
            db.session.delete(student_to_delete)
            db.session.commit()
            return redirect(url_for('admin_student_edit', course=course))
        except Exception as e:
            db.session.rollback()
            return f"An error occurred: {e}", 500
        return redirect(url_for('admin_student_edit', course=course))
    return "something went wrong"
@app.route("/admin_student_display", methods=["GET", "POST"])
def admin_student_display():
    if request.method == 'GET':
        student_id = request.args.get('student_id')
        student_details=student_info.query.filter_by(student_task_id=student_id).first()
        if student_details:
            firstname=student_details.firstname
            surname=student_details.surname
            secondname=student_details.secondname
            course_enrolled=student_details.course_enrolled
            linkedin_url=student_details.linkedin_url
            phone=student_details.phone
            address=student_details.address
            profile_pic_name=student_details.profile_pic_name
            student_status=student_details.student_status
            student_level=student_details.student_level
            date_created=student_details.date_created
            grad_date=student_details.grad_date
            return render_template('student_profile_edit_page.html', firstname=firstname, secondname=secondname, surname=surname,
            course_enrolled=course_enrolled, linkedin_url=linkedin_url, phone=phone, address=address, profile_pic_name=profile_pic_name,
            student_status=student_status, student_level=student_level, date_created=date_created, grad_date=grad_date)
            

@app.route('/student_profile_route', methods=['GET', 'POST'])
def student_profile_route():

    if request.method == 'POST':
        student_name=request.form.get('student_name')
        firstname=student_name.split(" ")[0]
        surname=student_name.split(" ")[1]
        exact_match= student_info.query.filter_by(firstname=firstname, surname=surname).first()
        if exact_match:
            student_id_details=exact_match
        else:
            print("couldnt find this record")

    else:
        email = request.args.get('email')
        if not email:
            return "Email is required to view the profile.", 400
        student_id_details = student_info.query.filter_by(email=email).first()
        if not student_id_details:
            return f"No student found with email: {email}", 404
    
    form = Student_reg_form()
    firstname = student_id_details.firstname
    secondname = student_id_details.secondname
    surname = student_id_details.surname
    course_enrolled = student_id_details.course_enrolled
    linkedin_url = student_id_details.linkedin_url
    phone = student_id_details.phone
    address = student_id_details.address
    profile_pic_name = student_id_details.profile_pic_name
    student_status = student_id_details.student_status
    student_level = student_id_details.student_level
    grad_date = student_id_details.grad_date
    email=student_id_details.email
    uploads_folder = os.path.join(app.static_folder, 'uploads')
    for file_name in os.listdir(uploads_folder):
        if file_name.startswith(profile_pic_name):
            profile_picture = file_name
            break
        else:
            profile_picture = "noname.png"
    if not profile_pic_name:
        profile_picture = "noname.png"  
    print(profile_picture)
    return render_template(
        'student_profile_page.html',firstname=firstname,secondname=secondname,surname=surname,course_enrolled=course_enrolled,linkedin_url=linkedin_url,
        phone=phone,email=email,address=address,student_status=student_status,student_level=student_level,grad_date=grad_date,
        profile_picture=profile_picture,form=form)


@app.route('/student_profile_saving_action', methods=['GET', 'POST'])
def student_profile_saving_action():
    if request.method == 'POST':
        firstname = request.form.get('firstname')
        secondname = request.form.get('secondname')
        surname = request.form.get('surname')
        course_enrolled = request.form.get('course_enrolled')
        linkedin_url = request.form.get('linkedin_url')
        phone = request.form.get('phone')
        email = request.args.get('email')  # From query params
        address = request.form.get('address')
        if not email:
            return "Email is required to update the profile.", 400
        student_id_details = student_info.query.filter_by(email=email).first()
        if not student_id_details:
            return f"No student found with email: {email}", 404
        form = Student_reg_form()
        student_id_details.firstname = firstname
        student_id_details.secondname = secondname
        student_id_details.surname = surname
        student_id_details.course_enrolled = course_enrolled
        student_id_details.linkedin_url = linkedin_url
        student_id_details.phone = phone
        student_id_details.address = address
        try:
            db.session.commit()
            return render_template(
                'student_profile_page.html',firstname=firstname,secondname=secondname,surname=surname,course_enrolled=course_enrolled,
                linkedin_url=linkedin_url,phone=phone,email=email,address=address,student_status=student_id_details.student_status,student_level=student_id_details.student_level,
                grad_date=student_id_details.grad_date,profile_picture=student_id_details.profile_pic_name,
                form=form
            )
        except Exception as e:
            db.session.rollback()
            return f"An error occurred: {e}", 500

    return redirect(url_for('general_login_page'))


@app.route("/project_page")
def project_page():
    return render_template('project_page.html')




@app.route('/make_public', methods=['GET', 'POST'])
def make_public():
    project_id = request.args.get('project_id')
    project=project_table.query.filter_by(project_id=project_id).first()
    project.public=1
    db.session.commit()

    uploaded_project=project_table.query.all()
    return render_template('admin_edit_uploaded.html', uploaded_project=uploaded_project) 

   



@app.route('/student_project_page', methods=['GET', 'POST'])
def student_project_page():
    email = request.args.get('email')
    student_details=student_info.query.filter_by(email=email).first()
    course_enrolled=student_details.course_enrolled
    project_list=project_table.query.filter_by(course_enrolled=course_enrolled).all()
    return render_template('student_project_page.html', project_list=project_list) 




@app.route('/particular_project_page', methods=['GET', 'POST'])
def particular_project_page():
    project_id= request.args.get('project_id')
    project=project_table.query.filter_by(project_id=project_id).first()
    project_title=project.project_title
    project_concept=project.project_concept
    project_resources=project.project_resources
    project_requirements=project.project_requirements
    project_objectives=project.project_objectives
    particular_obj_set = objective_questions.query.filter_by(project_id=project_id).all()
    particular_theory_set=theory_questions.query.filter_by(project_id=project_id).all()

    return render_template('particular_project_page.html', project_id=project_id, project=project, project_title=project_title,
    project_concept=project_concept, project_resources=project_resources, project_requirements=project_requirements,
    project_objectives=project_objectives, particular_obj_set=particular_obj_set, particular_theory_set=particular_theory_set) 




@app.route("/manage_student", methods=["GET", "POST"])
def manage_student():
    # For GET: Populate JSON for student names
    std_details = student_info.query.all()
    student_full = [f"{s.firstname} {s.surname}" for s in std_details]
    with open("static/data.json", "w") as json_file:
        json.dump(student_full, json_file)
    return render_template('manage_student.html', form=ManageStudentForm())

@app.route("/manage_student_action", methods=["GET", "POST"])
def manage_student_action():

    if request.method == 'POST':
        filtering = request.form.get('filtering')
        course = request.form.get('course')
        student_name = request.form.get('student_name')
        date_created= datetime.now()     
        if filtering == "student":

            name_filter=student_name.split(" ")
            firstname = name_filter[0]
            surname = name_filter[1]
            student_row = student_info.query.filter(student_info.firstname == firstname,
            student_info.surname == surname).first()
            each_student_email = student_row.email
            return redirect(url_for('student_profile_route' , email=each_student_email ))
        else:
            student_row=student_info.query.filter_by(course_enrolled=course).all()
            
            return redirect(url_for('admin_student_edit', course=course))
            
    return "action successfully!"
    

if __name__=='__main__':
	app.run(debug=True)



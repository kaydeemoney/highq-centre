from flask import Flask, Blueprint, render_template, request, redirect, url_for, flash, session
from flask_wtf import FlaskForm
from flask_sqlalchemy import SQLAlchemy
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField, DateField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo
import uuid, json
from config import Config
from datetime import datetime, timedelta
#this is for the validation efficiency of the wtf form you must always include it
from flask_wtf.csrf import CSRFProtect
from sqlalchemy.exc import IntegrityError


app = Flask(__name__, static_folder='static')

app.config.from_object(Config)
db = SQLAlchemy(app)


#wtf form validation, for form input sending
csrf = CSRFProtect(app)
app.config['WTF_CSRF_ENABLED'] = True
app.config['WTF_CSRF_SECRET_KEY'] = '7caa483b-e1c7-4a65-b901-beae2633e028' 


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
    title = db.Column(db.String(500), nullable=False)
    course_enrolled = db.Column(db.String(50), nullable=False)
    date_created = db.Column(db.String(50), nullable=False)
    deadline=db.Column(db.String(50), nullable=False)
    project_type=db.Column(db.String(50), nullable=False)

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
    submit = SubmitField('sign up!')


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
    deadline = DateField('Deadline', validators=[DataRequired()])    
    submit_objective = SubmitField('Objective')
    submit_theory = SubmitField('Theory')

class Objupload(FlaskForm):
    question = StringField('Question', validators=[DataRequired()])
    opt_a = StringField('Option A', validators=[DataRequired()])
    opt_b = StringField('Option B', validators=[DataRequired()])
    opt_c = StringField('Option C', validators=[DataRequired()])
    opt_d = StringField('Option D', validators=[DataRequired()])
    answer = StringField('answer', validators=[DataRequired()])
    submit = SubmitField('submit this!')

class Theoryupload(FlaskForm):
    question = TextAreaField('Project Tasks', validators=[DataRequired()])
    submit = SubmitField('Add')
    






#defining model for the student sign in form

class general_login_form(FlaskForm):
    email= StringField('email', validators=[DataRequired(), Length(min=5, max =50)])
    password = PasswordField('password', validators=[DataRequired()])
    submit = SubmitField('Login')

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
    joint_id= uuid.uuid4()
    profile_pic_name=joint_id
    student_task_id=joint_id
    student_status="student"
    student_level="stage_1"
    date_created= datetime.now()
    grad_date=date_created + timedelta(days=90)

    form = Student_reg_form()

    if form.validate_on_submit():
        firstname=form.firstname.data
        secondname=form.secondname.data
        surname=form.surname.data
        course_enrolled=form.course_enrolled.data
        linkedin_url=form.linkedin_url.data
        phone=form.phone.data
        email=form.email.data
        address=form.address.data
        password=form.password.data
        student = student_info(firstname= firstname, secondname=secondname, surname=surname, course_enrolled=course_enrolled,
        linkedin_url=linkedin_url, phone=phone, email=email, address=address, password=password, profile_pic_name=joint_id,
        student_status=student_status, student_level=student_level, date_created=date_created, grad_date=grad_date,
        student_task_id=student_task_id)
        try:

            db.session.add(student)
            db.session.commit()
            flash(f"Account Created For {{form.surname.data}}", 'success')
            return redirect(url_for('general_login_page'))
        except IntegrityError:
        # Rollback the session in case of an error
            db.session.rollback()
            return render_template('student_reg_page.html', title="Student Application", form=form)
    if not form.validate_on_submit():
        print(form.errors)
    return render_template('student_reg_page.html', 
    title="Student Application", form=form) 


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
    print(firstname)


    return render_template('student_dashboard.html', 
    firstname=firstname, surname=surname, student_status=student_status)


@app.route("/admin_dashboard")
def admin_dashboard():

    student_no = student_info.query.all()
    headcount=0

    for student in student_no:
        headcount+=1


    return render_template('admin_dashboard.html', headcount=headcount)

@app.route("/admin_project_upload_page" , methods=['GET', 'POST'])
def admin_project_upload_page():
    pid=uuid.uuid4()
    project_id=pid
    form = ProjectUploadForm()
    if form.validate_on_submit():

        project_id=project_id
        title=form.project_title.data
        course_enrolled=form.course_enrolled.data
        deadline=form.deadline.data
        date_created= datetime.now()


        if form.submit_objective.data:
            project_type="objective"
            project = project_table(project_id=project_id, title=title, course_enrolled=course_enrolled,
            deadline=deadline, date_created=date_created, project_type=project_type)
            db.session.add(project)
            db.session.commit()

            return redirect(url_for('admin_obj', project_id=project_id, title=form.project_title.data,
            course_enrolled=form.course_enrolled.data, deadline=form.deadline.data))
        elif form.submit_theory.data:

            project_type="theory"
            project = project_table(project_id=project_id, title=title, course_enrolled=course_enrolled,
            deadline=deadline, date_created=date_created, project_type=project_type)
            db.session.add(project)
            db.session.commit()


            return redirect(url_for('admin_theory', project_id=project_id, title=form.project_title.data,
            course_enrolled=form.course_enrolled.data, deadline=form.deadline.data))

        return redirect(url_for('admin_project_upload_page'))  # Redirect to avoid form re-submission
    return render_template('admin_project_upload_page.html', form=form)


@app.route('/admin_obj', methods=['GET', 'POST'])
def admin_obj():
    
    course_enrolled = request.args.get('course_enrolled')
    deadline = request.args.get('deadline')
    project_id=request.args.get('project_id')

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
            return redirect(url_for('admin_obj', project_id=project_id, course_enrolled=course_enrolled, deadline=deadline))
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
    project_correct=objective_questions.query.filter_by(project_id=project_id).all()
    for bad_question in project_correct:
        question_to_correct= bad_question.question
        opt_a_edit=bad_question.opt_a
        opt_b_edit=bad_question.opt_b
        opt_c_edit=bad_question.opt_c
        opt_d_edit=bad_question.opt_d
        answer_edit=bad_question.answer
    return render_template('admin_edit_current.html', project_correct=project_correct) 


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

@app.route("/notification")
def notification():
    #the JSON part
    std_details=student_info.query.all()
    counter=0
    student_full=[]
    for specifics in std_details:
        specifics_fullname = specifics.firstname + " " + specifics.surname
        student_full.append(specifics_fullname)
    print ("this is the revised list")
    print(student_full)
    for name in student_full:
        print(name)
    return "thanks for checking"  
    
   
if __name__=='__main__':
	app.run(debug=True)
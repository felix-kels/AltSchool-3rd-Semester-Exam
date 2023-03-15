from flask import Flask
from flask_restx import Api, Resource, fields
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///students.db'  # change this to your database connection string
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'secret'  # change this to your secret key

db = SQLAlchemy(app)
jwt = JWTManager(app)
api = Api(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(10), nullable=False)  # either 'student' or 'teacher'

    def __repr__(self):
        return f'<User {self.username}>'


class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)
    courses = db.relationship('Course', secondary='student_course', backref='students')

    def __repr__(self):
        return f'<Student {self.name}>'


class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    teacher = db.relationship('User', backref='courses')
    grades = db.relationship('Grade', backref='course')

    def __repr__(self):
        return f'<Course {self.name}>'


class Grade(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    student = db.relationship('Student', backref='grades')
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    score = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f'<Grade {self.student.name} - {self.course.name} - {self.score}>'


# association table for many-to-many relationship between students and courses
student_course = db.Table('student_course',
                          db.Column('student_id', db.Integer, db.ForeignKey('student.id')),
                          db.Column('course_id', db.Integer, db.ForeignKey('course.id'))
                          )

# from flask_jwt_extended import create_access_token
# from flask_restx import fields, Resource
# from werkzeug.security import generate_password_hash, check_password_hash
#
# from app import api, db
# from models import User

user_model = api.model('User', {
    'username': fields.String(required=True),
    'password': fields.String(required=True),
})


@api.route('/register')
class Register(Resource):

    @api.expect(user_model)
    def post(self):
        data = api.payload
        username = data.get('username')
        password = data.get('password')
        role = data.get('role')

        if not username or not password or not role:
            return {'message': 'Missing username, password or role'}, 400

        if User.query.filter_by(username=username).first():
            return {'message': 'Username already exists'}, 400

        hashed_password = generate_password_hash(password)

        user = User(username=username, password=hashed_password, role=role)

        try:
            db.session.add(user)
            db.session.commit()
            return {'message': 'User registered successfully'}, 201
        except:
            return {'message': 'Something went wrong'}, 500


@api.route('/login')
class Login(Resource):

    @api.expect(user_model)
    def post(self):
        data = api.payload
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return {'message': 'Missing username or password'}, 400

        user = User.query.filter_by(username=username).first()

        if not user or not check_password_hash(user.password, password):
            return {'message': 'Invalid credentials'}, 401

        access_token = create_access_token(identity=user.id)

        return {'access_token': access_token}, 200


# # oauth.py
# from flask_jwt_extended import jwt_required
# from flask_restx import fields, Resource
#
# from app import api, db
# from models import User

student_model = api.model('Student', {
    'name': fields.String(required=True),
    'email': fields.String(required=True)
})

course_model = api.model('Course', {
    'name': fields.String(required=True),
    'teacher_id': fields.Integer(required=True)
})

grade_model = api.model('Grade', {
    'student_id': fields.Integer(required=True),
    'course_id': fields.Integer(required=True),
    'score': fields.Float(required=True)
})


@api.route('/students')
class Students(Resource):

    @jwt_required()
    def get(self):
        students = Student.query.all()
        return [student.name for student in students], 200

    @api.expect(student_model)
    @jwt_required()
    def post(self):
        data = api.payload
        name = data.get('name')
        email = data.get('email')

        if not name or not email:
            return {'message': 'Missing name or email'}, 400

        if Student.query.filter_by(email=email).first():
            return {'message': 'Email already exists'}, 400

        student = Student(name=name, email=email)

        try:
            db.session.add(student)
            db.session.commit()
            return {'message': 'Student created successfully'}, 201
        except:
            return {'message': 'Something went wrong'}, 500


@api.route('/students/<int:id>')
class Student(Resource):

    @jwt_required()
    def get(self, id):
        student = Student.query.get_or_404(id)
        return {
                   'name': student.name,
                   'email': student.email,
                   'courses': [course.name for course in student.courses],
                   'gpa': self.calculate_gpa(student.grades)
               }, 200

    @api.expect(student_model)
    @jwt_required()
    def put(self, id):
        data = api.payload
        name = data.get('name')
        email = data.get('email')

        if not name or not email:
            return {'message': 'Missing name or email'}, 400

        student = Student.query.get_or_404(id)

        if Student.query.filter_by(email=email).first() and email != student.email:
            return {'message': 'Email already exists'}, 400

        student.name = name
        student.email = email

        try:
            db.session.commit()
            return {'message': 'Student updated successfully'}, 200
        except:
            return {'message': 'Something went wrong'}, 500

    @jwt_required()
    def delete(self, id):
        student = Student.query.get_or_404(id)
        try:
            db.session.delete(student)
            db.session.commit()
            return {'message': 'Student deleted successfully'}, 200
        except:
            return {'message': 'Something went wrong'}, 500

    def calculate_gpa(self, grades):
        # use the standard 4.0 scale for calculating GPA
        total_points = 0
        total_credits = 0
        for grade in grades:
            score = grade.score
            if score >= 90:
                points = 4.0
            elif score >= 80:
                points = 3.0
            elif score >= 70:
                points = 2.0
            elif score >= 60:
                points = 1.0
            else:
                points = 0.0
            total_points += points
            total_credits += 1  # assume each course has one credit
        if total_credits == 0:
            return None  # no grades available
        else:
            return round(total_points / total_credits, 2)

    @api.route('/courses')
    class Courses(Resource):

        @jwt_required()
        def get(self):
            courses = Course.query.all()
            return [course.name for course in courses], 200

        @api.expect(course_model)
        @jwt_required()
        def post(self):
            data = api.payload
            name = data.get('name')
            teacher_id = data.get('teacher_id')

            if not name or not teacher_id:
                return {'message': 'Missing name or teacher_id'}, 400

            if Course.query.filter_by(name=name).first():
                return {'message': 'Course already exists'}, 400

            teacher = User.query.get_or_404(teacher_id)

            if teacher.role != 'teacher':
                return {'message': 'Invalid teacher_id'}, 400

            course = Course(name=name, teacher_id=teacher_id)

            try:
                db.session.add(course)
                db.session.commit()
                return {'message': 'Course created successfully'}, 201
            except:
                return {'message': 'Something went wrong'}, 500


@api.route('/courses/<int:id>')
class Course(Resource):

    @jwt_required()
    def get(self, id):
        course = Course.query.get_or_404(id)
        return {
                   'name': course.name,
                   'teacher': course.teacher.username,
                   'students': [student.name for student in course.students],
                   'grades': [grade.score for grade in course.grades]
               }, 200

    @api.expect(course_model)
    @jwt_required()
    def put(self, id):
        data = api.payload
        name = data.get('name')
        teacher_id = data.get('teacher_id')

        if not name or not teacher_id:
            return {'message': 'Missing name or teacher_id'}, 400

        course = Course.query.get_or_404(id)

        if Course.query.filter_by(name=name).first() and name != course.name:
            return {'message': 'Course already exists'}, 400

        teacher = User.query.get_or_404(teacher_id)

        if teacher.role != 'teacher':
            return {'message': 'Invalid teacher_id'}, 400

        course.name = name
        course.teacher_id = teacher_id

        try:
            db.session.commit()
            return {'message': 'Course updated successfully'}, 200
        except:
            return {'message': 'Something went wrong'}, 500

    @jwt_required()
    def delete(self, id):
        course = Course.query.get_or_404(id)

        try:
            db.session.delete(course)
            db.session.commit()
            return {'message': 'Course deleted successfully'}, 200
        except:
            return {'message': 'Something went wrong'}, 500


@api.route('/grades')
class Grades(Resource):

    @jwt_required()
    def get(self):
        grades = Grade.query.all()
        return [{
            'student': grade.student.name,
            'course': grade.course.name,
            'score': grade.score
        } for grade in grades], 200

    @api.expect(grade_model)
    @jwt_required()
    def post(self):
        data = api.payload
        student_id = data.get('student_id')
        course_id = data.get('course_id')
        score = data.get('score')

        if not student_id or not course_id or not score:
            return {'message': 'Missing student_id, course_id or score'}, 400

        if Grade.query.filter_by(student_id=student_id, course_id=course_id).first():
            return {'message': 'Grade already exists'}, 400

        student = Student.query.get_or_404(student_id)
        course = Course.query.get_or_404(course_id)

        if score < 0 or score > 100:
            return {'message': 'Invalid score'}, 400

        grade = Grade(student_id=student_id, course_id=course_id, score=score)

        try:
            db.session.add(grade)
            db.session.commit()
            return {'message': 'Grade created successfully'}, 201
        except:
            return {'message': 'Something went wrong'}, 500


@api.route('/grades/<int:id>')
class Grade(Resource):

    @jwt_required()
    def get(self, id):
        grade = Grade.query.get_or_404(id)
        return {
                   'student': grade.student.name,
                   'course': grade.course.name,
                   'score': grade.score
               }, 200

    @api.expect(grade_model)
    @jwt_required()
    def put(self, id):
        data = api.payload
        student_id = data.get('student_id')
        course_id = data.get('course_id')
        score = data.get('score')

        if not student_id or not course_id or not score:
            return {'message': 'Missing student_id, course_id or score'}, 400

        grade = Grade.query.get_or_404(id)

        student = Student.query.get_or_404(student_id)
        course = Course.query.get_or_404(course_id)

        if score < 0 or score > 100:
            return {'message': 'Invalid score'}, 400

        grade.student_id = student_id
        grade.course_id = course_id
        grade.score = score

        try:
            db.session.commit()
            return {'message': 'Grade updated successfully'}, 200
        except:
            return {'message': 'Something went wrong'}, 500

    @jwt_required()
    def delete(self, id):
        grade = Grade.query.get_or_404(id)
        try:
            db.session.delete(grade)
            db.session.commit()
            return {'message': 'Grade deleted successfully'}, 200
        except:
            return {'message': 'Something went wrong'}, 500

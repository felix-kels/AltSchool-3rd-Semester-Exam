# # models.py
# from app import db
#
#
# class User(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     username = db.Column(db.String(50), unique=True, nullable=False)
#     password = db.Column(db.String(100), nullable=False)
#     role = db.Column(db.String(10), nullable=False)  # either 'student' or 'teacher'
#
#     def __repr__(self):
#         return f'<User {self.username}>'
#
#
# class Student(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(50), nullable=False)
#     email = db.Column(db.String(50), unique=True, nullable=False)
#     courses = db.relationship('Course', secondary='student_course', backref='students')
#
#     def __repr__(self):
#         return f'<Student {self.name}>'
#
#
# class Course(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(50), nullable=False)
#     teacher_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
#     teacher = db.relationship('User', backref='courses')
#     grades = db.relationship('Grade', backref='course')
#
#     def __repr__(self):
#         return f'<Course {self.name}>'
#
#
# class Grade(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
#     student = db.relationship('Student', backref='grades')
#     course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
#     score = db.Column(db.Float, nullable=False)
#
#     def __repr__(self):
#         return f'<Grade {self.student.name} - {self.course.name} - {self.score}>'
#
#
# # association table for many-to-many relationship between students and courses
# student_course = db.Table('student_course',
#                           db.Column('student_id', db.Integer, db.ForeignKey('student.id')),
#                           db.Column('course_id', db.Integer, db.ForeignKey('course.id'))
#                           )
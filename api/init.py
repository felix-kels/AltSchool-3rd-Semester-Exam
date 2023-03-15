# from app import app, api
# from auth import jwt
# from oauth import resource_protector, validate_token
# from models import db, Student, Course, Grade
#
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///students.db'
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# app.config['JWT_SECRET_KEY'] = 'super-secret'
#
# db.init_app(app)
# jwt.init_app(app)
# resource_protector.register_token_validator(validate_token)
#
# with app.app_context():
#     db.create_all()
#     if not Student.query.all():
#         db.session.add(Student(name='John Doe', email='john.doe@example.com'))
#         db.session.add(Student(name='Jane Doe', email='jane.doe@example.com'))
#         db.session.commit()
#     if not Course.query.all():
#         db.session.add(Course(name='Introduction to Computer Science', teacher='Dr. Smith', students=[Student.query.get(1), Student.query.get(2)]))
#         db.session.commit()
#     if not Grade.query.all():
#         db.session.add(Grade(course_id=1, student_id=1, grade=3.7))
#         db.session.add(Grade(course_id=1, student_id=2, grade=3.9))
#         db.session.commit()
#
# if __name__ == '__main__':
#     app.run(debug=True)

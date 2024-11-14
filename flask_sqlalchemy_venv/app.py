#Task 1: Setting Up Flask with Flask-SQLAlchemy
#  - Initialize a new Flask project and set up a virtual environment.
#  - Install Flask, Flask-SQLAlchemy, and Flask-Marshmallow.
#  - Configure Flask-SQLAlchemy to connect to your database. 
# - Define `Members` and `WorkoutSessions` models using Flask-SQLAlchemy ORM.



from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow

from marshmallow import fields, ValidationError


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:Babinz2023!@localhost/gym_database'
db = SQLAlchemy(app)
ma = Marshmallow(app)




class MemberSchema(ma.Schema):
      id = fields.Integer(required = True)
      name = fields.String(required= True)
      age = fields.Integer()

      class Meta:
          fields = ("id", "name", "age")

member_schema = MemberSchema()
members_schema = MemberSchema(many= True)


class SessionSchema(ma.Schema):
    session_id = fields.Integer(required=True)
    member_id = fields.Integer(required=True)
    session_date = fields.Date(required=True)
    session_time = fields.String(required=True)
    activity = fields.String()
    

    
     
  #  FOREIGN KEY (member_id) REFERENCES Members(id)
    class Meta:
        fields = ("session_id", "member_id", "session_date", "session_time", "activity")

session_schema = SessionSchema()
sessions_schema = SessionSchema(many=True)






class Member(db.Model):
      __table_name__ = "Members"

      id = db.Column(db.Integer, primary_key = True)
      name= db.Column(db.String(255), unique = True, nullable = False)
      age = db.Column(db.String(8))
      member_sessions = db.relationship('WorkoutSession', backref= 'members', lazy = True)
      
 

class WorkoutSession(db.Model):
      __table_name__ = "WorkoutSessions"

      session_id = db.Column(db.Integer, primary_key = True)
      member_id= db.Column(db.Integer, db.ForeignKey('member.id'))
      
      session_date = db.Column(db.Date)
      session_time = db.Column(db.String(40))
      activity = db.Column(db.String(255))
      member = db.relationship('Member', backref = 'member_session', uselist= False)
    
      





# Task 2: Implementing CRUD Operations for Members Using ORM 
# - Create Flask routes to add, retrieve, update, and delete members using the ORM models.
#  - Apply HTTP methods: POST to add, GET to retrieve, PUT to update,
#  and DELETE to delete members.
#  - Handle errors effectively and return appropriate JSON responses.


@app.route('/', methods =['GET'])

def home():
    return "Welcome to the Fitness Center DB!!"

@app.route('/members', methods=['GET'])

def get_members():
      members = Member.query.all()
      return  members_schema.jsonify(members)

@app.route('/members', methods=['POST'])
def add_a_member():
   try:
     member_data = member_schema.load(request.json)
   except ValidationError as e:
     print(f'Validation Error: {e}')
     return jsonify(e.messages), 400

   new_member = Member(id = member_data["id"], name = member_data["name"], age = member_data["age"])
   db.session.add(new_member)
   db.session.commit()
       
   return jsonify({"message": "New member added successfully"}), 201


@app.route('/members/<int:id>', methods=['PUT'])
def update_member(id):
    member = Member.query.get_or_404(id)

    try:
    
      member_data = member_schema.load(request.json)
     #catch errors in input during update

    except ValidationError as e:
      print(f'Validation Error: {e}')
      return jsonify(e.messages), 400

    member.id  = member_data['id']
    member.name = member_data['name']
    member.age = member_data['age']

    db.session.commit()

    return jsonify({"message": "Member updated successfully"}), 201

  
@app.route('/members/<int:id>', methods=['DELETE'])
def delete_member(id):
    
    member = Member.query.get_or_404(id)
    db.session.delete(member)
    db.session.commit()
    
    return jsonify({"message": "Member deleted successfully"}), 201





# _________________________******************____________________________

#Task 3: Managing Workout Sessions with ORM 
# - Develop routes to schedule, update, and view workout sessions using SQLAlchemy.
#  Implement a route to retrieve all workout sessions for a specific member.


@app.route('/sessions/member_sessions/<int:id>', methods=['GET'])

def get_member_sessions(id):
      
      id = Member.query.get('id')
      sessions = WorkoutSession.query.filter(id==id).first()
      if sessions:
        return  session_schema.jsonify(sessions)
      else:
          return jsonify({"message": "No sessions found for that member."})


@app.route('/sessions', methods=['GET'])

# route to view all sessions

def get_all_sessions():

      sessions = WorkoutSession.query.all()
      return  sessions_schema.jsonify(sessions)

### route for scheduling a workout session

@app.route('/sessions', methods=['POST'])
def schedule_session():
   try:
     session_data = session_schema.load(request.json)
   except ValidationError as e:
     print(f'Validation Error: {e}')
     return jsonify(e.messages), 400

   new_session = WorkoutSession(session_id= session_data["session_id"], 
                                member_id= session_data["member_id"],
                                session_date= session_data["session_date"], 
                                session_time= session_data["session_time"], 
                                activity= session_data["activity"])
                                
   db.session.add(new_session)
   db.session.commit()
       
   return jsonify({"message": "New workout session added successfully"}), 201



# route to update a workout

@app.route('/sessions/<int:session_id>', methods=['PUT'])
def update_session(session_id):
    session = WorkoutSession.query.one_or_404(session_id)
    try:
    
      session_data = session_schema.load(request.json)
     #catch errors in input during update

    except ValidationError as e:
      print(f'Validation Error: {e}')
      return jsonify(e.messages), 400

    session.session_id  = session_data['session_id']
    session.member_id  = session_data['member_id']
    session.session_date = session_data['session_date']
    session.session_time = session_data['session_time']
    session.activity = session_data['activity']

    db.session.commit()

    return jsonify({"message": "Workout session updated successfully"}), 201

# route to delete a workout

@app.route('/sessions/<int:session_id>', methods=['DELETE'])
def delete_session(session_id):
    
    try:
      session = WorkoutSession.query.one_or_404(session_id)
      
     #catch errors in input during update

    except ValidationError as e:
      print(f'Validation Error: {e}')
      return jsonify(e.messages), 400
  
    db.session.delete(session)
    db.session.commit()

    return jsonify({"message": "Workout session deleted successfully"}), 200



with app.app_context():
    db.create_all()
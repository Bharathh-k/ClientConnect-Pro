from db_extensions import db

# Client table
class Client(db.Model):
    __tablename__ = 'clients'
    client_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    contact_no = db.Column(db.String(15), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    industry = db.Column(db.String(100), nullable=False)
    company_size = db.Column(db.String(50))
    username = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)  # 255 to accommodate hashed passwords

    # One-to-many relationships
    projects = db.relationship('Project', backref='client', lazy=True)
    invoices = db.relationship('Invoice', backref='client', lazy=True)

# Project table
class Project(db.Model):
    __tablename__ = 'projects'
    project_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    project_name = db.Column(db.String(100), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date)
    status = db.Column(db.String(50), nullable=False)
    budget = db.Column(db.Float, nullable=False)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.client_id'), nullable=False)

    # One-to-one relationship with Invoice
    invoice = db.relationship('Invoice', backref='project', uselist=False)
    # One-to-many relationships
    tasks = db.relationship('Task', backref='project', lazy=True)
    employees = db.relationship('Employee', backref='project', lazy=True)

# Task table
class Task(db.Model):
    __tablename__ = 'tasks'
    task_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    task_name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(250))
    deadline = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(50), nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.project_id'), nullable=False)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.client_id'), nullable=False)

    # Many-to-many relationship with Team (via association table)
    teams = db.relationship('Team', secondary='task_team', back_populates='tasks')

# Association table for Task and Team many-to-many relationship
task_team = db.Table('task_team',
    db.Column('task_id', db.Integer, db.ForeignKey('tasks.task_id'), primary_key=True),
    db.Column('team_id', db.Integer, db.ForeignKey('teams.team_id'), primary_key=True)
)

# Team table
class Team(db.Model):
    __tablename__ = 'teams'
    team_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    team_name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(250))

    # One-to-many relationship with Employee
    employees = db.relationship('Employee', backref='team', lazy=True)

    # Many-to-many relationship with Task
    tasks = db.relationship('Task', secondary='task_team', back_populates='teams')

# Employee table
class Employee(db.Model):
    __tablename__ = 'employees'
    employee_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    phno = db.Column(db.String(15), nullable=False)
    team_id = db.Column(db.Integer, db.ForeignKey('teams.team_id'))
    project_id = db.Column(db.Integer, db.ForeignKey('projects.project_id'))

# Invoice table
class Invoice(db.Model):
    __tablename__ = 'invoices'
    invoice_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(50), nullable=False)
    invoice_date = db.Column(db.Date, nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.project_id'), unique=True)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.client_id'), nullable=False)

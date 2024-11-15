from flask import Flask, redirect, render_template, flash, url_for, request, session, jsonify
from werkzeug.security import check_password_hash, generate_password_hash   
from db_extensions import db
from models import Client, Task, Employee, Team, Invoice, Project
from datetime import date
from sqlalchemy import text

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = ""
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = "clientconnectpro"

db.init_app(app)

SECRET_KEY = "clientconnectpro"

@app.route('/db_check', methods=['GET'])
def db_check():
    try:
        result = db.session.execute(text("SELECT 1")).scalar()
        if result == 1:
            return jsonify({"status": "success", "message": "Database connection is successful"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": f"Database connection failed: {str(e)}"}), 500

@app.route('/tables')
def list_tables():
    try:
        result = db.session.execute(
            text("SELECT table_name FROM information_schema.tables WHERE table_catalog = 'chs';")
        )
        tables = [row[0] for row in result.fetchall()]
        return render_template("tables.html", tables=tables)
    except Exception as e:
        return jsonify({"message": f"Failed to retrieve tables: {str(e)}", "status": "error"})

@app.route("/")
def home():
    session.pop('_flashes', None)
    return render_template("home.html")

@app.route("/add_user", methods=['GET', 'POST'])
def create_client():
    session.pop('_flashes', None)
    if request.method == 'POST':
        username = request.form["username"]
        password = request.form["password"]
        secret = request.form["secret"]
        name = request.form['name']
        address = request.form['address']
        contact_no = request.form['contact_no']
        email = request.form['email']
        industry = request.form['industry']
        company_size = request.form['company_size']

        # Clear previous flash messages
        session.pop('_flashes', None)

        if secret != SECRET_KEY:
            flash("Secret key is incorrect", "error")
            return render_template("add_user.html")

        try:
            user = Client(
                username=username, 
                password=generate_password_hash(password),
                name=name,
                address=address, 
                contact_no=contact_no, 
                email=email, 
                industry=industry, 
                company_size=company_size
            )
            db.session.add(user)
            db.session.commit()
            flash('User added successfully.', 'success')
            return redirect(url_for('client_login'))
        except Exception as e:
            db.session.rollback()
            flash(f'Failed to add user: {str(e)}', 'error')
            return redirect(url_for('create_client'))

    return render_template("add_user.html")

@app.route("/client_login", methods=['GET', 'POST'])
def client_login():
    session.pop('_flashes', None)
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        session.pop('_flashes', None)

        try:
            user = Client.query.filter_by(username=username).first()
        except Exception as e:
            flash('Failed to query user.', 'error')
            return redirect(url_for('client_login'))
        
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.client_id
            session['user_role'] = 'client'
            return redirect(url_for('client_dashboard', client_id=user.client_id))
        else:
            flash('Login failed. Check your username and/or password.', 'error')
            return redirect(url_for('client_login'))

    return render_template("client_login.html")

@app.route("/manager_login", methods=['GET', 'POST'])
def manager_login():
    session.pop('_flashes', None)
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        session.pop('_flashes', None)

        try:
            user = Employee.query.filter_by(name=username, role="Manager").first()
        except Exception as e:
            flash('Failed to login.', 'error')
            return redirect(url_for('manager_login'))

        if user and user.role == 'Manager' and password == user.phno:
            session['user_id'] = user.employee_id
            session['user_role'] = 'manager'
            return redirect(url_for('manager_dashboard'))
        else:
            flash("Login failed. Check username or password.", 'error')
            return redirect(url_for('manager_login'))

    return render_template("manager_login.html")

@app.route('/employee_login', methods=['GET', 'POST'])
def employee_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        session.pop('_flashes', None)

        try:
            # Query the employee from the database
            employee = Employee.query.filter_by(name=username).first()
        except Exception as e:
            flash('Failed to query employee.', 'error')
            return redirect(url_for('employee_login'))

        # Check if employee exists and verify password
        if employee and employee.phno == password:
            # Store employee information in the session
            session['user_id'] = employee.employee_id
            session['user_role'] = 'employee'
            flash('Login successful!', 'success')
            return redirect(url_for('employee_dashboard'))
        else:
            flash('Login failed. Check your username and/or password.', 'error')
            return redirect(url_for('employee_login'))

    # Render the employee login form if it's a GET request
    return render_template("employee_login.html")

@app.route("/employee_dashboard")
def employee_dashboard():
    employee_id = session.get("user_id")

    # Clear previous flash messages
    session.pop('_flashes', None)

    if not employee_id:
        flash('You must be logged in to access the employee dashboard.', 'error')
        return redirect(url_for('employee_login'))

    employee = Employee.query.get(employee_id)
    projects = Project.query.filter_by(project_id=employee.project_id).all()
    tasks = Task.query.filter_by(project_id=employee.project_id, status="Pending").all()
    teams = Team.query.filter_by(team_id=employee.team_id).all()

    return render_template("employee_dashboard.html", employee=employee, projects=projects, tasks=tasks, teams=teams)

@app.route("/client_dashboard", methods=['GET', 'POST'])
def client_dashboard():
    # Check if user is logged in
    # Clear previous flash messages
    session.pop('_flashes', None)

    if 'user_id' not in session:
        flash('Please log in first', 'error')
        return redirect(url_for('client_login'))
    
    client_id = session['user_id']
    
    # Handle new project creation
    if request.method == 'POST':
        project_name = request.form.get("project_name")
        budget = request.form.get("budget")

        # Clear previous flash messages
        session.pop('_flashes', None)

        if project_name and budget:
            try:
                new_project = Project(
                    project_name=project_name,
                    start_date=date.today(),
                    status="Pending",
                    budget=float(budget),  # Convert budget to float
                    client_id=client_id
                )
                db.session.add(new_project)
                db.session.commit()
                flash('Project request submitted successfully.', 'success')
            except ValueError:
                flash('Invalid budget value. Please enter a valid number.', 'error')
            except Exception as e:
                db.session.rollback()
                flash(f'Failed to create project: {str(e)}', 'error')
    
    try:
        # Get client data
        client = Client.query.get(client_id)
        if not client:
            flash('Client not found', 'error')
            return redirect(url_for('client_login'))

        # Get all projects for this client
        projects = Project.query.filter_by(client_id=client_id).all()
        
        # Get all invoices for this client
        pending_invoices = Invoice.query.filter_by(
            client_id=client_id,
            status="Pending"
        ).all()
        
        completed_invoices = Invoice.query.filter_by(
            client_id=client_id,
            status="Paid"
        ).all()

        return render_template(
            "client_dashboard.html",
            client=client,
            projects=projects,
            pending_invoices=pending_invoices,
            completed_invoices=completed_invoices
        )
        
    except Exception as e:
        flash(f'Error fetching dashboard data: {str(e)}', 'error')
        return redirect(url_for('client_login'))
    
@app.route("/manager_dashboard", methods=['GET', 'POST']) 
def manager_dashboard():
    if request.method == 'POST':
        if 'update_end_date' in request.form:
            project_id = request.form["project_id"]
            end_date = request.form["end_date"]

            # Clear previous flash messages
            session.pop('_flashes', None)

            try:
                # Call the new stored procedure change_end_date to update only the end_date
                db.session.execute(text("CALL change_end_date(:project_id_param, :end_date_param)"), {
                    'project_id_param': project_id,
                    'end_date_param': end_date
                })
                db.session.commit()
                flash('Project end date updated successfully.', 'success')
            except Exception as e:
                db.session.rollback()
                flash(f'Failed to update project end date: {str(e)}', 'error')

        elif 'new_project' in request.form:
            project_name = request.form["project_name"]
            try:
                new_project = Project(
                    project_name=project_name,
                    start_date=date.today(),
                    status="Not Started",
                    budget=10000.0,
                    client_id=10
                )
                db.session.add(new_project)
                db.session.commit()
                flash('New project created successfully.', 'success')
            except Exception as e:
                db.session.rollback()
                flash(f'Failed to create project: {str(e)}', 'error')
        elif 'update_pending_project' in request.form:
            project_id = request.form["project_id"]
            end_date = request.form["end_date"]
            budget = request.form["budget"]

            try:
                # Update end_date and budget in the projects table
                db.session.execute(text("""
                    UPDATE projects
                    SET end_date = :end_date_param,
                        budget = :budget_param
                    WHERE project_id = :project_id_param
                """), {
                    'project_id_param': project_id,
                    'end_date_param': end_date,
                    'budget_param': budget
                })
                db.session.commit()
                
                flash('Project details updated successfully, and invoice trigger initiated.', 'success')
            except Exception as e:
                db.session.rollback()
                flash(f'Failed to update project details: {str(e)}', 'error')

    # Get all projects by status
    pending_projects = Project.query.filter_by(status="Pending").all()
    inprogress_projects = Project.query.filter_by(status="InProgress").all()

    # Get employee details
    employees = Employee.query.all()
    employee_details = []

    for employee in employees:
        tasks = Task.query.filter(Task.project_id == employee.project_id).all()
        projects = Project.query.filter_by(project_id=employee.project_id).all()
        teams = Team.query.filter_by(team_id=employee.team_id).all()

        employee_details.append({
            'employee': employee,
            'tasks': tasks,
            'projects': projects,
            'teams': teams
        })

    return render_template(
        "manager_dashboard.html", 
        pending_projects=pending_projects,
        inprogress_projects=inprogress_projects,
        employee_details=employee_details,
        employees=employees
    )


if __name__ == "__main__":
    app.run(debug=True)

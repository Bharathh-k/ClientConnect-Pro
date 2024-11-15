CREATE TABLE clients (
    client_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    address VARCHAR(200) NOT NULL,
    contact_no VARCHAR(15) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    industry VARCHAR(100) NOT NULL,
    company_size VARCHAR(50),
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(50) NOT NULL UNIQUE
);

CREATE TABLE projects (
    project_id SERIAL PRIMARY KEY,
    project_name VARCHAR(100) NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE,
    status VARCHAR(50) NOT NULL,
    budget FLOAT NOT NULL,
    client_id INTEGER REFERENCES clients(client_id) ON DELETE CASCADE
);

CREATE TABLE invoices (
    invoice_id SERIAL PRIMARY KEY,
    amount FLOAT NOT NULL,
    status VARCHAR(50) NOT NULL,
    invoice_date DATE NOT NULL,
    project_id INTEGER UNIQUE REFERENCES projects(project_id) ON DELETE CASCADE,
    client_id INTEGER REFERENCES clients(client_id) ON DELETE CASCADE
);

-- 4. Create the Tasks table
CREATE TABLE tasks (
    task_id SERIAL PRIMARY KEY,
    task_name VARCHAR(100) NOT NULL,
    description VARCHAR(250),
    deadline DATE NOT NULL,
    status VARCHAR(50) NOT NULL,
    project_id INTEGER REFERENCES projects(project_id) ON DELETE CASCADE,
    client_id INTEGER REFERENCES clients(client_id) ON DELETE CASCADE
);

CREATE TABLE teams (
    team_id SERIAL PRIMARY KEY,
    team_name VARCHAR(100) NOT NULL,
    description VARCHAR(250)
);

CREATE TABLE task_team (
    task_id INTEGER REFERENCES tasks(task_id) ON DELETE CASCADE,
    team_id INTEGER REFERENCES teams(team_id) ON DELETE CASCADE,
    PRIMARY KEY (task_id, team_id)
);

CREATE TABLE employees (
    employee_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    role VARCHAR(50) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    phno VARCHAR(15) NOT NULL,
    team_id INTEGER REFERENCES teams(team_id) ON DELETE SET NULL,
    project_id INTEGER REFERENCES projects(project_id) ON DELETE SET NULL
);

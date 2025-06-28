-- Table des utilisateurs
CREATE TABLE user (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    role TEXT CHECK(role IN ('gestion', 'commercial', 'support')) NOT NULL
);

-- Table des clients
CREATE TABLE client (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name TEXT NOT NULL,
    email TEXT NOT NULL,
    phone TEXT,
    company_name TEXT,
    created_date TEXT,
    last_contact_date TEXT,
    commercial_id INTEGER NOT NULL,
    FOREIGN KEY (commercial_id) REFERENCES user(id)
);

-- Table des contrats
CREATE TABLE contract (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    client_id INTEGER NOT NULL,
    commercial_id INTEGER NOT NULL,
    total_amount REAL NOT NULL,
    amount_due REAL NOT NULL,
    created_date TEXT NOT NULL,
    is_signed INTEGER NOT NULL CHECK(is_signed IN (0, 1)),
    FOREIGN KEY (client_id) REFERENCES client(id),
    FOREIGN KEY (commercial_id) REFERENCES user(id)
);

-- Table des événements
CREATE TABLE event (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    contract_id INTEGER NOT NULL,
    support_id INTEGER,
    start_date TEXT,
    end_date TEXT,
    location TEXT,
    attendees INTEGER,
    notes TEXT,
    FOREIGN KEY (contract_id) REFERENCES contract(id),
    FOREIGN KEY (support_id) REFERENCES user(id)
);

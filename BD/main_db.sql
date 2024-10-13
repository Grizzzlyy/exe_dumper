CREATE TABLE files (
        idx serial primary key ,
        username      TEXT,
        filetype      TEXT,
        header_first  JSON,
        header_second JSON,
        import_table  JSON,
        export_table  JSON,
        file_name     TEXT,
        FOREIGN KEY(username) REFERENCES users(username)
);

CREATE TABLE users (
    username TEXT PRIMARY KEY,
    is_admin BOOLEAN,
    is_blocked BOOLEAN,
    email TEXT,
    pwd_hash TEXT,
    two_factor_code TEXT NOT NULL DEFAULT 'NOT_BOUND'
);

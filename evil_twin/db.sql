create database evil;
create user evil_user with password 'evil_user_pass';

create table evil_info
(
    id       serial primary key,
    login    text,
    password text,
    unique (login, password)
);

grant connect on database evil to evil_user;

-- on evil db
grant usage on schema public to evil_user;
grant all privileges on all tables in schema public to evil_user;
grant all privileges on all sequences in schema public to evil_user;
grant create on schema public to evil_user;
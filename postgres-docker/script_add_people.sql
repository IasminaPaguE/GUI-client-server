INSERT INTO people (ssn, firstname, lastname, gender, age)
VALUES
  (200011, 'Ana', 'Popescu', 'F', 25),
  (200021, 'Mihai', 'Ionescu', 'M', 30),
  (200031, 'Elena', 'Georgescu', 'F', 28);


-- command to run this script:

-- psql -h <host> -p <port> -U <user> -d <database> -f seed_people.sql - if you have postgres installed locally
-- or
-- docker exec -it <container_name> psql -U <user> -d <database> -f /path/in/container/seed_people.sql - if using docker and the script is inside the container
-- or 
-- docker exec -i local_pgdb psql -U iasmina -d filetransfer < .\script_add_people.sql - if using docker and the script is on the host machine




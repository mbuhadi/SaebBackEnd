#! bash
rm db.sqlite3;
bash ./migrate.sh;
bash ./seed.sh;
bash ./runserver.sh;




# LMS Back-end

> Create a database and a user with the name of _lms_ then in _psql_ shell run: `grant all privileges on database lms to lms;`

### Setup and Run Server on VPS

```console 
sudo chmod +x app.sh && sudo pm2 start app.sh --name=lms
```

### Create `dev` and `lms` Superuser

```console 
cd lms && python manage.py createsuperuser
```

> `dev` is the staff but ain't `lms` 

> Inactive the staff status of `lms` with `dev` account

> Remember to create `superuser`, `admin`, `teacher` user groups and make `lms` and `dev` a user with group `superuser`

### Backup Commands

```console
pg_dump -U lms -W -F t lms > /home/lms/backups/lms.sql
``` 

```console
psql -U lms lms < lms.sql
```


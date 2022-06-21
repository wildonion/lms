


# Bitdad LMS Back-end

> Create a database and a user with the name of _bitdad_ then in _psql_ shell run: `grant all privileges on database bitdad to bitdad;`

### Setup and Run Server on VPS

```console 
sudo chmod +x app.sh && sudo pm2 start app.sh --name=lms
```

### Create `dev` and `bitdad` Superuser

```console 
cd lms && python manage.py createsuperuser
```

> `dev` is the staff but ain't `bitdad` 

> Inactive the staff status of `bitdad` with `dev` account

> Remember to create `superuser`, `admin`, `teacher` user groups and make `bitdad` and `dev` a user with group `superuser`

### Backup Commands

```console
pg_dump -U bitdad -W -F t bitdad > /home/bitdad/backups/bitdad.sql
``` 

```console
psql -U bitdad bitdad < bitdad.sql
```





### step 0

```console
$ sudo chown -R root:root /home/lms/LMS-Server/backups && sudo chmod -R 777 /home/lms/LMS-Server/backups
```

### Step 1

```console
$ suso cp .pgpass /home/lms/
```

### Step 2

```console
$ sudo chown -R root:root /home/lms/.pgpass
```

### Step 3

```console
$ crontab backup
```
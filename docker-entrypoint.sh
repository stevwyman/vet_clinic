#!/bin/sh

echo "building translations ..."
django-admin makemessages --all --ignore=env  
django-admin compilemessages --ignore=env 
echo "... translations compiled"

python vet/manage.py migrate

exec "$@"
Lost-Visions
============

pip install BeautifulSoup

pip install nltk

pip install pysolr

###On CentOS, for haystack
yum install libxslt-devel
pip install lxml --update

schema.xml should copied into solr conf

#in python
import nltk
nltk.download('stopwords')
nltk.download('wordnet')


git clone https://github.com/BL-Labs/imagedirectory
set british library data file location in "views"

download
http://geolite.maxmind.com/download/geoip/database/GeoLiteCity.dat.gz


#### On CentOS 6 with squashFS, this can be a pig.
yum install cmake28

openjpeg for jpeg2000
install from /tmp to avoid squashfs issues
svn checkout http://openjpeg.googlecode.com/svn/trunk/ openjpeg-read-only
cmake .
make
make install
sudo ldconfig

pip install pillow
### edit build directories setup.py to have jpeg2000 files in right place
nano /tmp/pip-build-root/pillow/setup.py
JPEG2K_ROOT = '/usr/lib64'
sudo pip install -e .

### add libopenjp2 libs to LD_LIBRARY_PATH
LD_LIBRARY_PATH=/usr/local/lib python /var/www/lost_visions/Lost-Visions/manage.py runfcgi host=127.0.0.1 port=8080

python-boost


### supervisord, environment var not working, so embedded in a script instead
    [program:django]
    command=/var/www/lost_visions/Lost-Visions/runme.sh
    ;command=gunicorn -c /var/www/lost_visions/Lost-Visions/crowdsource/gunicorn.settings crowdsource.wsgi:application
    ;environment=LD_LIBRARY_PATH="/usr/local/lib"

### runme.sh for supervisord

#!/bin/bash

export LD_LIBRARY_PATH="/usr/local/lib"
export PYTHONPATH="/var/www/lost_visions/Lost-Visions"
exec gunicorn -c /var/www/lost_visions/Lost-Visions/crowdsource/gunicorn.settings crowdsource.wsgi:application

### certbot

https://certbot.eff.org/lets-encrypt/centos6-nginx
/etc/cron.daily/certbot

    #!/bin/bash
    python -c 'import random; import time; time.sleep(random.random() * 3600)' && /usr/local/bin/certbot-auto renew && service nginx restart


### ReImagine change to nginx.conf
    client_max_body_size 20M;


Log files are all over the place:
root user (sudo su), /debug.log

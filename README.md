kc
==

All cryptographic keys in your organization are chosen with the utmost care! OpenSSL always creates secure keys! Broken random number generators are never deployed! Really? How could you know for sure? 

Your organization deploys many keys every year? Due to ignorance or software bugs some of them might be chosen badly and therefore compromise the encryption and authenticity of your electronic communication.
 
KeyCheck offers a solution to this problem by detecting weak keys ahead of their deployment. KeyCheck tests uploaded keys for several known weaknesses (common gcds, Debian weak key, nearly equal or small prime factors) and reports the result via an optional web-interface. The flexibility and easy expandability allow adapting easily to upcoming vulnerabilities by adding new tests or new clients to the web service. 

Dependencies
* relational database (only MySQL tested)
* python with standard library (tested version 2.7, version 3.x probably not running, the same holds for version 2.x with x < 7)
* OpenSSL and openssl-vulnkey
* SQLalchemy
* Flask
* gmpy
* database driver (the SQLalchemy error message will tell you the name of the required driver) for python


Clone this repo for using KeyCheck
Before starting KeyCheck open config.cfg and enter the correct database connection information in the section [db]
The possible values for Type are described here: http://docs.sqlalchemy.org/en/rel_0_9/core/engines.html
Host, User, Password should be self-explaining.

start keycheck from the directory kc with bin/keycheck.py 
The option -h displays a help-page
With the option --reset the initial database structure is created, all other data in the database is deleted

Examples of use:
python bin/keycheck.py -c all -k 1 -f test-data/debian-weak/1
Tests a sample key as user "all" with key reference 1 

python bin/keycheck.py -c all -r 1
Returns the result of test run 1 (watch out: test run is not the same as the key reference)

python bin/keycheck.py -b -s -f test-data/debian-weak/
Batch import the whole directory. Names of files has to be numbers. -s specifes silent input

python bin/keycheck.py -g -c global
Execute global tests as user global

python web.py
Starts the webserver. Open a new console for the following commands 

curl -L -F keyreference=1 -F key=@./1  http://127.0.0.1:5000/
Sends certificate file 1 with POST to the web server for testing. 

curl -L  http://127.0.0.1:5000/1
Gets the Result of test run 1 from the web server via GET. 


The configuration of the users and testsets is done in the database. An initial working config is created by --reset The relevant tables are: Client, Test_Set and Test
The client table contains the clients, their test set (each client has an unique test set) and the flag "admin" which decides whether the user has the right to see the revoked keys of other users
The table contains the ids and descriptions of the existing Test_Set.
The table Test says which test should be executed with which parameters in which tests set. The type describes, weather the test should be executed synchron (0), asynchron (1) or is a global test (2)

Bisher läuft / lief KeyCheck noch nie auf einem Apache Web-Server. Das Deployment von Flask-Applikationen wird hier beschrieben http://flask.pocoo.org/docs/0.10/deploying/
Dieser Anleitung werde ich folgen. Ob ich als Standardlösung FastCGI oder mod_wsgi vorsehen werde ist noch nicht geklärt. Die Konfigurationsdatei wird momentan im Verzeichnis erwartet, aus dem keycheck.py bzw web.py gestarted wird. Dies wäre ggf. anzupassen für den Apache Webserver anzupassen










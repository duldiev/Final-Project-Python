# Articles of Coin

## Installation

Install following packages. It also shown in requirements text file.
* Flask
* Flask_sqlalchemy
* Flask_WTF
* JWT
* flaskweb
* bs4, beautifulsoup4
* selenium

Just install them in the following way (Example 1):
```
pip install -U selenium

pip install bs4
```

#### As this program works directly with Firefox, you should install it on your computer.

## Usage

* Import those libraries
* Load the page at the given URL
* It automatically runs firefox to fetch the data
* Results will be shown on the web page

Set postgreSQL properties such user, password and database name with SQLALCHEMY_DATABASE_URI config (Example 2):

```
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://user:password@localhost:port/database_name'
```
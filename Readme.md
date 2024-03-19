# Cf-Bypasser
Bypass Cloudflare IUAM and Captcha Protected Site

Simple Python Script for Bypass Cloudflare IUAM and Captcha Protected Site.


## Usage 

1. `pip install -r requirements.txt`

2. `pip install gunicorn`

3. Edit file `app.py` on the line `9` you can change to the Web Target.

4. Run the code `gunicorn -w 4 -b 0.0.0.0:8080 wsgi:app`

5. Open the `localhost:8080/getcookie` for initialize get the Cloudflare cookie.

6. Enjoy


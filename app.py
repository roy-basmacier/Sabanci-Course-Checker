from flask import Flask, render_template, request
import requests
import lxml
from lxml import html
import time
import random
app = Flask(__name__)
import smtplib

def sendEmail(to, id):
    gmail_user = 'sabanci.class.checker'
    gmail_password = '5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8 '
    #email properties
    sent_from = gmail_user
    subject = 'Alert for course opening'
    email_text = 'There has been an opening for the course id: ' + id
    message = 'Subject: {}\n\n{}'.format(subject, email_text)
    #email send request
    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.ehlo()
        server.login(gmail_user, gmail_password)
        server.sendmail(sent_from, to, message)
        server.close()

        print('Email sent!')
    except Exception as e:
        print(e)
        print('Something went wrong...')



def checkSeats(URL, id_list, email, isDelay=False):
    if isDelay:
        time.sleep(random.randint(5, 15))

    course_no = random.choice(id_list)
    URL += course_no
    r = requests.get(URL)
    tree = lxml.html.fromstring(r.content)
    elms = tree.find_class('dddefault')

    cnt = 0
    data = []  # CAP , ACTUAL , REM
    for el in elms:
        if el.text_content().isdigit():
            cnt += 1
            data.append(int(el.text_content()))
        if cnt > 2:
            break

    if data[-1] > 0:
        print(data)
        print(('EMPTY SEAT FOUND AT ' + str(course_no)))
        # sendEmail(email, course_no)
        return course_no
    return 0

def test(load):
    print(load)
    URL = 'http://suis.sabanciuniv.edu/prod/bwckschd.p_disp_detail_sched?term_in=' + load['year'] + load['term'] + '&crn_in='
    classes = load['cids'].split(',')

    if load['checkone'] == 'on':
        looping = False
        while not looping:
            looping = checkSeats(URL, classes, load['email'], True)
        return looping
    else:
        while classes != []:
            remove_id = checkSeats(URL, classes, load['email'], True)
            if remove_id != 0:
                classes.remove(remove_id)
        return load['cids'].split(',')





@app.route('/')
def home():
   return render_template('home.html')

@app.route('/result',methods = ['POST', 'GET'])
def result():
   if request.method == 'POST':
      result = request.form
      result = test(result)
      return render_template("result.html", result = result)

if __name__ == '__main__':
   app.run(debug = True)
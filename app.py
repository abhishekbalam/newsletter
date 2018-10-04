import os
from flask import Flask, render_template, request, redirect, jsonify, abort
import requests
from flask_mail import Mail, Message
import db

app = Flask(__name__)

app.config['MAIL_SERVER']='smtp.zoho.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = os.environ['zoho_username']
app.config['MAIL_PASSWORD'] = os.environ['zoho_password']
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
app_token=os.environ['APP_TOKEN']


@app.route('/')	
def main():
	return render_template('index.html')

@app.route('/subscribed/<email>')	
def subscribed(email):
	if(db.validateuser(email)):
		return render_template('subscribed.html')
	else:
		text='Email does not exist.'
		return render_template('error.html', text=text, again=True)	

@app.route('/unsubscribe/<email>')	
def unsubscribe(email):
	if(db.deluser(email)):
		return render_template('unsubscribed.html')
	else:
		text='You are not subscribed to this newsletter.'
		return render_template('error.html',text=text, again=False)
		
@app.route('/users')	
def getusers():
	return jsonify(db.getusers())

@app.route('/deluser/<email>/<token>')	
def deluser(email,token):
	if(token!=app_token):
		abort(404)
	if(db.deluser(email)):
		return "Deleted User"
	else:
		return "User doesn't Exist"


def verify(email):
	token="7996de2b-d743-4536-a107-5252fec5c828"
	url="https://api.trumail.io/v2/lookups/json?email="+email+"&token="+token
	print(url)
	data=requests.get(url).json()
	return data['deliverable']

@app.route('/subscribe', methods = ['POST'])	
def subscribe():
	data=request.form
	firstname=data['firstname'].strip()
	lastname=data['lastname'].strip()
	email=data['email'].strip()

	if(verify(email)==False):
		text="Invalid Email"
		return render_template('error.html', text=text, again=True)

	url='https://www.google.com/recaptcha/api/siteverify'
	response=data['g-recaptcha-response']
	secret='6Ld2jGAUAAAAAM9VAACLMcFnsNlaiAHHZCsITeeQ'
	
	params= {'secret': secret, 'response': response }
	data=requests.post(url,data=params).json()
	status=data['success']
	
	print firstname+'<br>'+lastname+'<br>'+email+'<br>'+str(status)
	
	if (data['success']==True):
		if(db.adduser(firstname,lastname,email)):
			mail = Mail(app)
			msg = Message('Confirm Your Email', sender = ('Abhishek Balam', 'newsletter@abhishekbalam.xyz'), recipients = [email])
			msg.html = render_template('confirm.html', name=firstname, email=email) 
			mail.send(msg)
			
			return render_template('info.html')
		else:
			text='User Already Exists'
			return render_template('error.html', text=text, again=True)
	else:
		text='Invalid Captcha'
		return render_template('error.html', text=text, again=True)


	
@app.route('/publish/<token>')
def mail(token):
	if(token!=app_token):
		abort(404)	

	mail = Mail(app)
	url="https://abhishekbalam.xyz/newsletter/latest.json"
	data=requests.get(url).json()
	
	users=db.getusers()
	users=users.items()

	response='Newsletter Sent to the following emails:<br><ol>'
	for user in users:
		if('1' in user[1]):
			response+='<li>'+user[0]+'</li>'
	
	response+='</ol>'
	
	with mail.connect() as conn:
		for user in users:
			
			status=str(user[1].split(',')[2])
			
			if(status=='1'):
				lname=str(user[1].split(',')[1])
				fname=str(user[1].split(',')[0])
				email=user[0]
				subject='Abhishek Balam\'s Newsletter for '+data['date']
				msg = Message(subject, sender = ('Abhishek Balam', 'newsletter@abhishekbalam.xyz'), recipients = [email])
				msg.html = render_template('newsletter.html', data=data, name=fname, email=email)
				mail.send(msg)
				conn.send(msg)

	return response

if __name__ == '__main__':
	app.jinja_env.auto_reload = True
	app.config['TEMPLATES_AUTO_RELOAD'] = True
	# app.run(debug=True, port=4000)
	app.run(debug=True)
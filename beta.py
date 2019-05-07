from flask_mail import Message
from volsteads import mail
msg = Message('test subject', sender=volsteads.config['ADMINS'][0], recipients=["jkboline@gmail.com"])
.body = 'text body'
msg.html = '<h1>HTML BODY</h1>
mail.send(msg)
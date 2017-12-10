import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import asyncio

def send_mail(toaddr, emailsub, emailbody):
    
    print("SENDING MAIL")
    fromaddr = "rocket2512@gmail.com"
    msg = MIMEMultipart()
    msg['From'] = "Hotel California"
    msg['To'] = toaddr
    msg['Subject'] = emailsub
    body = emailbody
    msg.attach(MIMEText(body, 'plain'))

    #server connection and login 
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(fromaddr, "123anuj123")

    # concatanate whole body into a string
    text = msg.as_string() 

    #sending email and closing the instance
    server.sendmail(fromaddr, toaddr, text)
    server.quit()

if __name__ == '__main__':
    send_mail ("soni.sannisth@gmail.com", "Regarding room booking/cancellation", "welcome to hotel california!")


#our emailid and password = sannisth.130410116107@gmail.com, kaladeep

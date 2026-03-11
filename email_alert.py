import smtplib

def send_alert(message):

    sender = "your_email@gmail.com"
    receiver = "receiver@gmail.com"
    password = "your_app_password"

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(sender, password)
    server.sendmail(sender, receiver, message)
    server.quit()

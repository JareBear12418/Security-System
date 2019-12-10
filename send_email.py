import smtplib, os
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from datetime import datetime
def email_picture(name):
    #IMPORT FIELDS!!
    EMAIL = 'xxxxxxxxxxxxxx@gmail.com'
    EMAIL_TO = 'yyyyyyyyyyyy@gmail.com'
    EMAIL_PASSWORD = 'YOUR_EMAIL_PASSWORD'

    # Create the root message and fill in the from, to, and subject headers
    msgRoot = MIMEMultipart('related')
    msgRoot['Subject'] = 'ALERT!'
    msgRoot['From'] = EMAIL
    msgRoot['To'] = EMAIL_TO
    msgRoot.preamble = 'This is a multi-part message in MIME format.'

    # Encapsulate the plain and HTML versions of the message body in an
    # 'alternative' part, so message agents can decide which they want to display.
    msgAlternative = MIMEMultipart('alternative')
    msgRoot.attach(msgAlternative)
    # We reference the image in the IMG SRC attribute by the ID we give it below
    msgText = MIMEText(f'{datetime.now()}\n<br><img src="cid:image1"><img src="cid:image2"><br>', 'html')
    msgAlternative.attach(msgText)

    # Define the image's ID as referenced above
    for i, j in enumerate(name):
        with open(f'{os.path.dirname(os.path.realpath(__file__))}/Pics/{name[i]}', 'rb') as fp:
            msgImage = MIMEImage(fp.read())
            msgImage.add_header('Content-ID', f'<image>{i}')
            msgRoot.attach(msgImage)

    # Send the email (this example assumes SMTP authentication is required)
    smtp = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    smtp.login(EMAIL, EMAIL_PASSWORD)
    smtp.sendmail(EMAIL, EMAIL_TO, msgRoot.as_string())
    smtp.quit()

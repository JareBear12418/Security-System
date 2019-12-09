import smtplib
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from datetime import datetime
def email_picture(name):
    # Define these once; use them twice!
    strFrom = FROM
    strTo = TO

    # Create the root message and fill in the from, to, and subject headers
    msgRoot = MIMEMultipart('related')
    msgRoot['Subject'] = 'ALERT!'
    msgRoot['From'] = FROM
    msgRoot['To'] = TO
    msgRoot.preamble = 'This is a multi-part message in MIME format.'

    # Encapsulate the plain and HTML versions of the message body in an
    # 'alternative' part, so message agents can decide which they want to display.
    msgAlternative = MIMEMultipart('alternative')
    msgRoot.attach(msgAlternative)

    msgText = MIMEText('This is the alternative plain text message.')
    msgAlternative.attach(msgText)

    # We reference the image in the IMG SRC attribute by the ID we give it below
    msgText = MIMEText(f'{datetime.now()}\n<br><img src="cid:image1"><br>', 'html')
    msgAlternative.attach(msgText)

    # This example assumes the image is in the current directory
    fp = open(f'C:/Users/Jared/Documents/Python Scripts/Face Detection/Pics/{name}', 'rb')
    msgImage = MIMEImage(fp.read())
    fp.close()

    # Define the image's ID as referenced above
    msgImage.add_header('Content-ID', '<image1>')
    msgRoot.attach(msgImage)

    # Send the email (this example assumes SMTP authentication is required)
    smtp = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    smtp.login(EMAIL, EMAIL_PASSWORD)
    smtp.sendmail(strFrom, strTo, msgRoot.as_string())
    smtp.quit()

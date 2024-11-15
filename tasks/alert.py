import os
from dotenv import load_dotenv

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def create_email_template(receiver_name, content):
  logo = ""
  try:
    with open("logo.txt", "r") as f:
      logo = f.read()
  except:
    pass
  print(logo)
  html = f'''
  <html>
  <body style="font-family: Arial, sans-serif; margin: 0; padding: 0; background-color: #f2f2f2;">
  <div style="width: 100%; max-width: 600px; margin: 0 auto; background-color: #fff; padding: 20px;">
      <div style="display: flex; align-items: center;">
          <img src="{logo}" alt="Image" style="width: 100px; height: 100px; margin-right: 20px;">
          <div style="display: flex; flex-direction: column; justify-content: center;">
              <h2 style="font-size: 24px; margin: 0;">찾을수있을지도</h2>
              <p style="font-size: 16px; margin: 0;">Lost n' Found map</p>
          </div>
      </div>
      <div style="padding: 20px;">
        <p style="font-size: 16px;">
            안녕하세요, {receiver_name} 님, 분실물 찾기 서비스 <strong>찾을수있을지도</strong> 입니다.
        </p>
        <br>
        <p style="font-size: 16px;">
          귀하께서 분실한 물건과 유사한 분실물이 발견되었습니다. 해당 포스트를 확인해주세요.
        </p>
        <br>
        <p style="font-size: 16px;">
          {content}
        </p>
        <br>
        <p style="font-size: 16px;">
          감사합니다.
        </p>
      </div>
  </div>
  </body>
  </html>
  '''
  return html

def send_email(receiver_email, subject, body):
  message = MIMEMultipart()
  message["From"] = os.getenv("SMTP_ID")
  message["To"] = receiver_email
  message["Subject"] = subject
  message.attach(MIMEText(body, "html"))
  
  try:
    server = smtplib.SMTP(os.getenv("SMTP_HOST"), os.getenv("SMTP_TLS_PORT"))
    server.starttls()
    print(os.getenv("SMTP_ID"), os.getenv("SMTP_PW"))
    server.login(os.getenv("SMTP_ID"), os.getenv("SMTP_PW"))
    
    # send email
    
    server.sendmail(os.getenv("SMTP_ID"), receiver_email, message.as_string())
  except Exception as e:
    print(f"Failed to send email: {e}")
    return False
  finally:
    server.quit()
  
  return True
  
def send_alert(receiver_email, receiver_name, items):
  subject = "분실물 발견 추정 알림"
  content = create_email_template("홍길동", "청소기")
  
  return send_email(receiver_email, subject, content)


  
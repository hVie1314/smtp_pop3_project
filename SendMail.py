from email import encoders
from email.mime.base import MIMEBase
from email.utils import make_msgid
from socket import*
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import datetime
import mimetypes
import os

def get_file_type(file_path):
    file_type, _ = mimetypes.guess_type(file_path)
    return file_type

def Connect_to_server():

    #Choose mail server and port
    mail_server = "127.0.0.1"
    mail_port = 2225
    #---------------------------

    # Create socket called clientSocket and establish a TCP connection with mailserver
    
    clientSocket = socket(AF_INET,SOCK_STREAM)
    clientSocket.connect((mail_server,mail_port))
    
    #---------------------------

    # Receive the response message from the server
    recv = clientSocket.recv(1024).decode("utf-8")

    # If the first three digits of the response code indicate an error, print an error message
    if recv[:3] != "220":
     print("220 reply not received from server.")

    #---------------------------

    # Send HELO command and print server response
    heloCommand = "EHLO [{}]\r\n".format(mail_server)
    clientSocket.send(heloCommand.encode("utf-8"))
    recv = clientSocket.recv(1024).decode("utf-8")
  
    # If the first three digits of the response code indicate an error, print an error message
    if recv[:3] != "250":
     print("250 reply not received from server.")
     return
    #---------------------------

    return clientSocket


def SendMail(clientSocket,user_mail,mail_destination,CC_destination_mail,BCC_destination_mail,attached_files,
             mail_subject, mail_content):
   
   all_destination = []
   if(mail_destination != ""):
    all_destination.append(mail_destination)
   for items in CC_destination_mail:
    if(items != "" and all_destination.count(items) == 0):
       all_destination.append(items)
   for items in BCC_destination_mail:
    if(items != "" and all_destination.count(items) == 0):
       all_destination.append(items)
   
   # Send mail_from
   mailFrom = "MAIL FROM:<{}>\r\n".format(user_mail)
   clientSocket.send(mailFrom.encode("utf-8"))
   recv = clientSocket.recv(1024)
   
   # Send all recipients
   for item in all_destination:
     rcptTo = "RCPT TO:<{}>\r\n".format(item)
     clientSocket.send(rcptTo.encode("utf-8"))
     recv = clientSocket.recv(1024)

   # Send DATA command and print server response
   data = "DATA\r\n"
   clientSocket.send(data.encode("utf-8"))
   recv = clientSocket.recv(1024)
   

   message_id = make_msgid()

   time_send_mail = datetime.datetime.now().strftime('%a, %d %b %Y %H:%M:%S %z')

   #Set up MIME
   endmsg = "\r\n.\r\n"
   msg = MIMEMultipart()

   msg['Message-ID'] = message_id

   msg['Date'] = time_send_mail
   
   if(mail_destination != ""):
    msg['To'] = mail_destination
   
   if(len(CC_destination_mail) != 0):
    msg['CC'] = ', '.join(CC_destination_mail)
   
   if(mail_destination == "" and len(BCC_destination_mail) != 0 and len(CC_destination_mail) == 0):
    msg["To"] = "undisclose_recipient"

   msg['From'] = user_mail
   
   msg['Subject'] = mail_subject

   mail_content = MIMEText(mail_content)
   msg.attach(mail_content)


   for file_item in attached_files:
     size_of_file = os.path.getsize(file_item)/(1024*1024)

     if(size_of_file > 3):
      print("Your file is too large!!")
     else:
      with open(file_item, 'rb') as file:
       attachment = MIMEBase('application', {get_file_type(file_item)})
       attachment.set_payload(file.read())
       encoders.encode_base64(attachment)
       attachment.add_header('Content-Disposition', f'attachment; filename="{file_item}"')
       msg.attach(attachment)     
      


   clientSocket.sendall(msg.as_bytes())
   # Message ends with a single period
   clientSocket.send(endmsg.encode("utf-8"))

   print("Welcome to mail Client\n")





mail_destination = input("To: ")

CC_destination_mail = input("CC: ")

BCC_destination_mail = input("BCC: ")



#Process mail
if(CC_destination_mail != ""):
 CC_destination_mail = CC_destination_mail.split(",")

if(BCC_destination_mail != ""):
 BCC_destination_mail = BCC_destination_mail.split(",")

user_mail = "duonghuutuong@gmail.com"

mail_subject = input("Subject: ")

mail_content = input("Content:\n")

number_file = input("How many file do you want to attachment:")

attached_files = []


number_file = range(int(number_file))

for i in number_file:
    file_name = input("File {}: ".format(i+1))
    attached_files.append(file_name)

try:
 clientSocket = Connect_to_server()
except:
  print("Connecting To Server Failed !")
  exit()

try:
 SendMail(clientSocket,user_mail,mail_destination,CC_destination_mail,BCC_destination_mail,attached_files,mail_subject,mail_content)
except:
  print("Sending Mail Failed !")
  exit()
  
clientSocket.close()
   



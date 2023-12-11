from SendMail import*
#import socket
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
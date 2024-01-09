from my_libs import *
from smtp import *
from pop3 import *


def receive():
   print("1. Inbox ")
   print("2. Project")
   print("3. Important ")
   print("4. Work ")
   print("5. Spam ")


def printmenu():
   print("Please enter your option: ")
   print("1. To send an email ")
   print("2. To see your mailbox ")
   print("3. To exit ")


def clear_console():
   _ = os.system('cls')

   
 
def menu(download_path,server_address,username,server_smtp_port):
   clear_console()
   printmenu()
   option=int(input("Your option: "))
   while True :
      if option == 1 :
         print("This is the information for composing an email (if you don't want to fill it in, please press enter to skip): ")
         mail_destination = input("To: ")
         CC_destination_mail = input("CC: ")
         BCC_destination_mail = input("BCC: ")

         #Process mail
         if(mail_destination != ""):
            mail_destination = mail_destination.split(",")

         if(CC_destination_mail != ""):
            CC_destination_mail = CC_destination_mail.split(",")

         if(BCC_destination_mail != ""):
            BCC_destination_mail = BCC_destination_mail.split(",")
            
         mail_subject = input("Subject: ") 
         mail_content = input("Content (enter a dot (.) to end the content):\n")
         while True:
            ct = input("")
            if(ct == "."):
               break
            mail_content = mail_content + "\n" + ct
            
         attachment=int(input("Do you want to send attached file(s)? (0. No, 1. Yes): "))
         
         number_file=0
         if attachment==0 :
               number_file=0
         else :      
            number_file = input("Number of files to send:")
            

         attached_files = []
   
         number_file = int(number_file)
      
         i = 0
         while i < number_file:
            file_name = input("File {}: ".format(i+1))
            if(file_name == "0"):
               exit()
            if(file_name == "1"):
               break
            size_of_file = os.path.getsize(file_name)/(1024*1024)
            i = i + 1
            if(size_of_file > 3):
               print("The size of file number {} is larger than 3 MB, cannot send the file!".format(str(i)))
               print("Please choose a different file (or enter 0 to exit, enter 1 to send mail): ")
               i = i - 1
            else:
               attached_files.append(file_name)
            

         try:   
            clientsocket=Connect_to_server(server_address,server_smtp_port)
         except:
            print("Connecting To Server Failed !")
            exit()
            
         try:
            SendMail(clientsocket,username,mail_destination,CC_destination_mail,BCC_destination_mail,attached_files,mail_subject,mail_content)
         except:
            print("Sending Mail Failed !")
            exit()
            
         clientsocket.close()
         
      elif option == 2 : 
         clear_console()
         print("This is the list of folders in your mailbox: ")
         receive()
         folder=""
         folder = input("Which folder do you want to select? (or press enter to exit, press 0 to go back: ")
         if folder =='' :
            exit()
         else:
            folder=int(folder)
            while folder !=0:
               if folder == 1 :
                  inbox = os.path.join(download_path, "Inbox")
                  read_email_list = get_read_email_list(inbox)
                  print("This is the email list in your Inbox: ")
                  emaildoc=list_emails(inbox,read_email_list)
                  if emaildoc !=[] :
                     email=input("Which email do you want to read? (press enter to exit, press 0 to view the list of mail folders): ")
                     while email != "" and int(email) !=0:
                        email=int(email)
                        if email == 0 :
                           continue
                        else :
                           open_email_from_list(emaildoc,inbox,read_email_list,email)   
                        email=input("Which email do you want to read? (press enter to exit, press 0 to view the list of mail folders): ")
                     if email=="":
                        exit()
                  else :
                     set=input("Press 0 to go back")
                     if set!='0':
                        continue
               elif folder == 2:
                  project = os.path.join(download_path, "Project")
                  read_email_list = get_read_email_list(project)
                  emaildoc=list_emails(project,read_email_list)
                  if emaildoc !=[] :
                     email=input("Which email do you want to read? (press enter to exit, press 0 to view the list of mail folders): ")
                     while email != "" and int(email) !=0:
                        email=int(email)
                        if email == 0 :
                           continue
                        else :
                           open_email_from_list(emaildoc,project,read_email_list,email)   
                        email=input("Which email do you want to read? (press enter to exit, press 0 to view the list of mail folders): ") 
                     if email=="":
                        exit()
                  else :
                     set=input("Press 0 to go back")
                     if set!='0':
                        continue
               elif folder == 3:
                  important = os.path.join(download_path, "Important")
                  read_email_list = get_read_email_list(important)
                  emaildoc=list_emails(important,read_email_list)
                  if emaildoc !=[] :
                     email=input("Which email do you want to read? (press enter to exit, press 0 to view the list of mail folders): ")
                     while email != "" and int(email) !=0:
                        email=int(email)
                        if email == 0 :
                           continue
                        else :
                           open_email_from_list(emaildoc,important,read_email_list,email)   
                        email=input("Which email do you want to read? (press enter to exit, press 0 to view the list of mail folders): ") 
                     if email=="":
                        exit()
                  else :
                     set=input("Press 0 to go back")
                     if set!='0':
                        continue
               elif folder == 4:
                  work = os.path.join(download_path, "Work")
                  read_email_list = get_read_email_list(work)
                  emaildoc=list_emails(work,read_email_list)
                  if emaildoc !=[] :
                     email=input("Which email do you want to read? (press enter to exit, press 0 to view the list of mail folders): ")
                     while email != "" and int(email) !=0:
                        email=int(email)
                        if email == 0 :
                           continue
                        else :
                           open_email_from_list(emaildoc,work,read_email_list,email)   
                        email=input("Which email do you want to read? (press enter to exit, press 0 to view the list of mail folders): ") 
                     if email=="":
                        exit()
                  else :
                     set=input("Press 0 to go back")
                     if set!='0':
                        continue
               elif folder == 5:
                  spam = os.path.join(download_path, "Spam")
                  read_email_list = get_read_email_list(spam)
                  emaildoc=list_emails(spam,read_email_list)
                  if emaildoc !=[] :
                     email=input("Which email do you want to read? (press enter to exit, press 0 to view the list of mail folders): ")
                     while email != "" and int(email) !=0:
                        email=int(email)
                        if email == 0 :
                           continue
                        else :
                           open_email_from_list(emaildoc,spam,read_email_list,email)   
                        email=input("Which email do you want to read? (press enter to exit, press 0 to view the list of mail folders): ") 
                     if email=="":
                        exit()
                  else :
                     set=input("Press 0 to go back")
                     if set!='0':
                        continue
               clear_console()
               receive()
               folder=input("Which folder do you want to select? (or press enter to exit, press 0 to go back): ")
               if folder =='' :
                  exit()
               folder=int(folder)
      elif option==3 :
         exit()
      else :
         print("Please enter a valid option")
      printmenu()
      option=int(input("Your option: "))   
      

def main():
   #from smtp import Connect_to_server
   file_path = 'config.json'

   try:
      with open(file_path, 'r') as file:
         config_data = json.load(file)
         
   except FileNotFoundError:
      print(f"File '{file_path}' does not exist.")
   except Exception as e:
      print(f"Undefined error: {e}")
         
   server_address = config_data["General"]["MailServer"]
   server_smtp_port = config_data["General"]["SMTP"]
   server_pop3_port = config_data["General"]["POP3"]
   username = config_data["General"]["Username"]
   password = config_data["General"]["Password"]
   autoload = config_data["General"]["Autoload"]

   print("1. Auto login\n2. Manual login.\nEnter your option:")
   choice = int(input())
   if choice == 2:
      username = input("Username: ")
      password = input("Password: ")
      
         
   download_path = r"D:\\"
      # create folder to store email
   download_path = create_folders(download_path, username)
   # create thread to auto fetch email
   thread = threading.Thread(target=auto_fetch_email, args=(server_address, server_pop3_port, username, password, download_path, config_data))
   thread.daemon = True  
   thread.start()
   
   # main thread to print menu
   menu(download_path,server_address,username,server_smtp_port)


if __name__ == "__main__":
  main()
       
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
   print(" Vui lòng chọn menu ")
   print(" 1. Để gửi email ")
   print(" 2. Để xem danh sách các email đã nhận ")
   print(" 3. Thoát")


def clear_console():
   _ = os.system('cls')

   
 
def menu(download_path,server_address,username,server_smtp_port):
   clear_console()
   printmenu()
   option=int(input("Bạn chọn : "))
   while True :
      if option == 1 :
         print("Đây là thông tin soạn email(nếu không điền vui lòng nhấn enter để bỏ qua): ")
         mail_destination = input("To: ")
         CC_destination_mail = input("CC: ")
         BCC_destination_mail = input("BCC: ")

         #Process mail
         if(CC_destination_mail != ""):
            CC_destination_mail = CC_destination_mail.split(",")

         if(BCC_destination_mail != ""):
            BCC_destination_mail = BCC_destination_mail.split(",")
            
         mail_subject = input("Subject: ") 
         mail_content = input("Content:\n")
         attachment=int(input("Có gửi kèm file (0. Không, 1. Có): "))
         
         number_file=0
         if attachment==0 :
               number_file=0
         else :      
            number_file = input("Số lượng file muốn gửi:")
            

         attached_files = []
         number_file = range(int(number_file))

         for i in number_file:
            file_name = input("File {}: ".format(i+1))
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
         print(" Đây là danh sách các folder trong mailbox của bạn: ")
         receive()
         folder=""
         folder = input("Bạn muốn chọn folder nào(hoặc nhấn enter để thoát,nhấn 0 để quay lại): ")
         if folder =='' :
            exit()
         else:
            folder=int(folder)
            while folder !=0:
               if folder == 1 :
                  inbox = os.path.join(download_path, "Inbox")
                  read_email_list = get_read_email_list(inbox)
                  print("Đây là danh sách trong mục Inbox của bạn : ")
                  emaildoc=list_emails(inbox,read_email_list)
                  if emaildoc !=[] :
                     email=input(" Bạn muốn đọc email thứ mấy(nhấn enter để thoát, nhấn 0 để xem danh sách folder mail) : ")
                     while email != "" and int(email) !=0:
                        email=int(email)
                        if email == 0 :
                           continue
                        else :
                           open_email_from_list(emaildoc,inbox,read_email_list,email)   
                        email=input(" Bạn muốn đọc email thứ mấy(nhấn enter để thoát, nhấn 0 để xem danh sách folder mail) : ")
                     if email=="":
                        exit()
                  
               elif folder == 2:
                  project = os.path.join(download_path, "Project")
                  read_email_list = get_read_email_list(project)
                  emaildoc=list_emails(project,read_email_list)
                  if emaildoc !=[] :
                     email=input(" Bạn muốn đọc email thứ mấy(nhấn enter để thoát, nhấn 0 để xem danh sách folder mail) : ")
                     while email != "" and int(email) !=0:
                        email=int(email)
                        if email == 0 :
                           continue
                        else :
                           open_email_from_list(emaildoc,project,read_email_list,email)   
                        email=input(" Bạn muốn đọc email thứ mấy(nhấn enter để thoát, nhấn 0 để xem danh sách folder mail) : ") 
                     if email=="":
                        exit()
               elif folder == 3:
                  important = os.path.join(download_path, "Important")
                  read_email_list = get_read_email_list(important)
                  emaildoc=list_emails(important,read_email_list)
                  if emaildoc !=[] :
                     email=input(" Bạn muốn đọc email thứ mấy(nhấn enter để thoát, nhấn 0 để xem danh sách folder mail) : ")
                     while email != "" and int(email) !=0:
                        email=int(email)
                        if email == 0 :
                           continue
                        else :
                           open_email_from_list(emaildoc,important,read_email_list,email)   
                        email=input(" Bạn muốn đọc email thứ mấy(nhấn enter để thoát, nhấn 0 để xem danh sách folder mail) : ") 
                     if email=="":
                        exit()
               elif folder == 4:
                  work = os.path.join(download_path, "Work")
                  read_email_list = get_read_email_list(work)
                  emaildoc=list_emails(work,read_email_list)
                  if emaildoc !=[] :
                     email=input(" Bạn muốn đọc email thứ mấy(nhấn enter để thoát, nhấn 0 để xem danh sách folder mail) : ")
                     while email != "" and int(email) !=0:
                        email=int(email)
                        if email == 0 :
                           continue
                        else :
                           open_email_from_list(emaildoc,work,read_email_list,email)   
                        email=input(" Bạn muốn đọc email thứ mấy(nhấn enter để thoát, nhấn 0 để xem danh sách folder mail) : ") 
                     if email=="":
                        exit()
               elif folder == 5:
                  spam = os.path.join(download_path, "Spam")
                  read_email_list = get_read_email_list(spam)
                  emaildoc=list_emails(spam,read_email_list)
                  if emaildoc !=[] :
                     email=input(" Bạn muốn đọc email thứ mấy(nhấn enter để thoát, nhấn 0 để xem danh sách folder mail) : ")
                     while email != "" and int(email) !=0:
                        email=int(email)
                        if email == 0 :
                           continue
                        else :
                           open_email_from_list(emaildoc,spam,read_email_list,email)   
                        email=input(" Bạn muốn đọc email thứ mấy(nhấn enter để thoát, nhấn 0 để xem danh sách folder mail) : ") 
                     if email=="":
                        exit()
               clear_console()
               receive()
               folder=input("Bạn muốn chọn folder nào (hoặc nhấn enter để thoát, nhấn 0 để quay lại) : ")
               if folder =='' :
                  exit()
               folder=int(folder)
      elif option==3 :
         exit()
      else :
         print(" vui lòng lựa chọn cho đúng ")
      printmenu()
      option=int(input(" Bạn chọn : "))   
      

def main():
   #from smtp import Connect_to_server
   file_path = 'config.json'

   try:
      with open(file_path, 'r') as file:
         config_data = json.load(file)
         
   except FileNotFoundError:
      print(f"Tệp tin '{file_path}' không tồn tại.")
   except Exception as e:
      print(f"Lỗi không xác định: {e}")
         
   server_address = config_data["General"]["MailServer"]
   server_smtp_port = config_data["General"]["SMTP"]
   server_pop3_port = config_data["General"]["POP3"]
   username = config_data["General"]["Username"]
   password = config_data["General"]["Password"]
   autoload = config_data["General"]["Autoload"]

   print("1. Đăng nhập tự động\n2. Đăng nhập thủ công.\nNhập lựa chọn của bạn:")
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
       
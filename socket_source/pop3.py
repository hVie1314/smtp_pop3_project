import os
import time 
import json
import email
import socket
import threading
from socket import *

#active
def connect_and_authenticate(client_socket, server_address, server_port, username, password):
    try:
        client_socket.connect((server_address, server_port))
        client_socket.recv(1024).decode("utf-8")
    except Exception as e:
        print(f"Error connecting to server: {e}")
        exit()

    try:
        client_socket.sendall(f"USER {username}\r\n".encode("utf-8"))
        client_socket.recv(1024).decode("utf-8")
    except Exception as e:
        exit()

    try:
        client_socket.sendall(f"PASS {password}\r\n".encode("utf-8"))
        data = client_socket.recv(1024).decode("utf-8")
    except Exception as e:
        exit()

    if not data.startswith("+OK"):
        print("Authentication failed")
        exit()

    return client_socket


#active
def check_and_create_folder(folder_path):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path, exist_ok=True)
        
 
#active
# create folder in local machine to store emails       
def create_folders(download_path, username):    
    # create folder email
    download_path = os.path.join(download_path, '\emails')
    check_and_create_folder(download_path) 
     
    # create folder user
    download_path = os.path.join(download_path, username)
    check_and_create_folder(download_path)    
    
    folders = ["Inbox", "Project", "Important", "Work", "Spam"]
    for folder in folders:
        folder_path = os.path.join(download_path, folder)
        check_and_create_folder(folder_path)
    
    return download_path


#active
# check sefver has email or not
def check_server_emails(client_socket):
    try:
        client_socket.sendall("STAT\r\n".encode("utf-8"))
        stat_response = client_socket.recv(1024).decode("utf-8")

        if "+OK" not in stat_response:
            print("Failed to get email server status")
            return None
        
        num_emails = int(stat_response.split()[1])
        if num_emails == 0:
            client_socket.sendall("QUIT\r\n".encode("utf-8"))
            client_socket.close()
            return None  

        return get_email_list(client_socket)

    except Exception as e:
        print(f"Error checking server emails: {e}")
        return None


#active
# get email list from server
def get_email_list(client_socket):
    try:
        client_socket.sendall("LIST\r\n".encode("utf-8"))
        list_response = client_socket.recv(1024).decode("utf-8")

        if "+OK" not in list_response:
            print("Failed to get email list")
            return None

        emails_info = list_response.replace("+OK\r\n", "").replace("\r\n.\r\n", "").split("\r\n")
        fetched_emails = []

        client_socket.sendall("UIDL\r\n".encode("utf-8"))
        uidl_response = client_socket.recv(1024).decode("utf-8")

        email_ids = uidl_response.replace("+OK\r\n", "").replace("\r\n.\r\n", "").split("\r\n")
        
        for email_info, email_id in zip(emails_info, email_ids):
            email_number, email_size = email_info.split()
            email_number = int(email_number)
            email_id = email_id.split()[1]

            fetched_emails.append((email_number, email_size, email_id))

        return fetched_emails

    except Exception as e:
        print(f"Error getting email list: {e}")
        return None


#active
# delete email from server after fetch
def delete_emails(client_socket, fetched_emails):
    try:
        for email_number, _, _ in fetched_emails:
            client_socket.sendall(f"DELE {email_number}\r\n".encode("utf-8"))
            client_socket.recv(1024).decode("utf-8")
    
    except Exception as e:
        print(f"Error deleting emails: {e}")


# active
# get email content  
def extract_email_content(email_data):
    try:
        email_content = ''

        if email_data.is_multipart():
            for part in email_data.walk():
                content_type = part.get_content_type()
                if content_type == "text/plain":
                    charset = part.get_content_charset()
                    if charset:
                        email_content = part.get_payload(decode=True).decode(charset)
                    else:
                        email_content = part.get_payload()
                    break 
        else:
            content_type = email_data.get_content_type()
            if content_type == "text/plain":
                charset = email_data.get_content_charset()
                if charset:
                    email_content = email_data.get_payload(decode=True).decode(charset)
                else:
                    email_content = email_data.get_payload()

        return email_content
    
    except Exception as e:
        print(f"Error extract email content: {e}")


# active - need more test to make sure it all work
# filter emails to get path
def filter_email(email_raw, config_data, download_path):  
    try:        
        email_raw = email_raw.split('\n\n')
        email_raw = '\r\n'.join(email_raw)
        email_data = email.message_from_string(email_raw)
        email_from = email_data['from'].split('<')[-1].split('>')[0]
        email_subject = email_data['subject']
        email_content = extract_email_content(email_data)            
                
        filters = config_data["Filters"]
        
        for rule in filters:
            if "From" in rule and "Destination_from_folder" in rule:
                email_from_filter = rule["From"]
                from_folder = rule["Destination_from_folder"]
                
            if "Subject" in rule and "Destination_subject_folder" in rule:
                email_subject_filter = rule["Subject"]
                subject_folder = rule["Destination_subject_folder"]
                
            if "Content" in rule and "Destination_content_folder" in rule:
                email_content_filter = rule["Content"]
                content_folder = rule["Destination_content_folder"]
                
            if "Spam" in rule and "Destination_spam_folder" in rule:
                email_spam_filter = rule["Spam"]
                spam_folder = rule["Destination_spam_folder"]
        
        # adjust path
        if email_from in email_from_filter:
            return os.path.join(download_path, from_folder)
        for subject in email_subject_filter:
            if subject in email_subject:
                return os.path.join(download_path, subject_folder)
        for content in email_content_filter:
            if content in email_content:
                return os.path.join(download_path, content_folder)
        for spam in email_spam_filter:
            if spam in email_subject or spam in email_content:
                return os.path.join(download_path, spam_folder)
        
        return os.path.join(download_path, "Inbox")
    
    except Exception as e:
        print(f"Error filter emails: {e}")


# active
# fetch email from server then save to local machine
def fetch_email(server_address, server_port, username, password, download_path, config_data):
    connect_socket = socket(AF_INET,SOCK_STREAM)
    client_socket = connect_and_authenticate(connect_socket, server_address, server_port, username, password)

    try:
        fetched_emails = check_server_emails(client_socket)
        if fetched_emails:
            for email_number, email_size, email_id in fetched_emails:
                client_socket.sendall(f"RETR {email_number}\r\n".encode("utf-8"))
                email_raw = ""
                received_size = 0

                while received_size < int(email_size):
                    data = client_socket.recv(2048).decode("utf-8")
                    email_raw += data
                    received_size += len(data.encode("utf-8"))

                email_raw = email_raw.replace(f"+OK {email_size}\r\n", "").replace("\r\n.\r\n", "")

                # filter email to get path 
                download_path_updated = filter_email(email_raw, config_data, download_path)
                email_file_path = os.path.join(download_path_updated, f"{email_id}")

                with open(email_file_path, "w") as email_file:
                    email_file.write(email_raw)
                    
            # call function delete email to delete email from server     
            delete_emails(client_socket, fetched_emails) 
            
            client_socket.sendall("QUIT\r\n".encode("utf-8"))
            client_socket.close()

    except Exception as e:
        print(f"Error fetching emails: {e}")
    finally:
        client_socket.close()


# active 
# auto fetch email from server
def auto_fetch_email(server_address, server_port, username, password, download_path, config_data):
    while True:
        fetch_email(server_address, server_port, username, password, download_path, config_data)
        time.sleep(config_data["General"]["Autoload"])


# active 
def save_attachment(email_data):
    try:
        for part in email_data.walk():
            if part.get('Content-Disposition') is not None:
                file_name = part.get_filename()
                option = input(f"This email contains: {file_name} \nDo you want to save it?(Y/N): ").upper()
                match option:
                    case "Y":
                        directory = input("Enter directory: ")
                        with open(os.path.join(directory, file_name), 'wb') as file:
                            file.write(part.get_payload(decode = True))
                    case "N":
                        continue
                    case _:
                        print("Invalid option!")
                        continue

    except Exception as e:
        print(f"Error saving attachment: {e}")


# active - need more test to make sure it all work
# read email from local machine and print to screen
def read_email(email_file_path):
    try:
        with open(email_file_path, "r") as file:
            email_raw = file.read().split('\n\n')
            email_raw = '\r\n'.join(email_raw)
            email_data = email.message_from_string(email_raw)
            
            print(f"Date: {email_data['date']}")
            print(f"From: {email_data['from'].split('<')[-1].split('>')[0]}")
            print(f"To: {email_data['to']}")
            # not test in case cc and bcc
            print(f"Cc: {email_data['cc']}") if email_data['cc'] != None else ""
            print(f"Bcc: {email_data['bcc']}") if email_data['bcc'] != None else ""
            print(f"Subject: {email_data['subject']}")
            print(f"Content:\n {extract_email_content(email_data)}")

            save_attachment(email_data)
                            
    except FileNotFoundError:
        print("File not found.")
    except Exception as e:
        print(f"Error reading email: {e}")


# active 
def check_email_status(read_email_list, email_id):
    if email_id in read_email_list:
        return True
    return False


# active
# in case client closed or first run
def get_read_email_list(read_email_list_path):
    try:
        read_email_list = []
        read_email_list_path = os.path.join(read_email_list_path, "read_email_list.txt")
                    
        if not os.path.exists(read_email_list_path):
            with open(read_email_list_path, "w") as f:
                f.write("")
                
        else:   
            with open(read_email_list_path, "r") as f:
                read_email_list = f.readlines()
                # remove \n in each line
                read_email_list = [line.strip() for line in read_email_list]
                
        return read_email_list

    except Exception as e:
        print(f"Error get read email list: {e}")
        return []


# active
# param: read_email_list: golbal variable
# param: read_email_list_path: same folder with {id}.msg
def update_read_email_list(read_email_list, read_email_list_path, email_id):
    try:
        read_email_list_path = os.path.join(read_email_list_path, "read_email_list.txt")
        if not os.path.exists(read_email_list_path):
            with open(read_email_list_path, "w") as f:
                f.write("")

        existing_emails = []
        with open(read_email_list_path, "r") as f:
            existing_emails = f.readlines()

        if email_id not in existing_emails:
            with open(read_email_list_path, "a") as f:
                f.write(f"{email_id}\n")

        read_email_list.append(email_id)    

        return read_email_list

    except Exception as e:
        print(f"Error update read email list: {e}")
        return []
    

# active 
# list email from local machine
def list_emails(emails_file_path, read_email_list):
    emails_list = []

    if not os.path.exists(emails_file_path):
        print("Directory doesn't exist")
        return emails_list

    try:
        for index, filename in enumerate(os.listdir(emails_file_path), start=1):
            file_path = os.path.join(emails_file_path, filename)
            if os.path.isfile(file_path) and filename.endswith('.msg'):
                with open(file_path, "r") as file:
                    email_raw = file.read().split('\n\n')
                    email_raw = '\r\n'.join(email_raw)
                    email_data = email.message_from_string(email_raw)
                    
                    sender = email_data['from'].split('<')[-1].split('>')[0]
                    subject = email_data['subject']
                    email_id = filename.split(".")[0] 

                    email_info = f"{sender}, {subject}"
                    emails_list.append((email_id, email_info))

                    if (check_email_status(read_email_list, email_id)):
                        print(f"{index}. <{sender}> <{subject}>")
                    else:
                        print(f"{index}. (chưa đọc) <{sender}> <{subject}>")
        
        if not emails_list:
            print("You haven't received any emails in this folder.")

    except Exception as e:
        print(f"Error listing emails: {e}")

    return emails_list



# active
# open email from local machine
# index: input from user
def open_email_from_list(emails_list, emails_file_path, read_email_list, index):
    if not emails_list:
        print("No emails to open.")
        return

    try:
        if 1 <= index <= len(emails_list):
            email_id, email_info = emails_list[index - 1]
            file_path = os.path.join(emails_file_path, f"{email_id}.msg")
            read_email(file_path)
            update_read_email_list(read_email_list, emails_file_path, email_id)
        else:
            print("Invalid index. Please choose a valid index from the list.")
    except Exception as e:
        print(f"Error opening email: {e}")


def main():
    # load data from config.json
    with open('./config.json', 'r') as config_file:
        config_data = json.load(config_file)
        
    server_address = config_data["General"]["MailServer"]
    server_pop3_port = config_data["General"]["POP3"]
    username = config_data["General"]["Username"]
    password = config_data["General"]["Password"]
    autoload = config_data["General"]["Autoload"]
    
    # set download path
    download_path = r"D:"
    # create folder to store email
    download_path = create_folders(download_path, username) 
    
    # set up file and array to store read email
    # read_email_list_path = os.path.join(download_path, 'emails', username, 'read_email_list.txt')
    # read_email_list = get_read_email_list(read_email_list_path)

    # create thread to auto fetch email
    # thread = threading.Thread(target=auto_fetch_email, args=(server_address, server_pop3_port, username, password, download_path, config_data))
    # thread.daemon = True  
    # thread.start()

    # fetch_email(server_address, server_pop3_port, username, password, download_path, config_data)
    
    download_path = "D:\emails\hoangviet@gmail.com\Inbox"
    # path = os.path.join(path, "20231222234933854.msg")
    # read_email(path)
    
    
    read_email_list = get_read_email_list(download_path)
    # print(read_email_list)
    
    # read_email_list = update_read_email_list(read_email_list, download_path, "12345.msg")
    # print(read_email_list)

    
    emails_list = list_emails(download_path, read_email_list)
    index = 1 # input from user
    open_email_from_list(emails_list, download_path, read_email_list, index)
    
if __name__ == "__main__":
   main()
   

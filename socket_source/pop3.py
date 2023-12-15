import os
import time 
import json
import socket
import threading
from email.parser import BytesParser


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


def check_and_create_folder(folder_path):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path, exist_ok=True)
        
 
# create folder in local machine to store emails       
def create_folders(download_path, username):    
    # create folder email
    download_path = os.path.join(download_path, 'emails')
    check_and_create_folder(download_path) 
     
    # create folder user
    download_path = os.path.join(download_path, username)
    check_and_create_folder(download_path)    
    
    folders = ["Inbox", "Project", "Important", "Work", "Spam"]
    for folder in folders:
        folder_path = os.path.join(download_path, folder)
        check_and_create_folder(folder_path)


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


# get email list from server
def get_email_list(client_socket):
    try:
        client_socket.sendall("LIST\r\n".encode("utf-8"))
        list_response = client_socket.recv(1024).decode("utf-8")

        if "+OK" not in list_response:
            print("Failed to get email list")
            return None

        emails_info = list_response.split("\r\n")[1:-3] # eliminate +OK and \r\n.\r\n
        fetched_emails = []

        client_socket.sendall("UIDL\r\n".encode("utf-8"))
        uidl_response = client_socket.recv(1024).decode("utf-8")

        email_ids = uidl_response.split("\r\n")[1:-3]

        for email_info, email_id in emails_info, email_ids:
            email_number, email_size = email_info.split()
            email_number = int(email_number)
            email_id = email_id.split()[1]

            fetched_emails.append((email_number, email_size, email_id))

        return fetched_emails

    except Exception as e:
        print(f"Error getting email list: {e}")
        return None

# delete email from server after fetch
def delete_emails(client_socket, fetched_emails):
    try:
        for email_number, _, _ in fetched_emails:
            client_socket.sendall(f"DELE {email_number}\r\n".encode("utf-8"))
            client_socket.recv(1024).decode("utf-8")
    
    except Exception as e:
        print(f"Error deleting emails: {e}")


# filter emails to get path
def filter_email(email_content, config_data, download_path):
    msg = BytesParser().parse(email_content)
    email_from = msg['From']
    email_subject = msg['Subject']
    for part in msg.walk():
        if part.get_content_type() == "text/plain":
            email_content = part.get_payload(decode=True).decode("utf-8")
            
    filters = config_data["Filters"]
    
    for rule in filters:
        email_from_filter = rule["From"]
        email_subject_filter = rule["Subject"]
        email_content_filter = rule["Content"]
        email_spam_filter = rule["Spam"]

        for from_filter in email_from_filter:
            if from_filter in email_from:
                return os.path.join(download_path, rule["Destination_from_folder"])
            
        for subject_filter in email_subject_filter:
            if subject_filter in email_subject:
                return os.path.join(download_path, rule["Destination_subject_folder"])
            
        for content_filter in email_content_filter:
            if content_filter in email_content:
                return os.path.join(download_path, rule["Destination_content_folder"])
        
        for spam_filter in email_spam_filter:
            if spam_filter in email_subject or spam_filter in email_content:
                return os.path.join(download_path, rule["Destination_spam_folder"])
    

# fetch email from server then save to local machine
def fetch_email(server_address, server_port, username, password, download_path, config_data):
    connect_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket = connect_and_authenticate(connect_socket, server_address, server_port, username, password)

    try:
        fetched_emails = check_server_emails(client_socket)
        if fetched_emails:
            for email_number, email_size, email_id in fetched_emails:
                client_socket.sendall(f"RETR {email_number}\r\n".encode("utf-8"))
                email_content = ""
                received_size = 0

                while received_size < int(email_size):
                    data = client_socket.recv(2048).decode("utf-8")
                    email_content += data
                    received_size += len(data.encode("utf-8"))

                email_content = email_content.replace("+OK\r\n", "").replace("\r\n.\r\n", "")
                
                # filter email to get path 
                download_path_updated = filter_email(email_content, config_data, download_path)
                email_file_path = os.path.join(download_path_updated, f"{email_id}")
                with open(email_file_path, "w") as email_file:
                    email_file.write(email_content)
                    
            # call function delete email to delete email from server     
            delete_emails(client_socket, fetched_emails) 
            
            client_socket.sendall("QUIT\r\n".encode("utf-8"))
            client_socket.close()

    except Exception as e:
        print(f"Error fetching emails: {e}")
    finally:
        client_socket.close()

# auto fetch email from server
def auto_fetch_email(server_address, server_port, username, password, download_path, autoload):
    while True:
        fetch_email(server_address, server_port, username, password, download_path)
        time.sleep(autoload)


def save_attachments(part, download_folder):
    file_name = part.get_filename()
    if file_name:
        file_path = os.path.join(download_folder, file_name)
        if not os.path.isfile(file_path):
            with open(file_path, "wb") as attachment:
                payload = part.get_payload(decode=True)
                attachment.write(payload)
                print(f"Attachment '{file_name}' saved to '{download_folder}'")
        else:
            print(f"File '{file_name}' already exists in '{download_folder}'. Skipped.")


# read email from local machine and print to screen
def read_email(email_file_path):
    try:
        with open(email_file_path, "rb") as email_file:
            msg = BytesParser().parse(email_file)

            print(f"Date: {msg['Date']}")
            print(f"From: {msg['From']}")
            print(f"To: {msg['To']}")
            print(f"Cc: {msg['Cc'] if 'Cc' in msg else ''}")
            print(f"Bcc: {msg['Bcc'] if 'Bcc' in msg else ''}")
            print(f"Subject: {msg['Subject']}")

            for part in msg.walk():
                if part.get_content_type() == "text/plain":
                    print("Email content:\n")
                    print(part.get_payload(decode=True).decode("utf-8"))

                if part.get('Content-Disposition') is not None:
                    file_name = part.get_filename()
                    if file_name:
                        download_choice = input(f"Download '{file_name}' (y/n)? ").lower()
                        if download_choice == "y":
                            download_folder = input("Enter download path: ")
                            save_attachments(part, download_folder)
                        else:
                            print(f"Skipping download of '{file_name}'")
                            
    except FileNotFoundError:
        print("File not found.")
    except Exception as e:
        print(f"Error reading email: {e}")


def check_email_status(read_email_list, email_id):
    if email_id in read_email_list:
        return True
    return False


# in case client closed or first run
def get_read_email_list(read_email_list_path):
    read_email_list = []
    if not os.path.exists(read_email_list_path):
        with open(read_email_list_path, "w") as f:
            f.write("")
            
    else:   
        with open(read_email_list_path, "r") as f:
            read_email_list = f.readlines()
            
    return read_email_list


# param: read_email_list: golbal variable
# param: read_email_list_path: same folder with {id}.msg
def update_read_email_list(read_email_list, read_email_list_path, email_id):
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


# list email from local machine
def list_emails(emails_file_path, read_email_list):
    email_list = []

    if not os.path.exists(emails_file_path):
        print("Directory doesn't exist")
        return email_list

    try:
        for filename in os.listdir(emails_file_path):
            file_path = os.path.join(emails_file_path, filename)
            if os.path.isfile(file_path) and filename.endswith('.msg'):
                with open(file_path, "rb") as email_file:
                    msg = BytesParser().parse(email_file)

                    sender = msg['From']
                    subject = msg['Subject']
                    email_id = filename.split(".")[0] 

                    email_info = f"{sender}, {subject}"
                    email_list.append((email_id, email_info))

        if email_list:
            print("List of emails:")
            for index, (email_id, email_info) in enumerate(email_list, 1):
                if (check_email_status(read_email_list, email_id)):
                    print(f"{index}. {email_info}")
                else:
                    print(f"{index}. (chưa đọc) {email_info}")
        else:
            print("No emails found in the directory.")

        return email_list

    except Exception as e:
        print(f"Error listing emails: {e}")
        return email_list

# open email from local machine
# index: input from user
def open_email_from_list(email_list, emails_file_path, index, read_email_list):
    if not email_list:
        print("No emails to open.")
        return

    try:
        if 1 <= index <= len(email_list):
            email_id,  = email_list[index - 1]
            file_path = os.path.join(emails_file_path, f"{email_id}")
            read_email(file_path)
            update_read_email_list(read_email_list, email_id)
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
    download_path = r'D:\\'
    # create folder to store email
    create_folders(download_path, username) 
    
    # set up file and array to store read email
    read_email_list_path = os.path.join(download_path, 'emails', username, 'read_email_list.txt')
    read_email_list = get_read_email_list(read_email_list_path)

    # create thread to auto fetch email
    thread = threading.Thread(target=auto_fetch_email, args=(server_address, server_pop3_port, username, password, download_path, autoload))
    thread.daemon = True  
    thread.start()

    # code ...

if __name__ == "__main__":
    main()

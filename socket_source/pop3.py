import os
import time 
import json
import socket
import threading
from email.parser import BytesParser


def connect_and_authenticate(client_socket, server_address, server_port, username, password):
    try:
        client_socket.connect((server_address, server_port))
    except Exception as e:
        print(f"Error connecting to server: {e}")
        exit()

    try:
        data = client_socket.recv(1024).decode("utf-8")
        print("Server:", data)
    except Exception as e:
        exit()

    try:
        client_socket.sendall(f"USER {username}\r\n".encode("utf-8"))
        data = client_socket.recv(1024).decode("utf-8")
        print("Server:", data)
    except Exception as e:
        exit()

    try:
        client_socket.sendall(f"PASS {password}\r\n".encode("utf-8"))
        data = client_socket.recv(1024).decode("utf-8")
        print("Server:", data)
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
    folder_path = os.path.join(download_path, 'emails')
    check_and_create_folder(folder_path)  # create folder email
    
    download_path = download_path + 'emails'    # move to folder email 
    folder_path = os.path.join(download_path, username)
    check_and_create_folder(folder_path)    # create folder user
    
    download_path = download_path + '\\' + username #move to folder user
    
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


def get_email_list(client_socket):
    try:
        client_socket.sendall("LIST\r\n".encode("utf-8"))
        list_response = client_socket.recv(1024).decode("utf-8")

        if "+OK" not in list_response:
            print("Failed to get email list")
            return None

        emails_info = list_response.split("\r\n")[1:-2]
        fetched_emails = []

        for email_info in emails_info:
            email_number, email_size = email_info.split()
            email_number = int(email_number)

            client_socket.sendall(f"UIDL {email_number}\r\n".encode("utf-8"))
            uidl_response = client_socket.recv(1024).decode("utf-8")
            email_id = uidl_response.split()[2].split(".")[0]

            fetched_emails.append((email_number, email_size, email_id))

        return fetched_emails

    except Exception as e:
        print(f"Error getting email list: {e}")
        return None

# fetch email from server then save to local machine
def fetch_email(server_address, server_port, username, password, download_path):
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
                    data = client_socket.recv(1024).decode("utf-8")
                    email_content += data
                    received_size += len(data.encode("utf-8"))

                email_content = email_content.replace("+OK\r\n", "").replace("\r\n.\r\n", "")

                email_file_path = os.path.join(download_path, f"{email_id}.msg")
                with open(email_file_path, "w") as email_file:
                    email_file.write(email_content)
                    
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
            print(f"Subject: {msg['Subject']}")

            for part in msg.walk():
                if part.get_content_type() == "text/plain":
                    print("Email content:")
                    print(part.get_payload(decode=True).decode("utf-8"))

                if part.get_content_maintype() == 'multipart':
                    for attachment in part.walk():
                        if attachment.get('Content-Disposition'):
                            file_name = attachment.get_filename()
                            if file_name:
                                print(f"Found attachment: {file_name}")
                                choice = input(f"Download attachment '{file_name}'? (yes/no): ").lower()
                                if choice == 'yes':
                                    download_folder = input("Enter download path: ")
                                    save_attachments(attachment, download_folder)
                                else:
                                    print(f"Skipping download of '{file_name}'")

    except FileNotFoundError:
        print("File not found.")
    except Exception as e:
        print(f"Error reading email with attachments: {e}")

# list email from local machine
def list_emails(emails_file_path):
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
            for index, (_, email_info) in enumerate(email_list, 1):
                print(f"{index}. {email_info}")
        else:
            print("No emails found in the directory.")

        return email_list

    except Exception as e:
        print(f"Error listing emails: {e}")
        return email_list

# open email from local machine
def open_email_from_list(email_list, emails_file_path, index):
    if not email_list:
        print("No emails to open.")
        return

    try:
        if 1 <= index <= len(email_list):
            email_id, email_info = email_list[index - 1]
            file_path = os.path.join(emails_file_path, f"{email_id}.msg")
            read_email(file_path)
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

    # create thread to auto fetch email
    thread = threading.Thread(target=auto_fetch_email, args=(server_address, server_pop3_port, username, password, download_path, autoload))
    thread.daemon = True  
    thread.start()

    # code ...

if __name__ == "__main__":
    main()

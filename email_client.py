import socket
import os
import threading
import email
from email.parser import BytesParser


def connect_and_authenticate(client_socket, server_address, server_port, username, password):
    try:
        client_socket.connect((server_address, server_port))
    except Exception as e:
        print(f"Error connecting to server: {e}")
        exit()

    try:
        data = client_socket.recv(1024).decode()
        print("Server:", data)
    except Exception as e:
        print(f"Error receiving data: {e}")
        exit()

    try:
        client_socket.sendall(f"USER {username}\r\n".encode())
        data = client_socket.recv(1024).decode()
        print("Server:", data)
    except Exception as e:
        print(f"Error sending USER command: {e}")
        exit()

    try:
        client_socket.sendall(f"PASS {password}\r\n".encode())
        data = client_socket.recv(1024).decode()
        print("Server:", data)
    except Exception as e:
        print(f"Error sending PASS command: {e}")
        exit()

    if not data.startswith("+OK"):
        print("Authentication failed")
        exit()

    return client_socket


def check_and_create_folder(folder_path):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path, exist_ok=True)
        
        
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


# D:\\emails\{username}\Inbox
def get_fetched_emails(download_path):
    fetched_emails = []
    files = os.listdir(download_path)
    for file_name in files:
        if file_name.endswith(".msg"):
            email_id = int(file_name.split(".")[0])
            fetched_emails.append(email_id)
    return fetched_emails


def check_unfetched_emails(client_socket, fetched_emails):
    try:
        client_socket.sendall("LIST\r\n".encode())
        data = client_socket.recv(1024).decode()

        if "+OK\r\n.\r\n" in data:
            print("No emails available on server.")
            return None

        emails_info = data.split("\r\n")[1:-2]

        unfetched_emails = []

        if emails_info:
            for email_info in emails_info:
                email_number, email_size = email_info.split()
                email_number = int(email_number)
                email_size = int(email_size)

                if email_number not in downloaded_emails:
                    unfetched_emails.append((email_number, email_size))

        return unfetched_emails if unfetched_emails else None

    except Exception as e:
        print(f"Error checking unfetched emails: {e}")
        return None


def download_unfetched_emails(client_socket, unfetched_emails, download_path):
    try:
        for email_number, email_size in unfetched_emails:
            client_socket.sendall(f"RETR {email_number}\r\n".encode())

            email_content = ""
            received_size = 0
            while received_size < email_size:
                data = client_socket.recv(1024 * 3).decode()
                email_content += data
                received_size += len(data.encode("utf-8"))

            email_file_path = os.path.join(download_path, f"{email_number}.msg")
            with open(email_file_path, "w") as email_file:
                email_file.write(email_content)

    except Exception as e:
        print(f"Error downloading unfetched emails: {e}")


def download_attachment(part, download_folder):
    file_name = part.get_filename()
    if file_name:
        file_path = os.path.join(download_folder, file_name)
        if not os.path.isfile(file_path):
            with open(file_path, "wb") as attachment:
                attachment.write(part.get_payload(decode=True))
                print(f"Attachment '{file_name}' downloaded to '{download_folder}'")
        else:
            print(f"File '{file_name}' already exists in '{download_folder}'")


def read_email_with_attachments(email_file_path):
    try:
        with open(email_file_path, "rb") as email_file:
            msg = BytesParser().parse(email_file)

            # In thông tin cơ bản của email
            print(f"Date: {msg['Date']}")
            print(f"From: {msg['From']}")
            print(f"To: {msg['To']}")
            print(f"Subject: {msg['Subject']}")

            # In nội dung email
            for part in msg.walk():
                if part.get_content_type() == "text/plain":
                    print("Email content:")
                    print(part.get_payload(decode=True).decode("utf-8"))

            # Kiểm tra và tải xuống các tệp đính kèm nếu có
            for part in msg.walk():
                if part.get_content_maintype() == 'multipart':
                    continue
                if part.get('Content-Disposition') is None:
                    continue

                file_name = part.get_filename()
                if file_name:
                    choice = input(f"Found attachment '{file_name}'. Download? (yes/no): ").lower()
                    if choice == 'yes':
                        download_folder = input("Enter download path: ")
                        download_attachment(part, download_folder)
                    else:
                        print(f"Skipping download of '{file_name}'")

    except FileNotFoundError:
        print("File not found.")
    except Exception as e:
        print(f"Error reading email with attachments: {e}")


def list_emails(directory):
    email_list = []

    if not os.path.exists(directory):
        print("Directory doesn't exist")
        return email_list

    try:
        for filename in os.listdir(directory):
            file_path = os.path.join(directory, filename)
            if os.path.isfile(file_path):
                with open(file_path, "rb") as email_file:
                    msg = BytesParser().parse(email_file)

                    sender = msg['From']
                    subject = msg['Subject']

                    email_list.append(f"{sender}, {subject}")

        if email_list:
            print("List of emails:")
            for index, email_info in enumerate(email_list, 1):
                print(f"{index}. {email_info}")
        else:
            print("No emails found in the directory.")

        return email_list

    except Exception as e:
        print(f"Error listing emails: {e}")
        return email_list


def open_email_from_list(email_list, directory, index):
    if not email_list:
        print("No emails to open.")
        return

    try:
        if 1 <= index <= len(email_list):
            email_info = email_list[index - 1]

            file_path = os.path.join(directory, f"email_{index}.msg")
            read_email_with_attachments(file_path)
        else:
            print("Invalid index. Please choose a valid index from the list.")
    except Exception as e:
        print(f"Error opening email: {e}")


def fetch_email(server_address, server_port, username, password, download_path):
    connect_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket = connect_and_authenticate(connect_socket, server_address, server_port, username, password)

    downloaded_emails = get_fetched_emails(download_path)
    unfetched = check_unfetched_emails(client_socket, downloaded_emails)

    if unfetched:
        download_unfetched_emails(client_socket, unfetched, download_path)

    client_socket.close()
    
def auto_fetch_email(server_address, server_port, username, password, download_path, interval):
    while True:
        fetch_email(server_address, server_port, username, password, download_path)
        time.sleep(interval)


def main():
    server_address = 'localhost'
    server_port = 3335

    username = input("Enter your username: ")
    password = input("Enter your password: ")

    download_path = r'D:\\'
    create_folders(download_path, username)

    fetch_interval = 10  

    thread = threading.Thread(target=auto_fetch_email, args=(server_address, server_port, username, password, download_path, fetch_interval))
    thread.daemon = True  
    thread.start()

    emails = list_emails(download_path)
    display_email_list(emails)

    # Mở email từ danh sách
    while True:
        try:
            choice = int(input("Enter the number of the email you want to open (0 to exit): "))
            if choice == 0:
                break

            if 1 <= choice <= len(emails):
                selected_email = emails[choice - 1]
                email_file_path = os.path.join(download_path, f"{selected_email}.msg")
                read_email_with_attachments(email_file_path)
                display_email_list(emails)
            else:
                print("Invalid choice. Please select a valid email number.")

        except ValueError:
            print("Invalid input. Please enter a number.")

if __name__ == "__main__":
    main()

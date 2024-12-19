import socket

# Function to send a math expression to the server and get the result
def request_math_result():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(('127.0.0.1', 5555))  # Connect to the server

    # Send the expression to the server
    client.send(input("Enter a math expression (e.g., 3 + 5): ").encode('utf-8'))

    # Receive the result from the server
    response = client.recv(1024).decode('utf-8')
    print(f"Server response: {response}")

    # Close the connection
    client.close()

if __name__ == "__main__":
    request_math_result()
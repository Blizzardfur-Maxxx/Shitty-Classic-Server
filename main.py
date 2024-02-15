import socket
import time
import struct

# Define constants
SERVER_IP = '127.0.0.1'
SERVER_PORT = 8888
PROTOCOL_VERSION = 0x07
SERVER_NAME = "MyServer"
SERVER_MOTD = "Welcome to MyServer!"
USER_TYPE_OP = 0x64
USER_TYPE_NORMAL = 0x00

# Packet IDs
PACKET_ID_SERVER_IDENTIFICATION = 0x00
PACKET_ID_PING = 0x01

# Function to send server identification packet
def send_server_identification(client_socket):
    packet = struct.pack('BB64s64sB', PACKET_ID_SERVER_IDENTIFICATION, PROTOCOL_VERSION, SERVER_NAME.encode('ascii'), SERVER_MOTD.encode('ascii'), USER_TYPE_OP)
    client_socket.sendall(packet)

# Function to send ping packet
def send_ping_packet(client_socket):
    packet = struct.pack('B', PACKET_ID_PING)
    client_socket.sendall(packet)

# Function to send level initialize packet
def send_level_initialize_packet(client_socket):
    packet_id = 0x02
    packet = struct.pack('B', packet_id)
    client_socket.sendall(packet)

# Function to send level data chunk packet
def send_level_data_chunk_packet(client_socket, chunk_length, percent_complete):
    packet_id = 0x03
    chunk_data = b'\x00' * 1024  # 1024 bytes of 0x00s
    packet = struct.pack('Bh1024sB', packet_id, chunk_length, chunk_data, percent_complete)
    client_socket.sendall(packet)

# Function to send level finalize packet
def send_level_finalize_packet(client_socket):
    packet_id = 0x04
    x_size = 512
    y_size = 98
    z_size = 512
    packet = struct.pack('Bhhh', packet_id, x_size, y_size, z_size)
    client_socket.sendall(packet)

# Function to send spawn player packet
def send_spawn_player_packet(client_socket, player_id, player_name, x, y, z, yaw, pitch):
    packet_id = 0x07
    player_name_padded = player_name.ljust(64, ' ')  # Pad player name to 64 bytes with spaces
    packet = struct.pack('Bb64shhhBB', packet_id, player_id, player_name_padded.encode('ascii'), x, y, z, yaw, pitch)
    client_socket.sendall(packet)

# Main function to handle client connections
def main():
    # Create TCP socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((SERVER_IP, SERVER_PORT))
    server_socket.listen(5)
    print("Server listening on {}:{}".format(SERVER_IP, SERVER_PORT))

    while True:
        # Accept incoming connections
        client_socket, address = server_socket.accept()
        print("Connection from {}".format(address))

        # Send server identification packet to the client
        send_server_identification(client_socket)
        send_level_initialize_packet(client_socket)
        send_level_data_chunk_packet(client_socket, chunk_length=0, percent_complete=0)
        send_level_finalize_packet(client_socket)
        send_spawn_player_packet(client_socket, player_id=0, player_name="Player1", x=0, y=0, z=0, yaw=0, pitch=0)

        try:
            while True:
                # Periodically send ping packet
                send_ping_packet(client_socket)
                time.sleep(10)  # Adjust the interval as needed
        except ConnectionResetError:
            print("Connection closed by client")
        finally:
            client_socket.close()

if __name__ == "__main__":
    main()

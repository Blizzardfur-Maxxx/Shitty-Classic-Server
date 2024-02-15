import socket
import time
import struct
import numpy as np

# Define constants
SERVER_IP = '127.0.0.1'
SERVER_PORT = 25565
PROTOCOL_VERSION = 0x07
SERVER_NAME = "MyServer"
SERVER_MOTD = "Welcome to MyServer!"
USER_TYPE_OP = 0x64

# Packet IDs
PACKET_ID_SERVER_IDENTIFICATION = 0x00
PACKET_ID_PING = 0x01
PACKET_ID_LEVEL_INITILAZE = 0x02
PACKET_ID_LEVEL_DATA_CHUNK = 0x03
PACKET_ID_LEVEL_FINALIZE = 0x04
PACKET_ID_SPAWN_PLAYER = 0x07
PACKET_ID_SET_POSITION_ORIENTATION = 0x08

# Function to send server identification packet
def send_server_identification(client_socket):
    packet = struct.pack('BB64s64sB', PACKET_ID_SERVER_IDENTIFICATION, PROTOCOL_VERSION, SERVER_NAME.encode('ascii'), SERVER_MOTD.encode('ascii'), USER_TYPE_OP)
    client_socket.sendall(packet)

# Function to send ping packet
def send_ping_packet(client_socket):
    packet = struct.pack('B', PACKET_ID_PING)
    client_socket.sendall(packet)

def send_level_initialize_packet(client_socket):
    packet = struct.pack('B', PACKET_ID_LEVEL_INITILAZE)
    client_socket.sendall(packet)

# Function to send level data chunk packet
def send_level_data_chunk(client_socket, chunk_data, percent_complete):
    padded_chunk_data = chunk_data.ljust(1024, b'\x00')  # Pad the chunk with zeros to make it 1024 bytes long
    packet = struct.pack('>Bh1024sB', PACKET_ID_LEVEL_DATA_CHUNK, len(padded_chunk_data), padded_chunk_data, percent_complete)
    client_socket.sendall(packet)

# Function to send level finalize packet
def send_level_finalize_packet(client_socket):
    x_size = 256
    y_size = 128
    z_size = 256
    packet = struct.pack('Bhhh', PACKET_ID_LEVEL_FINALIZE, x_size, y_size, z_size)
    client_socket.sendall(packet)

# Function to send spawn player packet
def send_spawn_player_packet(client_socket, player_id, player_name, x, y, z, yaw, pitch):
    player_name_padded = player_name.ljust(64, ' ')  # Pad player name to 64 bytes with spaces
    packet = struct.pack('Bb64shhhBB', PACKET_ID_SPAWN_PLAYER, player_id, player_name_padded.encode('ascii'), x, y, z, yaw, pitch)
    client_socket.sendall(packet)

# Function to send set position orientation packet
def send_set_position_orientation_packet(client_socket, player_id, x, y, z, yaw, pitch):
    packet = struct.pack('BbfffBB', PACKET_ID_SET_POSITION_ORIENTATION, player_id, x, y, z, yaw, pitch)
    client_socket.sendall(packet)

import gzip

def generate_empty_level():
    # Create an empty level of size 256x128x256 in XZY order
    level = np.zeros((256, 64, 256), dtype=np.uint8)
    # Convert the level to bytes
    level_bytes = level.tobytes()
    # Reshape the level bytes to be in XZY order
    level_xzy = np.frombuffer(level_bytes, dtype=np.uint8).reshape((256, 256, 64))
    # Compress the level data using gzip
    compressed_data = gzip.compress(level_xzy.tobytes())
    return compressed_data


def split_level_data(level_data):
    chunk_size = 1024
    chunks = [level_data[i:i+chunk_size].ljust(chunk_size, b'\x00') for i in range(0, len(level_data), chunk_size)]
    return chunks

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
        time.sleep(1)

        try:
            # Generate empty level
            level_data = generate_empty_level()

            # Split level data into chunks
            chunks = split_level_data(level_data)

            # Send level initialization packet
            send_level_initialize_packet(client_socket)

            # Send each chunk as a level data chunk packet
            total_chunks = len(chunks)
            for i, chunk in enumerate(chunks, start=1):
                percent_complete = i * 100 // total_chunks
                send_level_data_chunk(client_socket, chunk, percent_complete)
                time.sleep(0.1)  # Adjust the interval as needed

            # Send level finalize packet
            send_level_finalize_packet(client_socket)

            # Example: Send spawn player packet
            send_spawn_player_packet(client_socket, 1, "Player1", 255, 64, 255, 1, 1)
            send_set_position_orientation_packet(client_socket, player_id=0, x=0.0, y=0.0, z=0.0, yaw=90, pitch=0)

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

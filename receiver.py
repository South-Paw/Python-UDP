''' receiver.py
	Usage: python3 receiver.py <receiver_in> <receiver_out> <channel_receiver_in> <file_to_receive>
	Example: python3 receiver.py 5001 5002 5007 testOut.dat

	Authors: James Paterson & Alex Gabites
	Date: August 2015
'''

import socket
import time
import sys
import os

from customPacket import customPacket

UDP_IP = "127.0.0.1"

class receiver:
	def __init__(self):
		self.expected = 0
		self.packet_count = 0

		# Get required arguments
		self.grab_args()

		# Create and bind the ports
		self.try_bind()

		# Status report
		print("Receiver ONLINE")

		# Listen
		self.listen()

	def grab_args(self):
		# Checking port numbers
		for arg in sys.argv[1:4]:
			if not arg.isdigit():
				print("Incorrect arguments!")
				print("Try: 'python3 receiver.py receiver_in receiver_out channel_receiver_in file_to_receive'")
				exit(1)
			elif not(1024 < int(arg) < 64001):
				print("Invalid port number!")
				print("'{}' should be within the range of 1025 - 64000".format(arg))
				exit(1)

		self.receiver_in			= int(sys.argv[1])
		self.receiver_out			= int(sys.argv[2])
		self.channel_receiver_in 	= int(sys.argv[3])

		# Checking no collisions in port numbers
		if self.channel_receiver_in in [self.receiver_in, self.receiver_out] or self.receiver_in == self.receiver_out:
			print("receiver.py Error!")
			print("Port collision: check your ports.")
			exit(1)

		# Grab file name
		self.file_name = sys.argv[4]

		# Check it doesn't already exist
		if os.path.isfile(self.file_name):
			print("receiver.py Error!")
			print("That file already exists.")
			exit(1)

	def try_bind(self):
		# Try receiver_in socket
		try:
			# Create
			self.sock_in = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
			# Bind
			self.sock_in.bind((UDP_IP, self.receiver_in))
		except OSError:
			print("sender.py Error!")
			print("Port: {} is already in use.".format(self.receiver_in))
			print("Exiting...")
			exit(1)

		# Try receiver_out socket
		try:
			self.sock_out = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
			self.sock_out.bind((UDP_IP, self.receiver_out))
		except OSError:
			print("sender.py Error!")
			print("Port: {} is already in use.".format(self.receiver_out))
			print("Exiting...")
			exit(1)

		self.address = (UDP_IP, self.channel_receiver_in)

	def listen(self):
		self.f = open(self.file_name, "wb")

		self.file_part = bytes("", "utf-8")
		self.file_fully_received = False

		while not self.file_fully_received:
			self.data, self.source_address = self.sock_in.recvfrom(1024)

			self.received_packet = customPacket()

			self.header = self.data[:9].decode(encoding="utf-8")
			self.payload = self.data[9:]

			self.expanded_packet = self.received_packet.expandPacket(self.data, 0x479E)

			if not self.expanded_packet:
				if self.received_packet.packetType:
					if self.received_packet.seqno == self.expected:
						self.packet_count += 1

						print("Packet no. {} received.".format(self.packet_count))

						if self.received_packet.dataLen == 0:
							print("File fully received.")
							print("Exiting normally")
							self.file_fully_received = True
						else:
							self.file_part = self.file_part + self.received_packet.data

						self.expected = 1 - self.expected

					# Create an acknowledgement packet
					self.return_packet = customPacket(0x479E)
					self.return_packet.setData(bytes('', 'utf-8'))
					self.return_packet.setSeqno(self.received_packet.seqno)
					self.return_packet.setType("0")

					# Condense it
					self.condensed_packet = self.return_packet.condensePacket()

					# Send the reply
					self.sock_out.sendto(self.condensed_packet, self.address)
				else:
					print("receiver.py Error!")
					print("Bad packet type.")
			else:
				print("receiver.py Error!")
				print("Bad magic number or length: '{}' | '{}'".format([self.received_packet.dataLen, int(self.data[:4], 16) == 0x479e][self.expanded_packet - 1], self.expanded_packet))

		# We're done, clean up
		self.sock_out.close()
		self.sock_in.close()

		# Close file
		self.f.write(self.file_part)
		self.f.close()

# Run!
if __name__ == "__main__":
	receiver()

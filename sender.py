''' sender.py
	Usage: python3 sender.py <sender_in> <sender_out> <channel_sender_in> <file_to_send>
	Example: python3 sender.py 5004 5003 5006 file.dat

	Authors: James Paterson & Alex Gabites
	Date: August 2015
'''

import socket
import select
import time
import sys
import os.path

from customPacket import customPacket

UDP_IP = "127.0.0.1"

class sender:
	def __init__(self):
		self.packets_sent_count = 0
		self.packets_needed_count = 0

		self.message_recieved = False
		self.message_fully_sent = False
		self.n_ext = 0
		self.exit_flag = False

		# Get required arguments
		self.grab_args()

		# Create and bind the ports
		self.try_bind()

		# Status report
		print("Sender ONLINE")
		#print("Target IP:", UDP_IP)
		#print("Target port:", self.channel_sender_in)
		#print("File to be sent:", self.file_name)

		# Send the file
		self.start_sending()

	def grab_args(self):
		# Checking port numbers
		for arg in sys.argv[1:4]:
			if not arg.isdigit():
				print("Incorrect arguments!")
				print("Try: 'python3 sender.py sender_in sender_out channel_sender_in file_to_send'")
				exit(1)
			elif not(1024 < int(arg) < 64001):
				print("Invalid port number!")
				print("'{}' should be within the range of 1025 - 64000".format(arg))
				exit(1)

		self.sender_in 			= int(sys.argv[1])
		self.sender_out 		= int(sys.argv[2])
		self.channel_sender_in 	= int(sys.argv[3])

		# Checking no collisions in port numbers
		if self.channel_sender_in in [] or self.sender_in == self.sender_out:
			print("sender.py Error!")
			print("Port collision: check your ports.")
			exit(1)

		# Grab file name
		self.file_name = sys.argv[4]

		# Check file exists
		if not os.path.isfile(self.file_name):
			print("sender.py Error!")
			print("That file does not exist.")
			exit(1)

		# Open and read file
		self.f = open(self.file_name, 'rb', encoding = None)
		self.file_contents = self.f.read()

	def try_bind(self):
		# Try sender_in socket
		try:
			# Create
			self.sock_in = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
			# Bind
			self.sock_in.bind((UDP_IP, self.sender_in))
			# ID
			self.sock_in_id = self.sock_in.fileno()
		except OSError:
			print("sender.py Error!")
			print("Port: {} is already in use.".format(self.sender_in))
			print("Exiting...")
			exit(1)

		# Try sender_out socket
		try:
			# Create
			self.sock_out = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
			# Bind
			self.sock_out.bind((UDP_IP, self.sender_out))
			# ID
			self.sock_out_id = self.sock_out.fileno()
		except OSError:
			print("sender.py Error!")
			print("Port: {} is already in use.".format(self.sender_out))
			print("Exiting...")
			exit(1)

	def get_next_data(self, bin_str, start, max_chars):
		end = min(start + max_chars, len(bin_str))
		grabbed_data = bin_str[start:end]

		#print("Data is of type: " + type(grabbedDat))
		return grabbed_data

	def start_sending(self):
		print("Begining sending process...")
		print("{} bytes of data to send.".format(len(self.file_contents)))

		self.selection = select
		self.p_start = 0

		self.max_packets = (len(self.file_contents) + 511) // 512 + 1

		while not self.message_fully_sent:
			self.p_end = min(len(self.file_contents) - self.p_start, 512)

			if self.p_start == len(self.file_contents):
				# EOF
				self.packet = customPacket(0x479E)

				self.packet.setSeqno(self.n_ext)
				self.packet.setType(1)
				self.packet.setData(bytes("", "utf-8"))

				self.message_fully_sent = True
			else:
				# Next packet
				self.new_data = self.get_next_data(self.file_contents, self.p_start, 512)

				self.packet = customPacket(0x479E)

				self.packet.setSeqno(self.n_ext)
				self.packet.setType(1)
				self.packet.setData(self.new_data)

			# Increment number of packets required
			self.packets_needed_count += 1

			self.message = self.packet.condensePacket()

			self.message_recieved = False

			while not self.message_recieved:
				(self.s_read, self.s_write, self.s_except) = self.selection.select([], [self.sock_out_id], [])
				if self.sock_out_id in self.s_write:
					self.packets_sent_count += 1
					self.sock_out.sendto(self.message, (UDP_IP, self.channel_sender_in))
				else:
					print("Write socket was not avaliable.")

				(self.s_read, self.s_write, self.s_except) = self.selection.select([self.sock_in_id], [], [], 1)
				if self.sock_in_id in self.s_read:
					self.data, self.address = self.sock_in.recvfrom(1024)

					self.received_packet = customPacket()

					self.magic_no_correct = not self.received_packet.expandPacket(self.data, 0x479E)
					self.recived_type = self.received_packet.packetType == 0
					self.packet_length = self.received_packet.dataLen == 0
					self.sequence_number = self.received_packet.seqno == self.n_ext

					if self.magic_no_correct and self.recived_type and self.packet_length and self.sequence_number:
						print("Great success! {}/{} packets sent | Progress: {:0.2f}% | Total sent: {}".format(self.packets_needed_count, self.max_packets, (100 * (self.packets_needed_count / self.max_packets)), self.packets_sent_count))
						self.n_ext = 1 - self.n_ext
						self.message_recieved = True
						self.p_start = self.p_start + self.p_end
					else:
						print("sender.py Error!")
						print("Packet state: {} {} {}".format(self.magic_no_correct, self.recived_type, self.sequence_number))
				else:
					print("Nothing received...")

		self.f.close()
		self.sock_in.close()
		self.sock_out.close()

		# Status report/summary
		print("sender.py Report:")
		print("	Sent {} of a required {} packets.".format(self.packets_sent_count, self.max_packets))
		print("	Packet excess of {:0.2f}%".format(100 * (self.packets_sent_count / self.packets_needed_count - 1)))
		print("	{} packets went missing.".format(self.packets_sent_count - self.max_packets))

		print("Exiting normally.")


# Run!
if __name__ == "__main__":
	sender()

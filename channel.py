''' channel.py
	Usage: python3 channel.py <channel_sender_in> <channel_sender_out> <channel_receiver_in> <channel_receiver_out> <sender_in> <receiver_out> <drop_rate> <hash>
	Example: python3 channel.py 5006 5005 5007 5008 5004 5001 0.01 somehash

	Authors: James Paterson & Alex Gabites
	Date: August 2015
'''

import socket
import select
import random
import sys

UDP_IP = "127.0.0.1"

class channel:
	def __init__(self):
		# Random number
		self.random_num_gen = random

		# Get required arguments
		self.grab_args()

		# Create and bind the ports
		self.try_bind()

		# Status report
		print("Channel ONLINE")

		# Stay alive
		self.channel_alive()

	def grab_args(self):
		# Checking port numbers
		for arg in sys.argv[1:7]:
			if not arg.isdigit():
				print("Incorrect arguments!")
				print("Try: 'python3 channel.py channel_sender_in channel_sender_out channel_receiver_in channel_receiver_out sender_in receiver_in drop_rate hash'")
				exit(1)
			elif not(1024 < int(arg) < 64001):
				print("Invalid port number!")
				print("'{}' should be within the range of 1025 - 64000".format(arg))
				exit(1)

		self.channel_sender_in		= int(sys.argv[1])
		self.channel_sender_out		= int(sys.argv[2])
		self.channel_receiver_in	= int(sys.argv[3])
		self.channel_receiver_out	= int(sys.argv[4])
		self.sender_in				= int(sys.argv[5])
		self.receiver_in			= int(sys.argv[6])

		# Check drop rate is within range
		try:
			self.drop_rate = float(sys.argv[7])
			if not 0 <= self.drop_rate < 1:
				raise ValueError("Drop rate value out of bounds!")
		except:
			print("Drop rate must be a value in the range 0 - 1")
			exit(1)

		# Check theres no port conflicts
		self.port_list = [self.channel_sender_in, self.channel_sender_out, self.channel_receiver_in, self.channel_receiver_out, self.sender_in, self.receiver_in]

		for i in range(5):
			if self.port_list[i] in self.port_list[i+1:]:
				print("channel.py Error!")
				print("Port collision: {} is used twice.".format(self.port_list[i]))
				exit(1)

		# Create our pseudo random number using the hash given
		if len(sys.argv) > 7:
			self.random_seed = "".join(sys.argv[7:])
			self.random_num_gen.seed(self.random_seed)

	def try_bind(self):
		# Try channel_sender_in socket
		try:
			self.sock_sender_in = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
			self.sock_sender_in.bind((UDP_IP, self.channel_sender_in))
			self.sock_sender_in_id = self.sock_sender_in.fileno()
		except OSError:
			print("channel.py Error!")
			print("Port: {} is already in use.".format(self.channel_sender_in))
			print("Exiting...")
			exit(1)

		# Try channel_sender_out socket
		try:
			self.sock_sender_out = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
			self.sock_sender_out.bind((UDP_IP, self.channel_sender_out))
			self.sock_sender_out_id = self.sock_sender_out.fileno()
		except OSError:
			print("channel.py Error!")
			print("Port: {} is already in use.".format(self.channel_sender_out))
			print("Exiting...")
			exit(1)

		# Try channel_receiver_in socket
		try:
			self.sock_receiver_in = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
			self.sock_receiver_in.bind((UDP_IP, self.channel_receiver_in))
			self.sock_receiver_in_id = self.sock_receiver_in.fileno()
		except OSError:
			print("channel.py Error!")
			print("Port: {} is already in use.".format(self.channel_receiver_in))
			print("Exiting...")
			exit(1)

		# Try channel_receiver_out socket
		try:
			self.sock_receiver_out = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
			self.sock_receiver_out.bind((UDP_IP, self.channel_receiver_out))
			self.sock_receiver_out_id = self.sock_receiver_out.fileno()
		except OSError:
			print("channel.py Error!")
			print("Port: {} is already in use.".format(self.channel_receiver_out))
			print("Exiting...")
			exit(1)

	def channel_alive(self):
		self.to_sender = (UDP_IP, self.sender_in)
		self.to_receiver = (UDP_IP, self.receiver_in)

		self.selection = select

		while True:
			(self.s_read, self.s_write, self.s_except) = self.selection.select([self.sock_sender_in_id, self.sock_receiver_in_id], [], [])

			(self.s_read1, self.s_write, self.s_except1) = self.selection.select([], [self.sock_sender_out_id, self.sock_receiver_out_id], [], 0)

			for fd in self.s_read:
				if (fd == self.sock_sender_in_id):
					self.data, self.source_address = self.sock_sender_in.recvfrom(1024)

					if (self.random_num_gen.random() > self.drop_rate and self.sock_receiver_out_id in self.s_write):
						self.sock_receiver_out.sendto(self.data, self.to_receiver)

						# Operations debug
						print("Message received from {}:{}".format(self.source_address[0], self.source_address[1]))
						print("Passed on to {}:{}\n".format(self.to_receiver[0], self.to_receiver[1]))
					else:
						print("Dropped packet from: {}\n".format(self.source_address))

				if (fd == self.sock_receiver_in_id and self.sock_sender_out_id in self.s_write):
					self.data, self.source_address = self.sock_receiver_in.recvfrom(1024)

					if (self.random_num_gen.random() > self.drop_rate):
						self.sock_sender_out.sendto(self.data,self.to_sender)

						# Operations debug
						print("Message received from {}:{}".format(self.source_address[0], self.source_address[1]))
						print("Passed on to {}:{}\n".format(self.to_sender[0], self.to_sender[1]))
					else:
						print("Dropped packet from: {}\n".format(self.source_address))

# Run!
if __name__ == "__main__":
	channel()

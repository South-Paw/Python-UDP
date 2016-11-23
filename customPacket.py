''' customPacket.py

	Authors: James Paterson & Alex Gabites
	Date: August 2015
'''

class customPacket:
	def __init__(self, magicNo = "notSet"):
		self.magicno 	= magicNo
		self.packetType = "notSet"
		self.seqno 		= "notSet"
		self.dataLen 	= "notSet"
		self.data 		= ""
		
	def getMagicNo(self):
		return hex(self.magicno)
		
	def setData(self, inputStr):
		if len(inputStr) > 512:
			return 1
		self.data = inputStr
		self.dataLen = len(self.data)
		return 0
		
	def setType(self, newType):
		if self.packetType != "notSet":
			return 1
		self.packetType = newType
		return 0
		
	def setSeqno(self, newSeq):
		if self.seqno != "notSet":
			return 1
		self.seqno = newSeq
		return 0
		
	def condensePacket(self):
		condensedStr = ""
		if "notSet" in [self.magicno, self.packetType, self.seqno, self.dataLen, self.data]:
			print(self.magicno, self.packetType, self.seqno, self.dataLen)
			raise Exception
			return 1
		condensedStr = condensedStr + str(hex(self.magicno)[2:])
		condensedStr = condensedStr + str(self.packetType)
		condensedStr = condensedStr + str(self.seqno)
		condensedStr = condensedStr + str(self.dataLen).zfill(3)
		condensedStr = bytes(condensedStr, "utf-8") + self.data
		return condensedStr
		
	def expandPacket(self, condStr, checkNo):
		header = condStr[:9].decode(encoding = "utf-8")
		payload = condStr[9:]
		self.magicno = int(header[:4], 16)
		
		if self.magicno != checkNo:
			return 2
		
		self.packetType = int(header[4])
		self.seqno = int(header[5])
		self.dataLen = int(header[6:9])
		self.data = payload
		
		if len(payload) > (self.dataLen):
			print("customPacket.py Error!")
			print("Debug: {} {}".format(len(payload), self.dataLen))
			return 1
		return 0
	
if __name__ == "__main__":
	# For solo testing customPacket
	lol = customPacket(0x479E)
	lol.setData(bytes("Hello", "utf-8"))
	lol.setSeqno(1)
	lol.setType(1)
	
	herewego = lol.condensePacket()
	
	herp = customPacket()
	print(herp.expandPacket(herewego,0x479E))
	print(herp.data)
	print(herp.packetType)
	print(herp.seqno)
	print(herp.getMagicNo())

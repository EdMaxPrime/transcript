import sys
import re

def main():
	helpText = """
	Usage: srt_maker.py -help OR <in-file> <out-file>
	Will convert the input file to SRT format and write it to the output file"""

	moreHelp = """
	===Sample subtitle===
	index               1
	start and end time  00:00:00,000 --> 00:00:10,000
	subtitle text       Text here (multiple lines allowed)
	empty line
	===Special formatting===
	<SCRIPT>
	[start time] --> [end time of first subtitle]
	multiline text ending in a line that contains only
	</SCRIPT>
	===Other directives===
	@OFFSET <time in milliseconds>
		will push all following subtitles later by the given time. Use 0 to stop the offset.
	@DELAY <time in milliseconds>
		will increase or decrease the time offset by the specified time.
	@SPEED <time in milliseconds>
		will change how long each letter increments the duration of the next subtitle. Default 50. Resets for each subtitle.
	"""
	if len(sys.argv) != 3:
		print helpText
	elif sys.argv[1] == "-help":
		print helpText + "\n" + moreHelp
	else:
		f = open(sys.argv[1], "r")
		converted = convert(f.read())
		f.close()
		f = open(sys.argv[2], "w")
		f.write(converted)
		f.close()

def convert(input):
	directiveOffset = re.compile("@OFFSET [+-]?\\d{1,9}")
	directiveDelay = re.compile("@DELAY [+-]?\\d{1,9}")
	directiveSpeed = re.compile("@SPEED \\d{1,6}")
	lines = input.splitlines()
	state = "heading"
	timeMultiplier = 50
	timeAdd = 0
	subs = [Subtitle()]
	unknownEndTime = False
	script = False
	for l in lines:
		if state == "heading":
			unknownEndTime = False
			if l.find("<SCRIPT>") == 0: #this is the start of a script section
				n = subs[-1].next()
				subs.append(n)
				state = "time"
				timeMultiplier = 50
				script = True
			elif directiveDelay.match(l): #this line is a delay directive
				timeAdd = int(l[7:])
			elif directiveSpeed.match(l): #this line is a speed directive
				timeMultiplier = int(l[7:])
			elif isInt(l): #this is already an SRT style timed text
				n = subs[-1].next()
				subs.append(n)
				state = "time"
				timeMultiplier = 50
				script = False
		elif state == "time":
			times = l.split(" --> ")
			if isTime(times[0]):
				subs[-1].start = parseTime(times[0])
			if isTime(times[1]):
				subs[-1].end = parseTime(times[1])
				unknownEndTime = False
			else:
				subs[-1].end = subs[-1].start.copy() #makes this a 0 length subtitle
				unknownEndTime = True
			subs[-1].incrementStart(timeAdd)
			subs[-1].incrementEnd(timeAdd)
			state = "text"
		elif state == "text":
			if l == '</SCRIPT>' and script:
				script = False
				timeAdd = 0
				state = "heading"
			elif l != "":
				if directiveDelay.match(l): #this line is a delay command
					timeAdd = int(l[7:])
				elif directiveSpeed.match(l): #this line is a speed command
					timeMultiplier = int(l[7:])
				else: #this line is actual subtitle text
					if script and ": " in l: #get rid of speaker's name
						l = l.split(": ", 2)[-1]
					if len(subs[-1].text) != 0: #add newline if necessary
						subs[-1].text += "\n"
					subs[-1].text += l #add text to subtitle
					if unknownEndTime:
						subs[-1].incrementEnd(len(l) * timeMultiplier)
						timeMultiplier = 50
					if script:
						timeMultiplier = 50
						unknownEndTime = True
						subs[-1].incrementStart(timeAdd)
						subs[-1].incrementEnd(timeAdd)
						subs.append(subs[-1].next())
			else:
				state = "heading"
	return "\n".join([x.toString() for x in subs[1:]])


def isInt(thing):
	try:
		i = int(thing)
		return True
	except:
		return False

def isTime(thing):
	try:
		parseTime(thing)
		return True
	except:
		return False

def parseTime(s):
	array4 = [int(s[0:2]), int(s[3:5]), int(s[6:8]), int(s[9:12])]
	return Time(array4[0], array4[1], array4[2], array4[3])


class Time:
	h = 0
	m = 0
	s = 0
	l = 0
	def __init__(self, hours=0, minutes=0, seconds=0, millis=0):
		self.h = hours
		self.m = minutes
		self.s = seconds
		self.l = millis

	def addTime(self, millis):
		total = self.l + self.s * 1000 + self.m * 1000 * 60 + self.h * 1000 * 60 * 60
		total += millis
		self.l = total % 1000
		total /= 1000
		self.s = total % 60
		total /= 60
		self.m = total % 60
		total /= 60
		self.h = total % 100

	def copy(self):
		return Time(self.h, self.m, self.s, self.l)

	def toString(self):
		return "{:0>2}:{:0>2}:{:0>2},{:0>3}".format(self.h, self.m, self.s, self.l)

#Actual Code of this Script
class Subtitle:
	index = 1
	start = Time()
	end = Time()
	text = ""

	def __init__(self, i=1, s=Time(), e=Time(), t=""):
		self.index = i
		self.start = s
		self.end   = e
		self.text  = t

	def incrementStart(self, millis):
		self.start.addTime(millis)

	def incrementEnd(self, millis):
		self.end.addTime(millis)

	def getStart(self):
		return self.start.toString()

	def getEnd(self):
		return self.end.toString()

	def next(self):
		n = Subtitle(i=(self.index + 1), s=self.end.copy(), e=self.end.copy())
		n.incrementEnd(100)
		return n

	def toString(self):
		return str(self.index) + "\n" + self.getStart() + " --> " + self.getEnd() + "\n" + self.text + "\n"

main()
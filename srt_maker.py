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
	defaultTimeMultiplier = 50
	timeMultiplier = defaultTimeMultiplier
	timeOffset = 0
	delayNext  = 0
	subs = [Subtitle()]
	unknownEndTime = False
	script = False
	keepNames = False
	for l in lines:
		if directiveOffset.match(l):
			timeOffset = int(l[8:])
		elif directiveDelay.match(l):
			if script:
				delayNext = int(l[7:])
			else:
				timeOffset += int(l[7:])
		elif directiveSpeed.match(l):
			timeMultiplier = int(l[7:])
		elif state == "heading":
			unknownEndTime = False
			if l.find("<SCRIPT>") == 0: #this is the start of a script section
				n = subs[-1].next()
				subs.append(n)
				state = "time"
				timeMultiplier = defaultTimeMultiplier
				script = True
				keepNames = False
			elif l.find("<SCRIPT names>") == 0: #also a script section, but keep the names preceding text
				n = subs[-1].next()
				subs.append(n)
				state = "time"
				timeMultiplier = defaultTimeMultiplier
				script = True
				keepNames = True
			elif isInt(l): #this is already an SRT style timed text
				n = subs[-1].next()
				subs.append(n)
				state = "time"
				timeMultiplier = defaultTimeMultiplier
				script = False
		elif state == "time":
			valid = "-->" in l #true if this contains the arrow, false otherwise so it can't have two times in it
			times = l.replace(" ", "").split("-->")
			if valid and isTime(times[0]):
				subs[-1].start = parseTime(times[0])
			if valid and isTime(times[1]):
				subs[-1].end = parseTime(times[1])
				unknownEndTime = False
			else:
				subs[-1].setDuration(0) #makes this a 0 length subtitle
				unknownEndTime = True
			subs[-1].adjustTime(timeOffset) #account for time offset
			state = "script" if script else "text"
		elif state == "script":
			if l == '</SCRIPT>':
				script = False
				state = "heading"
			else:
				if not keepNames:
					l = l.split(": ", 2)[-1]
				subs[-1].text += l #add text to subtitle
				if unknownEndTime:
					subs[-1].setDuration(len(l) * timeMultiplier)
				timeMultiplier = defaultTimeMultiplier
				unknownEndTime = True
				subs[-1].adjustTime(delayNext)
				subs.append(subs[-1].next())
				delayNext = 0
		elif state == "text":
			if l != "":
				if len(subs[-1].text) != 0: #add newline if necessary
					subs[-1].text += "\n"
				subs[-1].text += l #add text to subtitle
				if unknownEndTime:
					subs[-1].adjustEnd(len(l) * timeMultiplier)
					timeMultiplier = defaultTimeMultiplier
			else:
				state = "heading"
	return "\n".join([x.toString() for x in subs[1:]])


def isInt(thing):
	try:
		i = int(thing)
		return True
	except:
		return False

#Returns true if the string is a time like HH:MM:SS,LLL where L is a millisecond
def isTime(thing):
	return re.match("\\d\\d:\\d\\d:\\d\\d,\\d{3}", thing)

#Returns a Time object given a string where isTime(string) = True
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
		total = self.toMillis()
		total += millis
		self.l = total % 1000
		total /= 1000
		self.s = total % 60
		total /= 60
		self.m = total % 60
		total /= 60
		self.h = total % 100

	def toMillis(self):
		return self.l + self.s * 1000 + self.m * 1000 * 60 + self.h * 1000 * 60 * 60

	def difference(self, otherTime):
		return otherTime.toMillis() - self.toMillis()

	def copy(self):
		return Time(self.h, self.m, self.s, self.l)

	def toString(self):
		return "{:0>2}:{:0>2}:{:0>2},{:0>3}".format(self.h, self.m, self.s, self.l)

#Each subtitle object holds one subtitle, which can then be turned into SRT format
class Subtitle:
	index = 1
	start = Time()
	end = Time()
	text = ""

	# @param i  the index of this subtitle in the entire transcript
	# @param s  the time that this subtitle appears on screen
	# @param e  the time that this subtitle ends
	# @param t  the actual text of this subtitle, can contain newlines
	def __init__(self, i=1, s=Time(), e=Time(), t=""):
		self.index = i
		self.start = s
		self.end   = e
		self.text  = t

	def adjustStart(self, millis):
		self.start.addTime(millis)

	def adjustEnd(self, millis):
		self.end.addTime(millis)

	#Gives an offset to this subtitle
	def adjustTime(self, millis):
		self.adjustStart(millis)
		self.adjustEnd(millis)

	#Adjusts the end time of this subtitle to be <millis> milliseconds after the start time
	def setDuration(self, millis):
		self.adjustEnd(millis - self.getDuration())

	def getDuration(self):
		return self.start.difference(self.end)

	def getStart(self):
		return self.start.toString()

	def getEnd(self):
		return self.end.toString()

	#Returns a template for the next subtitle in the series. Index is increased by one, duration is 100 milliseconds, and it starts right when this one ended.
	def next(self):
		n = Subtitle(i=(self.index + 1), s=self.end.copy(), e=self.end.copy())
		n.adjustEnd(100)
		return n

	def toString(self):
		return str(self.index) + "\n" + self.getStart() + " --> " + self.getEnd() + "\n" + self.text + "\n"

main()
import sys
import os
from os import path, mkdir, listdir, rmdir
from getpass import getpass as inputHidden
import math
import unicodedata
import re

##############
# USER INPUT #
##############

"""
	Asks the user a question and returns the number of the response. If an invalid answer is given, the question is repeated.

	Parameters
	----------
	question : str
		The question that is asked.
	choices : list (str)
		An array of the different possible answers.
	allowMultiple : bool
		If True, the user may give multiple answers, each separated by a space. An array of these answers is returned.
	validChoicesWarning : bool
		If True, a warning will be printed if there are one or fewer valid answers.

	Returns
	-------
	If allowMultiple is True:
	int
		The chosen answer.
	Else:
	list (int)
		An array of ints representing chosen answers.
"""
def makeChoice(question, options, allowMultiple=False, validChoicesWarning=True):
	numChoices = len(options)
	if numChoices == 0:
		if validChoicesWarning:
			print("Warning: A question was asked with no valid answers. Returning None.")
		return None
	if numChoices == 1:
		if validChoicesWarning:
			print("A question was asked with only one valid answer. Returning this answer.")
		return 1
	print("\n"+question)
	for i in range(numChoices):
		print(str(i+1)+": "+options[i])
	cInput = input("\n").split(" ")
	if not allowMultiple:
		try:
			assert len(cInput) == 1
			choice = int(cInput[0])
			assert choice > 0 and choice <= numChoices
			return choice
		except:
			print("\nInvalid input.")
			return makeChoice(question, options, allowMultiple)
	else:
		try:
			choices = [int(c) for c in cInput]
			for choice in choices:
				assert choice > 0 and choice <= numChoices
			return choices
		except:
			print("\nInvalid input.")
			return makeChoice(question, options, allowMultiple)

"""
	Asks the user a question. The answer can be any number between the given minVal and maxVal. If an invalid answer is given, the question is repeated.

	Parameters
	----------
	question : str
		The question that is asked.
	minVal : float
		The minimum allowed value.
	maxVal : float
		The maximum allowed value.

	Returns
	-------
	float
		The given value.
"""
def makeChoiceNumInput(question, minVal, maxVal):
	while True:
		print("\n"+question)
		try:
			var = float(input())
			assert minVal <= var <= maxVal
			return var
		except:
			print("Invalid input.")

###########
# SEEDING #
###########

"""
	Encodes an array of variable values into a seed according to a given max value array.

	Parameters
	----------
	varArray : list (int)
		The array of values
	maxValueArray:
		An array of the (number of possible values - 1) of each variable. For example, if you have three variables with the possible values...
		var1 : [0, 1, 2, 3]
		var2 : [0, 1]
		var3 : [0, 1, 2, 3, 4]
		... then the maxValueArray should be [4, 2, 5].
		Note that the maxValueArray's implementation assumes that possible values start at 0 and each increment by 1. For example, if a variable is stated to have 4 possible values, it asusmes those values are [0, 1, 2, 3].
	base : int
		Between 2 and 36. The numerical base used by the seed (in other words, how many values are possible for each character, such as 0-9 and a-z).

	Returns
	-------
	int
		The seed in base-10 numerical form.
	str
		The seed in the given base.
"""
def encodeSeed(varArray, maxValueArray, base=10):
	if base > 36:
		print("Base must be between 2 and 36. Lowering to 36.")
		base = 36
	seed = 0
	baseShift = 0
	for i in range(len(varArray)):
		seed += varArray[i]<<baseShift
		baseShift += maxValueArray[i].bit_length()
	return seed, dec_to_base(seed, base)

"""
	Decodes a string or non-base-10 number into an array of variable values according to a given max value array.

	Parameters
	----------
	seed : str or int
		The seed that will be decoded.
	maxValueArray:
		An array of the (number of possible values - 1) of each variable. For example, if you have three variables with the possible values...
		var1 : [0, 1, 2, 3]
		var2 : [0, 1]
		var3 : [0, 1, 2, 3, 4]
		... then the maxValueArray should be [4, 2, 5].
		Note that the maxValueArray's implementation assumes that possible values start at 0 and each increment by 1. For example, if a variable is stated to have 4 possible values, it asusmes those values are [0, 1, 2, 3].
	base : int
		Unused if seed is an int (base-10 is assumed). Between 2 and 36. The numerical base used by the seed (in other words, how many values are possible for each character, such as 0-9 and a-z).

	Returns
	-------
	list (int)
		An array of variable values decoded from the string. For example, if there are 3 variables, the returned array is [var1's value, var2's value, var3's value]
"""
def decodeSeed(seed, maxValueArray, base=10):
	if type(seed) is str:
		if base > 36:
			print("Base must be between 2 and 36. Lowering to 36.")
			base = 36
		elif base < 2:
			print("Base must be between 2 and 36. Increasing to 2.")
			base = 2
		seed = int(seed, base)
	baseShift = 0
	varArray = []
	for i in range(len(maxValueArray)):
		bitLength = maxValueArray[i].bit_length()
		varArray.append((seed>>baseShift) & ((2**bitLength)-1))
		baseShift += bitLength
	return varArray

"""
	Returns whether or not a seed is possible given a maxValueArray and base.

	Parameters
	----------
	seed : str or int
		The seed that will be verified.
	maxValueArray:
		An array of the (number of possible values - 1) of each variable. For example, if you have three variables with the possible values...
		var1 : [0, 1, 2, 3]
		var2 : [0, 1]
		var3 : [0, 1, 2, 3, 4]
		... then the maxValueArray should be [4, 2, 5].
		Note that the maxValueArray's implementation assumes that possible values start at 0 and each increment by 1. For example, if a variable is stated to have 4 possible values, it asusmes those values are [0, 1, 2, 3].
	base : int
		Between 2 and 36. The numerical base used by the seed (in other words, how many values are possible for each character, such as 0-9 and a-z).

	Returns
	-------
	bool
		Whether or not the seed is valid.
	list (int)
		An array of variable values decoded from the string. For example, if there are 3 variables, the returned array is [var1's value, var2's value, var3's value]
"""
def verifySeed(seed, maxValueArray, base=10):
	if base > 36:
		print("Base must be between 2 and 36. Lowering to 36.")
		base = 36
	elif base < 2:
		print("Base must be between 2 and 36. Increasing to 2.")
		base = 2
	if type(seed) is int:
		base = 10
		seed = dec_to_base(seed,base)
	seed = seed.upper().strip()

	try:
		maxSeed = 0
		baseShift = 0
		for i in range(len(maxValueArray)):
			maxSeed += maxValueArray[i]<<baseShift
			baseShift += maxValueArray[i].bit_length()
		assert int(seed, 36) <= maxSeed
		varsInSeed = decodeSeed(seed, maxValueArray, base)
		for i in range(len(varsInSeed)):
			assert 0 <= varsInSeed[i] <= maxValueArray[i]
		return True, varsInSeed
	except:
		return False, None

"""
	From https://www.codespeedy.com/inter-convert-decimal-and-any-base-using-python/

	Converts a base-10 int into a different base.

	Parameters
	----------
	num : int
		The number that will be converted.
	base : int
		Between 2 and 36. The numerical base used by the seed (in other words, how many values are possible for each character, such as 0-9 and a-z).

	Returns
	-------
	str
		The number in the given base.
"""
def dec_to_base(num,base):  #Maximum base - 36
	base_num = ""
	while num>0:
		dig = int(num%base)
		if dig<10:
			base_num += str(dig)
		else:
			base_num += chr(ord('A')+dig-10)  #Using uppercase letters
		num //= base
	base_num = base_num[::-1]  #To reverse the string
	return base_num

########################
# FILE/PATH MANAGEMENT #
########################

"""
	Writes a value to a file at a given address. Supports multi-byte addresses.

	Parameters
	----------
	file : str
		The file that will be modified.
	address : int
		The value (ideally, a hex value such as 0x12345) that will be modified.
	val : int
		The value that will be written to this address.
	numBytes : int
		The number of bytes that this value will take up.
	isLittleEndian : bool
		If True, bytes are written in reverse order.

	Returns
	-------
	False if the value is too large to be written within the given number of bytes; True otherwise.

	Examples
	--------
	Example 1
		writeToAddress(file.exe, 0x12345, 0x41, 1, False) will write the following value:
		0x12345 = 41
	Example 2
		writeToAddress(file.exe, 0x12345, 0x6D18, 2, False) will write the following values:
		0x12345 = 6D
		0x12346 = 18
	Example 3
		writeToAddress(file.exe, 0x12345, 0x1C, 2, False) will write the following values:
		0x12345 = 00
		0x12346 = 1C
	Example 4
		writeToAddress(file.exe, 0x12345, 0x003119, 3, True) will write the following values:
		0x12345 = 19
		0x12346 = 31
		0x12347 = 00
"""
def writeToAddress(file, address, val, numBytes=1, isLittleEndian=False):
	if val.bit_length() > numBytes*8:
		print("Given value is greater than "+str(numBytes)+" bytes.")
		return False
	if not isLittleEndian:
		address += (numBytes-1)
		increment = -1
	else:
		increment = 1
	for i in range(numBytes):
		file.seek(address)
		currByte = val & 0xFF
		file.write(bytes([currByte]))
		address += increment
		val = val>>8
	return True

"""
	Swaps the endianness (byte order) of a number.

	Parameters
	----------
	num : int
		The number whose order will be swapped.
	numBytes : int
		The number of bytes that this number takes up.

	Returns
	-------
	The modified number with swapped endianness.

	Example
	-------
	swapEndianness(0x012345) will return: 0x452301
"""
def swapEndianness(num, numBytes):
	num2 = 0
	for i in range(1, numBytes + 1):
	    num2 += (num>>(8*(i-1)) & 0xFF)*(256**(numBytes - i))
	return num2

"""
	From https://gist.github.com/jacobtomlinson/9031697

	Removes all empty folders, including nested empty folders, in a directory.

	Parameters
	----------
	p : str
		The path of the starting directory; all empty folders that are children (or grandchildren, etc) of this directory are removed.
"""
def removeEmptyFolders(p):
	if not path.isdir(p):
		return
	files = listdir(p)
	if len(files):
		for f in files:
			fullpath = path.join(p, f)
			if path.isdir(fullpath):
				removeEmptyFolders(fullpath)
	files = listdir(p)
	if len(files) == 0:
		rmdir(p)

"""
	Returns an array of the individual components of a given path.

	Parameters
	----------
	p : str
		The path.

	Returns
	-------
	list (str)
		The path array.

	Example
	-------
	Input
		"C:/early folder/test2/thing.exe"
	Output
		["C:", "early folder", "test2", "thing.exe"]
"""
def getPathArray(p):
	p1, p2 = path.split(p)
	if p2 == "":
		p = p1
	pathArray = []
	while True:
		p1, p2 = path.split(p)
		pathArray = [p2] + pathArray
		if p2 == "":
			pathArray = [p1] + pathArray
			try:
				while pathArray[0] == "":
					del pathArray[0]
			except:
				pass
			return pathArray
		p = p1

"""
	Creates the given directory. Unlike mkdir, this will also create any necessary parent directories that do not already exist.

	Parameters
	----------
	p : str
		The path of the folder that will be created.

	Returns
	-------
	True if the folder was created, False if it already exists.
"""
def createDir(p):
	if path.isdir(p):
		return False
	pathArray = getPathArray(p)
	currPath = pathArray[0]
	for i in range(1, len(pathArray)):
		currPath = path.join(currPath, pathArray[i])
		if not path.isdir(currPath):
			mkdir(currPath)
	return True

"""
	Returns the directory containing the current program, regardless of whether it is a standalone script or a wrapped executable.

	Returns
	-------
	str
		The directory containing the current program.
"""
def getCurrFolder():
	if getattr(sys, 'frozen', False):
		mainFolder = path.dirname(sys.executable) # EXE (executable) file
	else:
		mainFolder = path.dirname(path.realpath(__file__)) # PY (source) file
	sys.path.append(mainFolder)
	return mainFolder

"""
	Returns the file extension (including the ".") of the first file found in the given folder that matches the given file name.

	Parameters
	----------
	folder : str
		The given folder.
	fileName : str
		The given file name.

	Returns
	-------
	str
		The file extension (including the ".") of the first file found in folder named fileName (with any extension); if no file with that name is found, return an empty string.
"""
def getFileExt(folder, fileName):
	for f in listdir(folder):
		fName, fExt = path.splitext(f)
		if fName == fileName:
			return fExt
	return ""

"""
	From https://stackoverflow.com/questions/1392413/calculating-a-directorys-size-using-python

	Returns the total number of bytes taken up by the given directory and its subdirectories.

	Parameters
	----------
	startPath : str
		The given directory.

	Returns
	-------
	int
		The number of bytes taken up by the directory.
"""
def getDirSize(startPath = '.'):
	totalSize = 0
	for dirpath, dirnames, filenames in os.walk(startPath):
		for f in filenames:
			fp = os.path.join(dirpath, f)
			# skip if it is symbolic link
			if not os.path.islink(fp):
				totalSize += os.path.getsize(fp)
	return totalSize

####################
# ARRAY MANAGEMENT #
####################

"""
	Returns the number of elements (including duplicates) that exist in two different given arrays.

	Parameters
	----------
	arr1 : list
		The first array.
	arr2 : list
		The second array.

	Returns
	-------
	int
		The number of elements in the overlap
"""
def arrayOverlap(arr1, arr2):
	count = 0
	for a in arr1:
		if a in arr2:
			count += 1
	return count

"""
	Merges a nested array into a single one-dimensional array.

	Parameters
	----------
	arr : list
		The nested array that will be merged.
	finalArr : list (str)
		Should be ignored (only used in recursion). The created array so far.

	Returns
	-------
	list (str):
		The merged array.

	Example
	-------
	Input
		[item1, [item2, item3], item4, [item 5, [item6, item7], item8]]
	Output
		[item1, item2, item3, item4, item5, item6, item7, item8]
"""
def mergeNestedArray(arr, finalArr=[]):
	for val in arr:
		if not isinstance(val, list):
			finalArr.append(val)
		else:
			finalArr = mergeNestedArray(val, finalArr)
	return finalArr

"""
	From https://www.geeksforgeeks.org/python-find-most-frequent-element-in-a-list/

	Returns the most common element in a list, along with how many times it occurrs.

	Parameters
	----------
	arr : list
		The array.

	Returns
	-------
	anything
		The most frequently-occurring element.
	int
		How many instances of this element there are in the array.
"""
def most_frequent(arr): 
	counter = 0
	elem = arr[0]
	for i in arr:
		curr_frequency = arr.count(i)
		if (curr_frequency > counter):
			counter = curr_frequency
			elem = i
	return elem, counter

"""
	Returns whether or not arr1 is an ordered subset of arr2.

	Parameters
	----------
	arr1 : list
		The first array.
	arr2: list
		The second array.

	Returns
	-------
	bool
		Whether or not arr1 is an ordered subset of arr2.

	Examples
	--------
	Input 1
		[3, 5], [1, 3, 5, 7, 9]
	Output 1
		True
	Input 2
		[3, 5], [1, 2, 3, 4, 5, 6, 7]
	Output 2
		False
"""
def arrayInArray(arr1, arr2):
	for i in range(len(arr2)-len(arr1)+1):
		passed = True
		for j in range(len(arr1)):
			if arr1[j] != arr2[i+j]:
				passed = False
				break
		if passed:
			return True
	return False

###############################
# CONSOLE/TERMINAL MANAGEMENT #
###############################

"""
	Clears the console screen.
"""
def clearScreen():
	os.system('clear' if os.name =='posix' else 'cls')

"""
	From https://www.quora.com/How-can-I-delete-the-last-printed-line-in-Python-language

	Clears ("backspaces") the last n console lines.

	PARAMETERS
	----------
	n : int
		The number of lines to clear.
"""
def delete_last_lines(n=1): 
	for _ in range(n): 
		sys.stdout.write('\x1b[1A')
		sys.stdout.write('\x1b[2K')

#######################
# STRING MANIPULATION #
#######################

"""
	Prints a title surrounded by a certain character.

	Parameters
	----------
	string : str
		The string that is printed.
	char : str
		The one-character string that surrounds the string.

	Example
	-------
	Input
		"MY TITLE"
	Output
		############
		# MY TITLE #
		############
"""
def printTitle(string, topBottomChar="#", sideChar="#", cornerChar="#"):
	topBottom = cornerChar+(topBottomChar*(len(string)+2))+cornerChar
	print(topBottom)
	print(sideChar+" "+string+" "+sideChar)
	print(topBottom)

"""
	Returns the base string with either the singular or plural suffix depending on the value of num.

	Parameters
	----------
	base : str
		The base of the word.
	num : int
		The quantity of the desired word.
	singularSuffix : str
		The suffix of the word's singular form
	pluralSuffix : str
		The suffix of the word's plural form

	Returns
	-------
	str
		The resulting string

	Examples
	--------
	Input 1
		pluralize("ind", 1, "ex", "ices")
	Output 1
		"index"
	Input 2
		pluralize("ind", 2, "ex", "ices")
	Output 2
		"indices"

"""
def pluralize(base, num, singularSuffix="", pluralSuffix="s"):
	return base+singularSuffix if num == 1 else base+pluralSuffix

"""
	Creates a copy of a given string, automatically adding line breaks and indenting lines, without splitting any words in two.
	A line's length will only exceed the given limit if a single word in the string exceeds it.

	Parameters
	----------
	string : str
		The string to be printed.
	lineLength : int
		The max length of each printed line.
	firstLineIndent : str
		The start of the first line.
	lineIndent : str
		The start of all subsequent lines.

	Returns
	-------
	The output string.

	Examples
	--------
	Input 1
		limitedString("Strong Bad's test sentence is as follows: The fish was delish, and it made quite a dish.", 40, "? ", ". ! ")
	Output 1
		"? Strong Bad's test sentence is as\n. ! follows: The fish was delish, and it\n. ! made quite a dish."
		(Which would look like the following when printed):
		? Strong Bad's test sentence is as
		. ! follows: The fish was delish, and it
		. ! made quite a dish.
	Input 2
		limitedString("THIS_WORD_IS_VERY_LONG there", 15, "", "")
	Output 2:
		"THIS_WORD_IS_VERY_LONG\nthere"
		(Which would look like the following when printed):
		THIS_WORD_IS_VERY_LONG
		there
"""
def limitedString(string, lineLength=80, firstLineIndent="", lineIndent="  "):
	printArray = string.split(" ")
	totalString = ""
	currString = firstLineIndent
	isStartOfLine = True
	while len(printArray) > 0:
		if isStartOfLine or (len(printArray[0]) + (not isStartOfLine) <= lineLength - len(currString)):
			currString += (" " if not isStartOfLine else "")+printArray.pop(0)
			isStartOfLine = False
		else:
			totalString += currString+"\n"
			currString = lineIndent
			isStartOfLine = True
	totalString += currString
	return totalString

"""
	Shortens a string to a maximum length, padding the last few characters with a given character if necessary.
	You have the option of whether or not the string can cut off mid-word.

	Parameters
	----------
	string : str
		The string to be shortened.
	maxLength : int
		The maximum length of the output.
	suffixChar : str
		The character that will pad a long string
	suffixLength : int
		The length of the padding
	cutoff : bool
		If True, the string can be cut mid-word; else, it will be cut at the end of the previous word.

	Returns
	-------
	The (possibly) shortened string, with spaces stripped from the right side of the pre-padded output.

	Examples
	--------
	Input 1
		shorten("this string is too long", 20, '.', 3, True)
	Output 1
		"This string is to..."
	Input 2
		shorten("this string is too long", 20, '.', 3, False)
	Output 2
		"This string is..."
	Input 3
		shorten("this is short", 15, '.', 3, True)
	Output 3
		"this is short"
"""
def shorten(string, maxLength=10, suffixChar='.', suffixLength=3, cutoff=True):
	if len(string) <= maxLength:
		return string
	if cutoff:
		return string[:(maxLength-suffixLength)].rstrip()+(suffixChar*suffixLength)
	shortened = string.rstrip()
	while len(shortened) > maxLength-suffixLength:
		shortened = " ".join(shortened.split(" ")[:-1]).rstrip()
	return shortened+(suffixChar*suffixLength)

"""
	Splits a string into multiple parts, with each part being about equal in length, and no words cut off in the middle.

	Parameters
	----------
	string : str
		The string to be split.
	numParts : int
		The number of parts to split the string into.
	reverse : bool
		Decide if the last part (False) or first part (True) is likely to be the longest part.

	Returns
	-------
	list
		The split string.

	Examples
	--------
	Input 1
		splitStringIntoParts("This string is split into three whole parts", 3, True)
	Output 1
		['This string is split', 'into three', 'whole parts']
	Input 2
		splitStringIntoParts("This string is split into three whole parts", 3, False)
	Output 2
		['This string', 'is split into', 'three whole parts']
"""
def splitStringIntoParts(string, numParts=2, reverse=False):
	totalLen = len(string) - (numParts-1)
	maxSubStringLength = math.ceil(totalLen/numParts)
	stringArray = string.split(" ")
	if reverse:
		stringArray.reverse()
	splitArray = []
	currString = ""
	offset = 0
	while len(stringArray) > 0:
		if len(currString) + (currString != "") + len(stringArray[0]) < maxSubStringLength + offset:
			currString += (" " if currString != "" else "")+stringArray.pop(0)
		else:
			offset = (maxSubStringLength + offset) - (len(currString) + (currString != ""))
			splitArray.append(currString)
			currString = ""
	splitArray[-1] += " "+currString
	if reverse:
		newSplitArray = []
		while len(splitArray) > 0:
			curr = splitArray.pop(-1).split(" ")
			curr.reverse()
			curr = " ".join(curr)
			newSplitArray.append(curr)
		return newSplitArray
	return splitArray

"""
	Returns a string indicating the input number of bytes in its most significant form, rounding up to the indicated number of decimal places.
	For example, if numBytes is at least 1 MB but less than 1 GB, it will be displayed in MB.

	Parameters
	----------
	numBytes : int
		The number of bytes.
	decimalPlaces : int
		The number of decimal places to round to.

	Returns
	-------
	str
		The number of the most significant data size, along with the data size itself.

	Examples
	--------
	Input 1
		5000000, 3
	Output 1
		4.769 MB
	Input 2
		2048, 1
	Output 2
		2 KB
	Input 3
		2049, 1
	Output 3
		2.1 KB
"""
def simplifyNumBytes(numBytes, decimalPlaces=2):
	numBytes = float(numBytes)
	byteTypeArray = ["B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB"]
	temp = (10.0**decimalPlaces)
	for byteType in byteTypeArray:
		if numBytes < 1024:
			num = math.ceil(numBytes * temp) / temp
			if num == int(num):
				num = int(num)
			return str(num)+" "+byteType
		numBytes /= 1024.0
	numBytes *= 1024
	num = math.ceil(numBytes * temp) / temp
	if num == int(num):
		num = int(num)
	return str(num)+" YB"

"""
	Converts a string to a filename-friendly format by replacing incompatible characters with underscores and shortening blank spaces.

	Parameters
	----------
	value : str
		The original file name.
	stripValue : bool
		If True, the value will also be stripped of any whitespace.

	Returns
	-------
	str
		The new file name.

	Examples
	--------
	Input
		"What? Yes...   <THIS> is: a file name!.png"
	Output
		"What_ Yes... [THIS] is - a file name!.png"
"""
def slugify(value, stripValue=True):
	value = unicodedata.normalize('NFKD', value)
	value = re.sub(':\s', ' - ', value)
	value = re.sub(':', '-', value)
	value = re.sub('\"', '\'', value)
	value = re.sub('<', '[', value)
	value = re.sub('>', ']', value)
	value = re.sub('[\\/\*|]', '-', value)
	value = re.sub('[?]', '_', value)
	value = re.sub('[\s]+', ' ', value)
	if stripValue:
		value = value.strip()
	return value

"""
	From https://en.wikibooks.org/wiki/Algorithm_Implementation/Strings/Longest_common_substring#Python

	Returns the longest common substring between two strings.

	Parameters
	----------
	s1 : str
		The first string.
	s2 : str
		The second string.

	Returns
	-------
	str
		The longest common substring length.

	Examples
	--------
	Input
		"Microwave oven", "Infrared waves"
	Output
		
"""
def lcs(s1, s2):
	m = [[0] * (1 + len(s2)) for i in range(1 + len(s1))]
	longest, x_longest = 0, 0
	for x in range(1, 1 + len(s1)):
		for y in range(1, 1 + len(s2)):
			if s1[x - 1] == s2[y - 1]:
				m[x][y] = m[x - 1][y - 1] + 1
				if m[x][y] > longest:
					longest = m[x][y]
					x_longest = x
			else:
				m[x][y] = 0
	return s1[x_longest - longest: x_longest]

#########
# OTHER #
#########

"""
	Returns an array of a given number of values spaced out by another given value, with offset as the average.
	Optionally, a fixed number of decimal places can be defined (to fix float rounding issues).

	Parameters
	----------
	numValues : int
		The number of values to be spaced out.
	spaceSize : float
		The size of the space.
	offset : float
		The average of all values.

	Returns
	-------
	array
		The spaced out array.

	Examples
	--------
	Input 1
		3, 10, 0
	Output 1
		[-10, 0, 10]
	Input 2
		4, 8, 0
	Output 2
		[-12, -4, 4, 12]
	Input 3
		3, 10, 2
	Output 3
		[-8, 2, 12]
"""
def spaceOut(numValues, spaceSize, offset=0, numDecimalPlaces=None):
	evenNumOfValues = (numValues%2 == 0)
	if numDecimalPlaces is None:
		return [spaceSize*(i-math.floor(numValues/2) + (0.5 if evenNumOfValues else 0)) + offset for i in range(numValues)]
	array = []
	for i in range(numValues):
		array.append(round(spaceSize*(i-math.floor(numValues/2) + (0.5 if evenNumOfValues else 0)) + offset, numDecimalPlaces))
	return array

"""
SOURCES

dec_to_base
https://www.codespeedy.com/inter-convert-decimal-and-any-base-using-python/

removeEmptyFolders
https://gist.github.com/jacobtomlinson/9031697

getDirSize
https://stackoverflow.com/questions/1392413/calculating-a-directorys-size-using-python

most_frequent
https://www.geeksforgeeks.org/python-find-most-frequent-element-in-a-list/

delete_last_lines
https://www.quora.com/How-can-I-delete-the-last-printed-line-in-Python-language

lcs
https://en.wikibooks.org/wiki/Algorithm_Implementation/Strings/Longest_common_substring#Python

All other functions made by GateGuy
"""

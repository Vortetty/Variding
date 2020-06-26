import secrets, json, time
from lists import lists
from lists import metadata as metaTable

def encoder(inputText, n = 0):
    """
        :param input: The input string
        :param n: Optional, if not defined it will be changed to the number that best compresses your text. Valid values are [1,2,3,4,5,8,12,16,64]. Yes i took the time to write these lists. It defines what character set is used. The number cannot be larger than the length of the binary representation of your string. And the `length of the binary representation modulo n` must be 0 or the optimal one will be used
        :param lists: Optional, if defined it will encode with you custom lists. These lists must be the same format as the default and you must decode with these lists.

        encodes the input 
    """
    shiftAmmnt = secrets.randbelow(len(lists["16"]))
    #for i in range(len(lists)):
    #    lists[i] = shift(lists, shiftAmmnt)

    encodeLengths = [1,2,3,4,5,8,12,16,64]
    if inputText.isascii():
        inputText = tobits(inputText)
    else:
        return "String is non-ascii, please try again with an ascii encoded string"

    i = len(encodeLengths) - 1 
    if n not in encodeLengths or len(inputText) % n:
        while i >= 0:
            if len(inputText) % encodeLengths[i] == 0:
                print("Using table of length: " + str(encodeLengths[i]))
                n = encodeLengths[i]
                break
            i -= 1

    i = None

    inputText = [inputText[i: i + n] for i in range(0, len(inputText), n)]

    output = ""

    if n < 32:
        lists[str(n)] = shift(lists[str(n)], n=shiftAmmnt)
        for i in range(len(inputText)):
            print("Chunk " + str(i+1) + ": " + inputText[i] + " → " + str(int(inputText[i], 2)) + " (" + lists[str(n)][int(inputText[i], 2)] + ")")
            output += lists[str(n)][int(inputText[i], 2)]
        print("Total Chunks: " + str(len(inputText)))
        print("Used table of length: " + str(n) + ", Shifted " + str(shiftAmmnt) + " places right (down)")
    else:
        #this tells you how many symbols are needed to do each number
        if n == 32:
            n1 = 217
        elif n == 64:
            n1 = 55111
        for i in range(len(inputText)):
            print("Chunk " + str(i+1) + ": " + inputText[i] + " → " + str(int(inputText[i], 2)) + " (" + lists["32+"](int(inputText[i], 2), n1, n) + ")")
            output += lists["32+"](int(inputText[i], 2), n1, n)
        print("Total Chunks: " + str(len(inputText)))
        print("Used table of length: " + str(n) + ", Shifted " + str(shiftAmmnt) + " places right (down)")
    
    # Now that we have the basic output, add some more data for decoding
    # "⌬" is our separator in this case, you can use your own separator provided it does not appear as a character in lists.py, you also must make the custom character the last character in the string (for reasons that should be obvious)
    # this is what table was used
    output += ("⌬" + str(n))
    # This is how far the list was shifted
    output += ("⌬" + ''.join(chr(shiftAmmnt)))
    # This is other metadata, just a json string, parameters are encoder name/nickname, discord ping if you have one (if you dont just put "null" or "nil"), timestamp (unix time, will be localized to the user upon decompilation), and author of the program used with contact for the author. other data can be specified and will be printed upon reading of the json.
    # metadata = tobits('{"name":"Vortetty","discord":"Vortetty#7462","timestamp":' + str(time.time()) + ',"Author":"Vortetty#7462","Encoder_Written_In": "Python 3.8.3", "Encoder/Decoder_Version":"1"}')
    # metadata = tobits('{"discord":"Vortetty#7462"}')
    # i = None
    # metadata = [metadata[i : i + 8] for i in range(0, len(metadata), 8)]
    # encmetadata = ""
    # for i in range(len(metadata)):
    #     encmetadata += metaTable[int(metadata[i], 2)]
    # output += ("⌬" + encmetadata)

    # this is how the decoder knows what separator to use :)
    output += "⌬"

    return output

def decoder(input):
    text = split(input.split(input[-1])[0])
    tableID = input.split(input[-1])[1]
    shiftAmmnt = ord(input.split(input[-1])[2])
    metadata = input.split(input[-1])[3]
    separator = input[-1]

    if int(tableID) < 32:
        lists[tableID] = shift(lists[tableID], n=shiftAmmnt)
        output = ""
        for i in range(len(text)):
            preout = ""
            print("Chunk " + str(i+1) + ": " + text[i] + " (" + str(lists[str(tableID)].index(text[i])) + ")" + " → " + str("0" + "{0:b}".format(lists[str(tableID)].index(text[i]), 2)))
            preout = str("0" + "{0:b}".format(lists[str(tableID)].index(text[i]), 2))
            while len(preout) < int(tableID):
                preout = "0" + preout
            output += preout
        output = frombits(output)
    else:
        if int(tableID) == 32:
            n1 = 217
            add = 0
        elif int(tableID) == 64:
            n1 = 55111
            add = 10712793383044096
        output = ""
        text = ["".join(text)[i:i+4] for i in range(0, len("".join(text)), 4)]
        for i in range(len(text)):
            preout = ""
            print("Chunk " + str(i+1) + ": " + str(text[i]) + " (" + str(lists["32+d"](text[i], n1, shiftAmmnt) + add) + ") → " + str("0" + "{0:b}".format(lists["32+d"](text[i], n1, shiftAmmnt) + add, 2)))
            preout = str("0" + "{0:b}".format(lists["32+d"](text[i], n1, shiftAmmnt) + add,2))
            while len(preout) < int(tableID):
                preout = "0" + preout
            output += preout
        output = frombits(output)

    premetadata = ""
    prepremetadata = ""
    for i in range(len(metadata)):
        premetadata = str("0" + "{0:b}".format(metaTable.index(metadata[i]), 2))
        while len(premetadata) < 8:
            premetadata = "0" + premetadata
        prepremetadata += premetadata
    metadata = prepremetadata
    metadata = frombits(metadata)

    return output, metadata

def tobits(s):
    result = []
    for c in s:
        bits = bin(ord(c))[2:]
        bits = '00000000'[len(bits):] + bits
        result.extend([b for b in bits])
    return "".join(result)

def frombits(bits):
    chars = []
    for b in range(int(len(bits) / 8)):
        byte = bits[b*8:(b+1)*8]
        chars.append(chr(int("".join([str(bit) for bit in byte]), 2)))
    return "".join(chars)

def shift(seq, n=0):
    a = n % len(seq)
    return seq[-a:] + seq[:-a]

def shiftl(seq, n=0):
    a = n % len(seq)
    return seq[:-a] + seq[-a:]

def split(word): 
    return [char for char in word]


#uncomment the below line and set the string to encode stuff
#print(encoder(""))

#uncommenr the below like and set the string to decode stuff
#print(decoder(""))

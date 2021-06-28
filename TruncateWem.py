import struct
import sys

def ReadUInt(file):
    return struct.unpack("I",file.read(4))[0]

def GetUIntFromBytes(buffer,start,end):
    return struct.unpack("I",buffer[start:end])[0]

def GetBytesFromUInt(value):
    return struct.pack("I",value)

def truncateWem(infile,outfile):
    #hold values as they are read
    outArray = bytearray()
    #first read RIFF header
    RIFF = infile.read(4)
    assert RIFF == b'RIFF'
    RIFFSize = infile.read(4) #not needed to interpret, since we just throw it into the outfile
    WAVE = infile.read(4)
    assert WAVE == b'WAVE'
    #add riff header to bytearray
    outArray.extend(RIFF)
    outArray.extend(RIFFSize)
    outArray.extend(WAVE)
    #now begin reading wave chunks
    #first should always be "fmt "
    wvFmt = infile.read(4)
    assert wvFmt == b'fmt '
    fmtLen = ReadUInt(infile)
    #now read into byte array
    fmtHdr = infile.read(fmtLen)
    #get vorbisOffset
    vorbisOffset = GetUIntFromBytes(fmtHdr,0x2c,0x30)
    #now add into byte array
    outArray.extend(wvFmt)
    outArray.extend(GetBytesFromUInt(fmtLen))
    outArray.extend(fmtHdr)
    #cycle through the rest of the chunks until data
    magic = infile.read(4)
    length = ReadUInt(infile)
    while(magic != b'data'):
        #add to bytearray
        outArray.extend(magic)
        outArray.extend(GetBytesFromUInt(length))
        outArray.extend(infile.read(length))
        magic = infile.read(4)
        length = ReadUInt(infile)
    #now that we are at data, we actually truncate the file
    #we want to make sure all of the "header" information of data is preserved, which is why we grab vorbis offset
    dataBuffer = infile.read(length)
    checkByte = dataBuffer[vorbisOffset]
    endOffset = vorbisOffset
    while(checkByte != 0x00):
        endOffset+= 1
        checkByte = dataBuffer[endOffset]
    #now copy to bytearray
    outArray.extend(magic)
    outArray.extend(GetBytesFromUInt(length))
    outArray.extend(dataBuffer[0:endOffset])
    #now write to file
    outfile.write(outArray)
    infile.close()
    outfile.close()


if __name__ == "__main__":
    for i, arg in enumerate(sys.argv):
        if i > 0:
            truncateWem(open(arg,'rb'),open(arg.replace(".wem","-truncated.wem"),'wb'))
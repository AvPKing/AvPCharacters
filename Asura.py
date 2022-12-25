import zlib
import io

def int32(input):
    return input & 0xffffffff

def parseInt32(bytesIO):
    intBytes = bytesIO.read(4)
    return int.from_bytes(intBytes, 'little')
    
def getAsrFileAsBytesIO(f):
    asrType = f.read(8)
    if asrType == b'AsuraZlb':
        zeros = parseInt32(f)
        compressedDataSize = parseInt32(f)
        decompressedFileSize = parseInt32(f)
        compressedData = f.read(compressedDataSize)
        decompressedData = zlib.decompress(compressedData)
        if len(decompressedData) != decompressedFileSize:
            raise Exception('Corrupted asura file')
        else:
            bytesIO = io.BytesIO(decompressedData)
            asrHeader = bytesIO.read(8)
            if(asrHeader == b'Asura   '):
                return bytesIO
            else:
                raise Exception('Corrupted asura file')
    elif asrType == b'Asura   ':
        size = getFileSize(f)
        size = size - 0x8
        #skip b'Asura   '
        #f.seek(8,1)
        return io.BytesIO(f.read(size))
    else:
        raise Exception('Invalid asura header')

def parseChunkDict(sourceInp):
    f = open(sourceInp, 'rb')
    bytesIO = getAsrFileAsBytesIO(f)
    chunkDict = {}
    while True:
        chunkID = bytesIO.read(4)
        chunkID_int = int.from_bytes(chunkID, 'little')
        if chunkID_int != 0:
            chunkSizeBytes = bytesIO.read(4)
            chunkSizeInt = int.from_bytes(chunkSizeBytes, 'little')
            bytesIO.seek(-8,1)
            chunkBytes = bytesIO.read(chunkSizeInt)
            if chunkID in chunkDict:
                chunkDict[chunkID].append(chunkBytes)
            else:
                chunkDict[chunkID] = [chunkBytes]
        else:
            break
    return chunkDict
    
def exportChunkDict(destInp, chunkDict):
    f = open(destInp, 'wb')
    asuraUncompressed = io.BytesIO()
    asuraUncompressed.write(b'Asura   ')
    for chunkID in chunkDict:
        chunkList = chunkDict[chunkID]
        for chunk in chunkList:
            asuraUncompressed.write(chunk)
    asuraUncompressed.write(b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')
    compObj = zlib.compressobj(level=zlib.Z_DEFAULT_COMPRESSION, method=zlib.DEFLATED, wbits=13, memLevel=9, strategy=zlib.Z_DEFAULT_STRATEGY)
    sizeUncompressed = getFileSize(asuraUncompressed)
    compressedData = compObj.compress(asuraUncompressed.getbuffer())
    compressedData += compObj.flush()
    f.write(b'AsuraZlb')
    f.write(b'\x00\x00\x00\x00')
    f.write(len(compressedData).to_bytes(4, 'little'))
    f.write(sizeUncompressed.to_bytes(4, 'little'))
    f.write(compressedData)

def readPaddedByteStr(bytes, startPos):
   end = bytes.find(b'\0', startPos)
   if end != -1:
      return bytes[startPos:end]
   else:
      return bytes[startPos:]


def getFileSize(f):
    curPos = f.tell()
    size =  f.seek(0, 2)
    f.seek(curPos, 0)
    return size

    
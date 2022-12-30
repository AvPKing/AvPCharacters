import zlib
import io
import hashlib

def int32(input):
    return input & 0xffffffff

def parseInt32(bytesIO):
    intBytes = bytesIO.read(4)
    return int.from_bytes(intBytes, 'little')
    

class ZlibBytesIO:
    def __init__(self, io):
        self.io = io
        self.buffer = b''
        self.CHUNK_SIZE = 1024
        self.decompData = b''
        self.decompObj = zlib.decompressobj(13)
        self.compObj = zlib.compressobj(level=zlib.Z_DEFAULT_COMPRESSION, method=zlib.DEFLATED, wbits=13, memLevel=9, strategy=zlib.Z_DEFAULT_STRATEGY)
    
    def read(self, nBytes):
        while len(self.decompData) < nBytes:
            self.buffer = self.io.read(self.CHUNK_SIZE)
            if not self.buffer:
                break
            else:
                self.decompData = self.decompData + self.decompObj.decompress(self.buffer)
        result = self.decompData[:nBytes]
        self.decompData = self.decompData[nBytes:]
        return result

    def write(self, bytes):
        compressedBytes = self.compObj.compress(bytes)
        compressedBytes = compressedBytes + self.compObj.flush(zlib.Z_NO_FLUSH)
        self.io.write(compressedBytes)
        return len(compressedBytes)

    def close(self):
        self.io.write(self.compObj.flush())


class AsuraFileReader:
    def __init__(self, filename):
        self.file = open(filename, 'rb')
        self.file.seek(0x10, 0)
        self.toRead = int.from_bytes(self.file.read(4), 'little')
        self.chunkDataRead = 0
        self.file.seek(0x14, 0)
        self.zlb = ZlibBytesIO(self.file)

    def getPercentageRead(self):
        return (self.chunkDataRead/self.toRead) * 100

    def getNextChunk(self):
        if self.file.tell() == 0x14:
            header = self.zlb.read(8)
            self.chunkDataRead = self.chunkDataRead + 8
            return self.getNextChunk()
        else:
            chunkID = self.zlb.read(4)
            if chunkID == b'\x00\x00\x00\x00' or b'':
                return b''
            szChunk = int.from_bytes(self.zlb.read(4), 'little')
            self.chunkDataRead = self.chunkDataRead + szChunk
            toReturn = chunkID + szChunk.to_bytes(4, 'little') + self.zlb.read(szChunk - 0x8)
            return toReturn
            
class AsuraFileWriter:
    def __init__(self, filename):
        self.file = open(filename, 'wb')
        self.zlb = ZlibBytesIO(self.file)
        self.file.write(b'AsuraZlb')
        self.file.write(b'\x00\x00\x00\x00')
        self.uncompressedSize = 8
        self.compressedSize = 0
        self.file.write(b'\x00\x00\x00\x00')
        self.file.write(b'\x00\x00\x00\x00')
        self.compressedSize = self.zlb.write(b'Asura   ')
        currPos = self.file.tell()
        self.file.seek(0xC, 0)
        self.file.write(self.compressedSize.to_bytes(4, 'little'))
        self.file.write(self.uncompressedSize.to_bytes(4, 'little'))
        self.file.seek(currPos, 0)
        self.chunkHashList = []

    def chunkExists(self, chunk):
        chunkHash = hashlib.md5(chunk).digest()
        return chunkHash in self.chunkHashList

    def writeChunk(self, chunk):
        chunkHash = hashlib.md5(chunk).digest()
        if chunkHash in self.chunkHashList:
            return
        nWritten = self.zlb.write(chunk)
        if nWritten > 0:
            self.chunkHashList.append(chunkHash)
        curFPos = self.file.tell()
        self.file.seek(0xc,0)
        self.uncompressedSize = self.uncompressedSize + int.from_bytes(chunk[4:8], 'little')
        self.compressedSize = self.compressedSize + nWritten
        self.file.write(self.compressedSize.to_bytes(4, 'little'))
        self.file.write(self.uncompressedSize.to_bytes(4, 'little'))
        self.file.seek(curFPos, 0)

    def __del__(self):
        self.zlb.write(b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')
        self.zlb.close()


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

    
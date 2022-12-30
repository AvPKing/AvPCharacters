import Asura
import os
import re
import time

def filterCharacters(chunkDict):
    toRemove = []
    materialRSCFList = b''
    for key in chunkDict:
        if key == b'FNFO':
            continue
        if key == b'RSFL':
            continue
        if key == b'RSCF':
            toRemoveChunks = []
            for chunk in chunkDict[key]:
                filename = Asura.readPaddedByteStr(chunk, 28)
                if(filename == b'Material Response Texture'):
                    toRemoveChunks.append(chunk)
                    if not materialRSCFList == b'':
                        raise Exception('Trying to parse ChunkDict with more than one Material Response Texture...')
                    else:
                        materialRSCFList = chunk
            for chunk in toRemoveChunks:
                chunkDict[key].remove(chunk)
            continue
        if key == b'SDSM':
            continue
        if key == b'SDEV':
            continue
        if key == b'DLEV':
            continue
        if key == b'HANM':
            continue
        if key == b'FACE':
            continue
        if key == b'FAAN':
            continue
        if key == b'MTRL':
            continue
        if key == b'HSKN':
            continue
        if key == b'HSKL':
            continue
        if key == b'HMPT':
            continue
        if key == b'HSND':
            continue
        if key == b'HSBB':
            continue
        if key == b'FXPT':
            continue
        if key == b'FXST':
            continue
        if key == b'FXET':
            continue
        if key == b'FSX2':
            continue
        if key == b'TXAN':
            continue
        # if key == b'apas':
        #    continue
        # if key == b'hpas':
        #    continue
        # if key == b'ppas':
        #    continue
        if key == b'MARE':
            continue
        toRemove.append(key)
    for key in toRemove:
        chunkDict.pop(key)
    return materialRSCFList

def filterCharactersPredicate(chunk):
    key = chunk[0:4]
    if key == b'FNFO':
        return False
    if key == b'RSFL':
        return False
    if key == b'RSCF':
        filename = Asura.readPaddedByteStr(chunk, 28)
        if(filename == b'Material Response Texture'):
            return True
        else:
            return False
    if key == b'SDSM':
        return False
    if key == b'SDEV':
        return False
    if key == b'DLEV':
        return False
    if key == b'HANM':
        return False
    if key == b'FACE':
        return False
    if key == b'FAAN':
        return False
    if key == b'MTRL':
        return False
    if key == b'HSKN':
        return False
    if key == b'HSKL':
        return False
    if key == b'HMPT':
        return False
    if key == b'HSND':
        return False
    if key == b'HSBB':
        return False
    if key == b'FXPT':
        return False
    if key == b'FXST':
        return False
    if key == b'FXET':
        return False
    if key == b'FSX2':
        return False
    if key == b'TXAN':
        return False
    # if key == b'apas':
    #    return False
    # if key == b'hpas':
    #    return False
    # if key == b'ppas':
    #    return False
    if key == b'MARE':
        return False
    return True

def filterOnlyMares(chunkDict):
    toRemove = []
    for key in chunkDict:
        if key == b'MARE':
            continue
        toRemove.append(key)
    for key in toRemove:
        chunkDict.pop(key)

def mergeChunkDict (firstDict, secondDict):
    for key in secondDict:
        for chunk in secondDict[key]:
            if not key in firstDict:
                firstDict[key] = secondDict[key]
            else:
                found = False
                for fchunk in firstDict[key]:
                    if fchunk == chunk:
                        if key == b'RSCF':
                            filename = Asura.readPaddedByteStr(chunk, 28)
                        found = True
                        break
                if not found:
                    firstDict[key].append(chunk)

def lowMemoryProcess():
    AvPFolder = input("Enter the root AvP folder: ")
    dest = os.path.join(AvPFolder, 'Characters/All_Characters.asr')
    AllCharacters = Asura.AsuraFileWriter(dest)
    print('Processing, this can take a few minutes...')
    start = time.time()
    for dirpath, dirnames, filenames in os.walk(AvPFolder):
        for file in filenames:
            regex = '([A,M,P]0[0-9]_[\\w]+\\.pc)|(Multiplayer.asr)'
            fullName = os.path.join(dirpath, file)
            if re.search(regex, file):
                if dirpath.endswith('/MP') or dirpath.endswith('\\MP') or ('P00_Tutorial' in file):
                    continue
                else:
                    print(f'File found: {fullName}. Extracting characters...', end='\r')
                    asrFile = Asura.AsuraFileReader(fullName)
                    nextChunk = asrFile.getNextChunk()
                    while nextChunk != b'':
                        print(f'File found: {fullName}. Extracting characters... {round(asrFile.getPercentageRead(), 2)}%', end='\r')
                        if (not filterCharactersPredicate(nextChunk)):
                            AllCharacters.writeChunk(nextChunk)
                        nextChunk = asrFile.getNextChunk()
                    print('')
    mplst = open(os.path.join(AvPFolder, 'Characters/Multiplayer.lst'), "w")
    mplst.write('Characters/All_Characters.asr\n')
    mplst.write('Characters/Multiplayer.en\n')
    end = time.time()
    totalTimeElapsed = round((end - start)/60, 2)
    print('Done.')
    print(f'Total execution time: {totalTimeElapsed} minutes')



def main():
    lowMemoryPC = input('Does your pc have less than 4 gigabytes of RAM? (Yes/No): ')
    if lowMemoryPC.lower() == 'yes':
        print('Activating low memroy mode...')
        lowMemoryProcess()
        return
    AvPFolder = input("Enter the root AvP folder: ")
    dest = os.path.join(AvPFolder, 'Characters/All_Characters.asr')
    chunkDict = {}
    mareDict = {}
    print('Processing, this can take a few minutes...')
    start = time.time()
    for dirpath, dirnames, filenames in os.walk(AvPFolder):
        for file in filenames:
            regex = '([A,M,P]0[0-9]_[\\w]+\\.pc)|(Multiplayer.asr)'
            fullName = os.path.join(dirpath, file)
            if re.search(regex, file):
                if dirpath.endswith('/MP') or dirpath.endswith('\\MP') or ('P00_Tutorial' in file):
                    continue
                if not chunkDict:
                    print(f'Creating chunk dict with file: {fullName}')
                    chunkDict = Asura.parseChunkDict(fullName)
                    MARETexture = filterCharacters(chunkDict)
                    mareTextureFile = {}
                    mareTextureFile[b'RSCF'] = [MARETexture]
                    mareDict[file] = mareTextureFile
                else:
                    print(f'Merging with: {fullName}')
                    temp = Asura.parseChunkDict(fullName)
                    MARETexture = filterCharacters(temp)
                    mareTextureFile = {}
                    mareTextureFile[b'RSCF'] = [MARETexture]
                    mareDict[file] = mareTextureFile
                    mergeChunkDict(chunkDict, temp)
    Asura.exportChunkDict(dest, chunkDict)
    mplst = open(os.path.join(AvPFolder, 'Characters/Multiplayer.lst'), "w")
    mplst.write('Characters/All_Characters.asr\n')
    mplst.write('Characters/Multiplayer.en\n')
    end = time.time()
    totalTimeElapsed = round((end - start)/60, 2)
    print('Done.')
    print(f'Total execution time: {totalTimeElapsed} minutes')




if __name__ == "__main__":
    main()
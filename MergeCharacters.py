import Asura
import os
import re

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

def main():
    AvPFolder = input("Enter the root AvP folder: ")
    chunkDict = {}
    mareDict = {}
    print('Processing, this can take a few minutes...')
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
    dest = os.path.join(AvPFolder, 'Characters/All_Characters.asr')
    Asura.exportChunkDict(dest, chunkDict)
    destPath = os.path.join(AvPFolder, 'Characters/mission')
    if not os.path.isdir(destPath):
        os.mkdir(destPath)
    for file in mareDict:
        dest = os.path.join(destPath, file)
        Asura.exportChunkDict(dest, mareDict[file])
    mplst = open(os.path.join(AvPFolder, 'Characters/Multiplayer.lst'), "w")
    mplst.write('Characters/All_Characters.asr\n')
    mplst.write('Characters/Multiplayer.en\n')
    print('Done.')




if __name__ == "__main__":
    main()
import os
import time
import datetime
import pickle
import logging

KEYSTORE_PREFIX = ''
KEYSTORE_SUFFIX = '.keystore'
DEFAULT_PATH = './'


class KeystoreBox:
    def __init__(self, Path_, KeystoreData_):
        self.Path = Path_
        self.KeystoreData = KeystoreData_

class KeystoreMaster:
    keystoreBox = None

    def __init__(self, KeystorePath_=None):
        if KeystorePath_ is not None:
            k = self.tryParseKeystoreFile(KeystorePath_)
            if k is not None:
                self.keystoreBox = KeystoreBox(KeystorePath_, k)

        if self.keystoreBox is None:
            kbox = self.searchForKeystore()
            if kbox is None:
                self.keystoreBox = self.createKeystore()
            else:
                self.keystoreBox = kbox

    def searchForKeystore(self, search_dir=DEFAULT_PATH):
        try:
            for filename in os.listdir(search_dir):
                if filename.endswith(KEYSTORE_SUFFIX):
                    k = self.tryParseKeystoreFile(search_dir+filename)
                    if k is not None:
                        kbox = KeystoreBox(search_dir+filename, k)
                        logging.debug('Keystore successfully found %s', kbox.Path)
                        return kbox
            return None
        except:
            logging.debug('Keystore search exception')
            return None

    def createKeystore(self, keystore_path=None):
        if keystore_path is None:
            keystore_path = DEFAULT_PATH + self.createKeystoreName()
        else:
            keystore_path += KEYSTORE_SUFFIX

        keystore_data = {
            'created': self.timestamp(),
            'uploads_info': {}
        }

        if self.marshal(keystore_path, keystore_data):
            logging.debug('Keystore created successfully %s', keystore_path)
            return KeystoreBox(keystore_path, keystore_data)
        else:
            logging.debug('Keystore creation exception')
            return None

    def tryParseKeystoreFile(self, filePath):
            data = self.unmarshal(filePath)

            if data is None or data.get('created') is None:
                logging.debug('Validation is not successful')
                return None
            logging.debug('Validation is successful')
            return data

    def getListOfUploadedFiles(self):
        print(list(self.keystoreBox.KeystoreData['uploads_info'].keys()))
        return list(self.keystoreBox.KeystoreData['uploads_info'].keys())

    def getUploadPiecesInfo(self, fileName):
        return self.keystoreBox.KeystoreData['uploads_info'].get(fileName)

    def createKeystoreName(self):
        return KEYSTORE_PREFIX + self.timestamp() + KEYSTORE_SUFFIX

    def isFilenameCollide(self, filename):
        if self.keystoreBox.KeystoreData['uploads_info'].get(filename) is None:
            return False
        else:
            return True

    def isFileCollide(self, filePath):
        fileName = os.path.basename(filePath)
        return self.isFilenameCollide(fileName)

    def addUploadedFileToKeystore(self, filename, upload_info):
        if self.keystoreBox is not None:
            if not self.isFilenameCollide(filename):
                self.keystoreBox.KeystoreData['uploads_info'][filename] = upload_info
                return self.marshal(self.keystoreBox.Path, self.keystoreBox.KeystoreData)
            else:
                logging.debug('Upload with same filename %s', filename)
                return False
        else:
            logging.debug('Keystore file is not present')
            return False

    def catKeystoreFile(self):
        print(self.tryParseKeystoreFile(self.keystoreBox.Path))

    def marshal(self, filePath, data):
        try:
            file = open(filePath, "wb")
            pickle.dump(data, file)
            file.close()
            return True
        except:
            logging.debug('Marshal exception')
            return False

    def unmarshal(self, filePath):
        try:
            file = open(filePath, "rb")
            data = pickle.load(file)
            file.close()
            return data
        except:
            logging.debug('Unmarshal exception')
            return None

    def timestamp(self):
            ts = time.time()
            return datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')

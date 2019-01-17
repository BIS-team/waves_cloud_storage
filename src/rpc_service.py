import zerorpc
import logging
import blockchain_interaction as BlIn
import keystore_interaction as KIn
import signal
import gevent
import sys
import datetime
import time

NODE = "https://testnode1.wavesnodes.com"
ADDRESS = "tcp://127.0.0.1:4242"
LOG_FORMAT = '%(levelname)s:\t%(asctime)-15s %(message)s'
LOG_LEVEL = logging.DEBUG

class RPC_service(object):
    blockm = None
    keym = None

    def signIn(self, seed):
        self.blockm = BlIn.BlockChainMaster(NODE, seed)
        self.keym = KIn.KeystoreMaster()

        data = {
            "address": self.blockm.Account.address
        }
        return data

    def getUploadHistory(self):
        return self.keym.getListOfUploadedFiles()

    def uploadFileToBlockchain(self, filePath):
        if not self.keym.isFileCollide(filePath):
            uploadFileInfo = self.blockm.uploadFile(filePath)
            self.keym.addUploadedFileToKeystore(uploadFileInfo['fileName'], uploadFileInfo['uploadFilePiecesInfo'])
        else:
            raise Exception('Upload with same filename', filePath)

    def downloadAndSaveFileFromBlockchain(self, fileName):
        uploadPiecesInfo = self.keym.getUploadPiecesInfo(fileName)
        filePathToSave = "./"+timestamp() + ' ' + fileName
        try:
            self.blockm.downloadFile(uploadPiecesInfo, filePathToSave)
            return True
        except KeyboardInterrupt as ke:
            raise ke
        except Exception:
            return False

    def echo(self, message):
        return message

def main():
    print(sys.path)

    try:
        _initLogger()
        s = zerorpc.Server(RPC_service())
        s.bind(ADDRESS)
        gevent.signal(signal.SIGINT, s.stop)
        logging.info("Starting RPC service on %s", ADDRESS)
        s.run()
    except Exception as e:
        logging.error(e)


def timestamp():
    ts = time.time()
    return datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')

def _initLogger():
    logging.getLogger("zerorpc").setLevel(logging.WARNING)
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)

    root = logging.getLogger()
    root.setLevel(LOG_LEVEL)

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter(LOG_FORMAT)
    handler.setFormatter(formatter)
    root.addHandler(handler)

if __name__ == '__main__':
    main()
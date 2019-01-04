import zerorpc
import logging
from src import blockchain_interaction as BlIn
import sys
import os.path
import datetime
import pickle
import time

NODE = "https://testnode1.wavesnodes.com"
ADDRESS = "tcp://127.0.0.1:4242"
LOG_FORMAT = '%(levelname)s:\t%(asctime)-15s %(message)s'
LOG_LEVEL = logging.DEBUG

class RPC_service(object):
    blockm = None
    keym = None

    def signIn(self, seed):
        self.bm = BlIn.BlockChainMaster(NODE, seed)

        data = {
            "address": self.bm.Account.address
        }
        return data

    def pushFileToBlockchain(self, filePath):
        uploadInfo = self.bm.uploadFile(filePath)

        fileName = os.path.basename(filePath)

        logging.info("Upload %s: %s pieces, fee %s",
                     fileName, len(uploadInfo), sum(map(lambda x: x['fee'], uploadInfo)))
        data = {
            'fileName': fileName,
            'uploadInfo': uploadInfo
        }

        pickle_out = open(timestamp(), "wb")
        pickle.dump(data, pickle_out)
        pickle_out.close()

        return data

    def downloadAndSaveFileFromBlockchain(self, keystorePath):
        try:
            keystore = open(keystorePath, "rb")
            data = pickle.load(keystore)
            keystore.close()

            with open(timestamp()+' '+data['fileName'], 'wb') as f:
                for tx in data['uploadInfo']:
                    filePiece = self.bm.downloadFile(tx['id'], tx['key'])
                    f.write(filePiece)
            return True
        except KeyboardInterrupt:
            return
        except:
            return False

    def echo(self, message):
        return message

def main():
    _initLogger()

    s = zerorpc.Server(RPC_service())
    try:
        s.bind(ADDRESS)
        logging.info("Starting RPC service on %s", ADDRESS)
        s.run()
    except KeyboardInterrupt:
        logging.info('Keyboard interrupt received, shutting down the service')
        s.close()

def timestamp():
    ts = time.time()
    return datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')

def _initLogger():
    logging.getLogger("zerorpc").setLevel(logging.WARNING)

    root = logging.getLogger()
    root.setLevel(LOG_LEVEL)

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter(LOG_FORMAT)
    handler.setFormatter(formatter)
    root.addHandler(handler)

if __name__ == '__main__':
    main()
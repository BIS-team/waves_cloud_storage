import pywaves
import hashlib
import base64
import encryption as encryption
import logging

KB_VAL = 16000

class BlockChainMaster:
    Account = None

    def __init__(self, Node_, Seed_):
        self.Node = Node_
        logging.info("Using node %s", Node_)
        self.Seed = Seed_
        logging.info("The given seed: %s", Seed_)
        self._initBlockChainComps()

    def uploadFile(self, filePath):
        with open(filePath, "rb") as file:
            bytes = file.read()

            logging.debug("File to upload: %s\tActual file: %s...\tType: %s\tLength: %s",
                          filePath, (lambda b: b[0:] if len(b) < 32 else b[0:32])(bytes), type(bytes), len(bytes))

            return self.uploadFileBytes(bytes)

    def uploadFileBytes(self, file_bytes):
        it = 0
        k = 0

        uploadFileInfo = []

        while it < len(file_bytes):
            if it+KB_VAL > len(file_bytes):
                file_bytes_slice = file_bytes[it:]
            else:
                file_bytes_slice = file_bytes[it:it + KB_VAL]

            it += KB_VAL

            uploadPieceInfo = self.uploadSizedPiece(file_bytes_slice)
            uploadPieceInfo['position'] = k

            uploadFileInfo.append(uploadPieceInfo)

            k += 1
        return uploadFileInfo

    def uploadSizedPiece(self, file_bytes_slice):
        logging.debug("Actual piece: %s...\tType: %s\tLength: %s",
                      (lambda b: b[0:] if len(b) < 32 else b[0:32])(file_bytes_slice), type(file_bytes_slice), len(file_bytes_slice))

        # generating hash
        hexDig = self._generateHexDig(file_bytes_slice)

        # encrypting data
        encryption_key = encryption.generateKey()
        encrypted_bytes = encryption.getEncryptedData(file_bytes_slice, encryption_key)
        encrypted_str = encrypted_bytes.decode('ASCII')

        logging.debug("Encrypted: %s...\tType: %s\tLength: %s",
                      (lambda b: b[0:] if len(b) < 32 else b[0:32])(encrypted_str), type(encrypted_str), len(encrypted_str))

        data = [{
            'type': 'binary',
            'key': hexDig,
            'value': encrypted_str
        }]
        txInfo = self.Account.dataTransaction(data)

        uploadInfo = {
            'id': txInfo['id'],
            'key': encryption_key,
            'fee': txInfo['fee']
        }
        return uploadInfo

    def downloadFile(self, transactionId, encryptionKey):
        b64_data_str = self._getDataByTxID(transactionId)
        b64_data_bytes = bytes(b64_data_str, 'ASCII')

        data_bytes = base64.b64decode(b64_data_bytes)

        decoded_data = encryption.getDecryptedData(data_bytes, encryptionKey)

        return decoded_data

    def _initBlockChainComps(self):
        pywaves.setNode(node=self.Node, chain='testnet')
        self.Account = pywaves.Address(seed=self.Seed)

    def _getDataByTxID(self, transactionId):
        dataTransJson = pywaves.tx(transactionId)

        b64_data_with_prefix = dataTransJson['data'][0]['value']

        b64_data = b64_data_with_prefix[7:]

        logging.debug("Data from txid - %s: %s", transactionId, b64_data)

        return b64_data

    @staticmethod
    def _generateHexDig(file_bytes):
        hash_object = hashlib.md5(file_bytes)
        hex_dig = hash_object.hexdigest()
        return hex_dig

var zerorpc = require("zerorpc");

var client = new zerorpc.Client();
client.connect("tcp://127.0.0.1:4242");

document.getElementById('signIn').onclick = function(){
  var seed = document.getElementById('seedInputField').value;

  client.invoke("signIn", seed, function(error, res, more) {
      if(error) {
         console.error(error);
      } else {
          doLog(res.address);
      }
  });
};

document.getElementById('uploadToBlockchain').onclick = function(){
  var filePath = document.getElementById('fileToUpload').files[0].path;

  client.invoke("uploadFileToBlockchain", filePath, function(error, res, more) {
      //doLog(res.fileName+"\t"+res.uploadInfo.length+" pieces");
  });
};

document.getElementById('downloadFromBlockchain').onclick = function() {
  var fileName = document.getElementById('fileNameToDownload').value;

  client.invoke("downloadAndSaveFileFromBlockchain", fileName, function(error, res, more) {
        doLog(res)
  });
}

document.getElementById('getUploadHistory').onclick = function() {
  client.invoke("getUploadHistory", function(error, res, more) {
    uploadHistoryTA = document.getElementById('uploadHistoryTextArea')
    uploadHistoryTA.rows = res.length
    uploadHistoryTA.value = res.join('\n')
  });
}

function doLog(message) {
   console.log(new Date().getTime()+":\t"+message);
}

var zerorpc = require("zerorpc");

var client = new zerorpc.Client();
client.connect("tcp://127.0.0.1:4242");

document.getElementById('signIn').onclick = function(){
  var seed = document.getElementById('seedInputField').value;

  client.invoke("signIn", seed, function(error, res, more) {
      doLog(res.address);
  });
};

document.getElementById('uploadToBlockchain').onclick = function(){
  var filePath = document.getElementById('fileToUpload').files[0].path;

  client.invoke("pushFileToBlockchain", filePath, function(error, res, more) {
      doLog(res.fileName+"\t"+res.uploadInfo.length+" pieces");
  });
};
document.getElementById('downloadFromBlockchain').onclick = function() {
  var keystoreFilepath = document.getElementById('keystoreFile').files[0].path;

  client.invoke("downloadAndSaveFileFromBlockchain", keystoreFilepath, function(error, res, more) {
      doLog(res)
  });
}

function doLog(message) {
   console.log(new Date().getTime()+":\t"+message);
}

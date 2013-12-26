function redirectToHome() {
  window.location.href = '/';
}

function updateProgress(savID, progressInterval) {
  console.log("Update bar start!");
  var progressBar = document.getElementById('processing-progress');
  var percentComplete = 0;

  $.ajax({
    url: "/api/savfiles/" + savID,
    type: "GET",
    dataType: "json",
    timeout: progressInterval,
    success: function(data) {
      percentComplete = data.percent_complete;
      progressBar.setAttribute('aria-valuenow', percentComplete);
      progressBar.setAttribute('style', 'width: ' + percentComplete + '%');
    },
    error: function(err) {
      console.log(err);
    },
    complete: function() {
      if (percentComplete == 100) {
        setTimeout(redirectToHome, 5000);
      } else {
        setTimeout(function() { updateProgress(savID, progressInterval) },
                   progressInterval);
      }
    }
  });
}

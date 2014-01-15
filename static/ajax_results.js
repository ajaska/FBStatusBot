var timeout = 4000;
function getProgress(uid) {
	$.ajaxSetup({cache:false});
	$.ajax({
		dataType: "json",
		url:"/get-chat-line/"+uid,
		success: function (msg, data) {
			$("#log").append("<p>"+msg['message']+"</p>");
			setTimeout(function(){getProgress(uid)},timeout);
		}
   });
}

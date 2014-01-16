var timeout = 4000;
function getProgress(uid) {
	$.ajaxSetup({cache:false});
	$.ajax({
		dataType: "json",
		url:"/get-chat-line/"+uid,
		success: function (msg, data) {
			$("#log").append("<p>"+msg['message']+"</p>");
			setTimeout(function(){getProgress(uid)},timeout);
		},
		error: function (jqXHR, errorStatus, errorThrown) {
			$("#log").append("<span class='error'>An error occured, the server may be overloaded or down. Try refreshing the page.</span>");
		}
   });
}

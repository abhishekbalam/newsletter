var robot = false;

var captcha = function (res) {
	robot = true;
	$('#submit').removeAttr('disabled');
}

var reset = function () {
	console.log("reseting");
	robot = false;
	$('#submit').attr('disabled','disabled');
}	

$( document ).ready(function() {
	$('#submit').attr('disabled','disabled');

	$('#submit').on('click', function(event) {
		console.log("click");
    });
	
});

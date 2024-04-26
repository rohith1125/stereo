/*
	Twenty by HTML5 UP
	html5up.net | @ajlkn
	Free for personal and commercial use under the CCA 3.0 license (html5up.net/license)
*/

(function ($) {

	var $window = $(window),
		$body = $('body'),
		$header = $('#header'),
		$banner = $('#banner');

	// Breakpoints.
	breakpoints({
		wide: ['1281px', '1680px'],
		normal: ['981px', '1280px'],
		narrow: ['841px', '980px'],
		narrower: ['737px', '840px'],
		mobile: [null, '736px']
	});

	// Play initial animations on page load.
	$window.on('load', function () {
		window.setTimeout(function () {
			$body.removeClass('is-preload');
		}, 100);
	});

	// Scrolly.
	$('.scrolly').scrolly({
		speed: 1000,
		offset: function () { return $header.height() + 10; }
	});

	// Dropdowns.
	$('#nav > ul').dropotron({
		mode: 'fade',
		noOpenerFade: true,
		expandMode: (browser.mobile ? 'click' : 'hover')
	});

	// Nav Panel.

	// Button.
	$(
		'<div id="navButton">' +
		'<a href="#navPanel" class="toggle" aria-label="navPanel"></a>' +
		'</div>'
	)
		.appendTo($body);

	// Panel.
	$(
		'<div id="navPanel">' +
		'<nav>' +
		$('#nav').navList() +
		'</nav>' +
		'</div>'
	)
		.appendTo($body)
		.panel({
			delay: 500,
			hideOnClick: true,
			hideOnSwipe: true,
			resetScroll: true,
			resetForms: true,
			side: 'left',
			target: $body,
			visibleClass: 'navPanel-visible'
		});

	// Fix: Remove navPanel transitions on WP<10 (poor/buggy performance).
	if (browser.os == 'wp' && browser.osVersion < 10)
		$('#navButton, #navPanel, #page-wrapper')
			.css('transition', 'none');

	// Header.
	if (!browser.mobile
		&& $header.hasClass('alt')
		&& $banner.length > 0) {

		$window.on('load', function () {

			$banner.scrollex({
				bottom: $header.outerHeight(),
				terminate: function () { $header.removeClass('alt'); },
				enter: function () { $header.addClass('alt reveal'); },
				leave: function () { $header.removeClass('alt'); }
			});

		});

	}

})(jQuery);

function validateForm() {
	const fileInput = document.getElementById("file");
	const selectedFile = fileInput.files[0];

	if (!selectedFile) {
		alert("No file selected.");
		return false;
	}

	// Check file type (extension)
	const allowedExtensions = ['jpg', 'zip', 'png'];
	const fileExtension = selectedFile.name.split('.').pop().toLowerCase();
	if (!allowedExtensions.includes(fileExtension)) {
		document.getElementById("error").innerHTML = "Invalid file type. Allowed types: " + allowedExtensions.join(", ");
		event.preventDefault();
		return false;
	}

	// Check file size
	const maxSizeInBytes = 25 * 1024 * 1024; // 25MB
	if (selectedFile.size > maxSizeInBytes) {
		document.getElementById("error").innerHTML = "File size exceeds the allowed limit (25MB).";
		event.preventDefault();
		return false;
	}

	if (fileExtension == 'zip') {
		document.getElementById("error").innerHTML = "Processing... (This could take a while depending on how many images)";
	}
	else {
		document.getElementById("error").innerHTML = "Processing...";
	}

	return true
}
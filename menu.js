$( document ).ready( function() {
	//set language by parameter
	var uselang = getURLParameter('uselang');
	if ( uselang ) {
		switchLanguage( uselang );
	}

	//set language through uls
	$( '.uls-trigger' ).uls( {
		onSelect : function( language ) {
			switchLanguage( language );
		},
		quickList: ['en', 'de', 'es', 'fr', 'ru', 'ja', 'ko', 'sv']
	} );
} );

//all of the needed language changes
function switchLanguage( language ) {
	$.qLabel.switchLanguage( language );
	console.log( 'Selected: ' + language + ' (' +
					$.uls.data.getDir(language) +
				 ')' );
	$( '.content' ).css( 'direction', $.uls.data.getDir( language ) );
	if ( $.uls.data.getDir( language ) == 'rtl' ) {
		$( '.content' ).css( 'text-align', 'right' );
	}
	else {
		$( '.content' ).css( 'text-align', 'left' );
	}
}

//returns the named url parameter
function getURLParameter(param) {
    var pageURL = decodeURIComponent(window.location.search.substring(1));
    var urlVariables = pageURL.split('&');
    for (var i = 0; i < urlVariables.length; i++) {
        var parameterName = urlVariables[i].split('=');
        if (parameterName[0] == param) {
            return parameterName[1];
        }
    }
}

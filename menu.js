$( document ).ready( function() {
	$( '.uls-trigger' ).uls( {
		onSelect : function( language ) {
			$.qLabel.switchLanguage( language );
			console.log( 'Selected: ' + language + ' (' +
							$.uls.data.getDir(language) +
						 ')' );
			$( '.content' ).css( 'direction', $.uls.data.getDir( language ) );
		},
		quickList: ['en', 'de', 'es', 'fr', 'ru', 'ja', 'ko', 'sv']
	} );
} );

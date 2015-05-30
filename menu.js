var langCode = 'sv';

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

	//load langQ json
	var langQ = {
	    'sv' : 'Q1123',
	    'fr' : 'Q150'
	};

	//trigger baloon on clicking any qlabel
	//would be much nicer to use jquery.mobile popup but it's unclear
	//how to have popup trigger lookup with right Q-val
	$.balloon.defaults.classname = "my-balloon";
	$('.qlabel').on("click", function() {
	    if($(this).hasClass('selected')) {
		$(this).hideBalloon();
		$(this).removeClass('selected');
	    } else {
		$(this).addClass('selected');
		entity = $(this).attr('its-ta-ident-ref').split('/entity/')[1];
		$(this).showBalloon({
		    position: null,
		    contents: 'This has qNo ' +
			      entity +
			      ' <div class="property-P18" ></div>' +
			      ' <div class="property-P443" ></div>'
		});
		getClaims( entity, 'P18', null, null );
		getClaims( entity, 'P443', 'P407', langQ[langCode] );
	    }
	    // close also if you click the balloon (closes them all though)
	    $('.my-balloon').on("click", function() {
		$('.selected').hideBalloon();
		$('.selected').removeClass('selected');
	    });
	});
} );

/**
 * request the claims for a specific entity for a specific property
 * (value must be of type string)
 * if a qualifier is not null then only claims where the qualifier is
 * present and has the value qualifierValue (must be of type wikibase-entityid)
 * are used
 */
function getClaims( entity, property, qualifier, qualifierValue ) {
    return $.getJSON('https://www.wikidata.org/w/api.php?callback=?', {
	action: 'wbgetclaims',
	entity: entity,
	property: property,
	format: 'json'
    }, function(data) {
	// TODO handle errors and exceptions
	$.each(data.claims[property], function(index, claim) {
	    if ( qualifier === null ){
		setClaim(property, claim.mainsnak.datavalue.value);
		return false;
	    }
	    else if ( qualifierValue === null ){  //no language match at all
		return false;
	    }
	    else if ( claim.qualifiers && qualifier in claim.qualifiers ) {
		console.log(qualifierValue.slice(1) + ' == ' +
		    claim.qualifiers[qualifier][0].datavalue.value['numeric-id']+
		    ' ?');
		if ( qualifierValue.slice(1) == claim.qualifiers[qualifier][0].datavalue.value['numeric-id'] ) {
		    setClaim(property, claim.mainsnak.datavalue.value);
		    return false;
		}
	    }
	});
    });
}

//sets the value of a given property in a popup
function setClaim(property, value) {
    console.log(property + ', ' + value);
    $('.property-'+property).text(value);
}

//all of the needed language changes
function switchLanguage( language ) {
    langCode = language;
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

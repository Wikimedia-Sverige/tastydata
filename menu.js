var langCode = 'sv';
var dataContent = '';
var popped = false;
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

	//trigger lookup on popover event
	$("[data-toggle='popover']").on('click', function(){
	    if ( popped ) {
		$(this).popover('toggle');
		popped = false;
		return false;  // should prevent kill trigger?
	    }
	    else {
		console.log(dataContent);
		var $triggerElement = $(this);
		var entity = $(this).children().attr('its-ta-ident-ref').split('/entity/')[1];
		dataContent = 'This has qNo ' + entity + 'Image: <property-P18>, Sound: <property-P443>';
		var jqxhrP18 = getClaims( entity, 'P18', null, null );
		var jqxhrP443 = getClaims( entity, 'P443', 'P407', langQ[langCode] );
    
		$.when(jqxhrP18, jqxhrP443).done(function() {
		    console.log(dataContent);
		    console.log($triggerElement.attr('data-content'));
		    $triggerElement.attr('data-content', dataContent);
		    popped = true;
		    $triggerElement.popover('toggle');
		});
	    }
	});
	// Kill also if you clicked anywhere else
	$(document).on('click', function(){
	    if ( popped ) {
		$("[data-toggle='popover']").popover('destroy');
		popped = false;
	    }
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
	if (typeof data.claims[property] === "undefined") {
	    // No hits for that property
	    return false;
	}
	$.each(data.claims[property], function(index, claim) {
	    if ( qualifier === null ){
		setClaim(property, claim.mainsnak.datavalue.value);
		return false;
	    }
	    else if ( qualifierValue === null || typeof qualifierValue === "undefined" ){
		// no language match at all
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
    dataContent = dataContent.replace('<property-'+property+'>',value);
}

//all of the needed language changes
function switchLanguage( language ) {
    langCode = language;
    $.qLabel.switchLanguage( language );
    console.log( 'Selected: ' + language + ' (' +
				    $.uls.data.getDir(language) +
			     ')' );
    $( '.row' ).css( 'direction', $.uls.data.getDir( language ) );
    if ( $.uls.data.getDir( language ) == 'rtl' ) {
	    $( '.row' ).css( 'text-align', 'right' );
    }
    else {
	    $( '.row' ).css( 'text-align', 'left' );
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

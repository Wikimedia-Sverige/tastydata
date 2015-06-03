var langCode = 'sv';
var dataContent = '';
var defaultContent = 'Sorry we couldn\'t find any images or pronunciations';
var langQ = '';
var popped = false;
var clicksound = '';
var thumbWidth = '300';  // remember to adapt .thumb and .popover in main.css
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
		quickList: ['en', 'de', 'es', 'fr', 'ru', 'ja', 'he', 'sv']
	} );

	//load langQ json
	var jqxhrLangQ = $.getJSON("./code2langQ.json", function( data ) {
	    langQ = data;
	});

	//trigger lookup on popover event
	//and close again if clicking anywhere except images inside the popup
	$("[data-toggle='popover']").on('click', function(event){
	    event.stopPropagation();
	    console.log('popoverTrigger-click');
	    if ( popped ) {
		//$(this).popover('toggle');
		$("[data-toggle='popover']").popover('destroy');
		popped = false;
		console.log('popoverTrigger-click-close');
		return false;  // should prevent kill trigger?
	    }
	    else {
		var $triggerElement = $(this);
		var entity = $(this).children().attr('its-ta-ident-ref').split('/entity/')[1];
		dataContent = '<property-P18><property-P443>';
		var jqxhrP18 = getClaims( entity, 'P18', null, null );
		var jqxhrP443 = getClaims( entity, 'P443', 'P407', langQ[langCode] );

		$.when(jqxhrP18, jqxhrP443).done(function() {
		    // if no hits then appologise
		    if ( dataContent === '<property-P18><property-P443>') {
			dataContent = defaultContent;
		    }
		    $triggerElement.attr('data-content', dataContent);
		    popped = true;
		    $triggerElement.popover('toggle');
		    
		    $('[data-toggle=popover]').on('shown.bs.popover', function () {
			$activePopover = $triggerElement.siblings('.popover').eq(0);
			console.log($activePopover.is_on_screen());
			//$('.popover').css('top',parseInt($('.popover').css('top')) + 22 + 'px')
		    });
		});
	    }
	});
	// Kill also if you clicked anywhere else
	$('body').on('click', function(event){
	    console.log('anywhere-click');
	    if ( popped ) {
		if ( !$(event.target).is('img.popoverImg') ) {
		    $("[data-toggle='popover']").popover('destroy');
		    popped = false;
		    console.log('anywhere-click-close');
		}
	    }
	});
} );

/**
 * request the claims for a specific entity for a specific property
 * (value must be of type string)
 * if a qualifier is not null then only claims where the qualifier is
 * present and has one of the value qualifierValues (must be of type
 * wikibase-entityid) are used
 */
function getClaims( entity, property, qualifier, qualifierValues ) {
    console.log('prop: ' + property +', qual: '+qualifier+', qualValues: '+qualifierValues);
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
	    else if ( qualifierValues === null || typeof qualifierValues === "undefined" ){
		// no language match at all
		console.log('no language match at all');
		return false;
	    }
	    else if ( claim.qualifiers && qualifier in claim.qualifiers ) {
		var qVal = 'Q' + claim.qualifiers[qualifier][0].datavalue.value['numeric-id'];
		if ( $.inArray(qVal, qualifierValues)!==-1 ) {
		    setClaim(property, claim.mainsnak.datavalue.value);
		    return false;
		}
	    }
	});
    });
}

//sets the value of a given property in a popup
function setClaim(property, value) {
    if ( property == 'P18' ) {
	descrUrl = 'https://commons.wikimedia.org/wiki/File:' +
		    value.replace(' ', '_');
	dataContent = dataContent.replace(
	    '<property-' + property + '>',
	    '<div class="thumbDiv">' +
		'<a href="' + descrUrl + '">' +
		    '<img class="popoverImg thumb" src="https://commons.wikimedia.org/w/thumb.php' +
			'?width=' + thumbWidth +
			'&f=' + value + '">' +
		'</a>' +
	    '</div>'
	);
    }
    else if ( property == 'P443' ){
	contentUrl = 'https://commons.wikimedia.org/wiki/Special:Redirect/file?wptype=file&wpvalue=' +
		      value.replace(' ', '+');
	descrUrl = 'https://commons.wikimedia.org/wiki/File:' +
		    value.replace(' ', '_');
	clicksound = createsoundbite(contentUrl);
	dataContent = dataContent.replace(
	    '<property-' + property + '>',
	    '<div class="soundDiv">' +
		'<a href="#" onclick="clicksound.playclip()">' +
		    '<img class="popoverImg" src="https://upload.wikimedia.org/wikipedia/commons/thumb/8/87/Gnome-mime-sound-openclipart.svg/50px-Gnome-mime-sound-openclipart.svg.png">' +
		'</a><br />' +
		'<center><a href="' + descrUrl + '">' +
		    '<img class="popoverImg infoIcon" src="https://upload.wikimedia.org/wikipedia/commons/thumb/5/5a/Info_Simple_bw.svg/20px-Info_Simple_bw.svg.png">' +
		'</a></center>' +
	    '</div>'
	);
    }
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

// Mouseover/ Click sound effect- by JavaScript Kit (www.javascriptkit.com)
// Visit JavaScript Kit at http://www.javascriptkit.com/ for full source code

//** Usage: Instantiate script by calling: var uniquevar=createsoundbite("soundfile1", "fallbackfile2", "fallebacksound3", etc)
//** Call: uniquevar.playclip() to play sound

var html5_audiotypes={ //define list of audio file extensions and their associated audio types. Add to it if your specified audio file isn't on this list:
    "mp3": "audio/mpeg",
    "mp4": "audio/mp4",
    "ogg": "audio/ogg",
    "wav": "audio/wav"
};

function createsoundbite(sound){
    var html5audio = document.createElement('audio');
    if (html5audio.canPlayType){ //check support for HTML5 audio
	for (var i=0; i<arguments.length; i++) {
	    var sourceel = document.createElement('source');
	    sourceel.setAttribute('src', arguments[i]);
	    if (arguments[i].match(/\.(\w+)$/i)) {
		sourceel.setAttribute('type', html5_audiotypes[RegExp.$1]);
	    }
	    html5audio.appendChild(sourceel);
	}
	html5audio.load();
	html5audio.playclip = function(){
	    html5audio.pause();
	    html5audio.currentTime=0;
	    html5audio.play();
	};
	return html5audio;
    }
    else {
	return {
	    playclip: function(){
		throw new Error("Your browser doesn't support HTML5 audio unfortunately");
	    }
	};
    }
    
}

$.fn.is_on_screen = function(){
    var win = $(window);
    var viewport = {
	top : win.scrollTop(),
	left : win.scrollLeft()
    };
    viewport.right = viewport.left + win.width();
    viewport.bottom = viewport.top + win.height();
 
    var bounds = this.offset();
    bounds.right = bounds.left + $('.popoverImg.thumb').clientWidth();
    bounds.bottom = bounds.top + $('.popoverImg.thumb').clientHeight();
    console.log(viewport);
    console.log(bounds);
    console.log($('.popoverImg.thumb').clientWidth(), $('.popoverImg.thumb').clientHeight());
 
    return (!(viewport.right < bounds.left || viewport.left > bounds.right || viewport.bottom < bounds.top || viewport.top > bounds.bottom));
};

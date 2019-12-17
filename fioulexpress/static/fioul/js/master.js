// Common
var utils = {};
utils.init = function() {
    utils.currentStep = utils.getStep();

    $(window).on('resize', function() {
        utils.currentStep = utils.getStep();
    });
};
utils.getStep = function() {
    var step = window.getComputedStyle(document.body, ":after").getPropertyValue("content");
    step = parseInt(step.replace(/'/g, "").replace(/"/g, ""));
    return step;
};



function getCookie(cname) {
    var name = cname + "=";
    var ca = document.cookie.split(';');
    for(var i = 0; i <ca.length; i++) {
        var c = ca[i];
        while (c.charAt(0)==' ') {
            c = c.substring(1);
        }
        if (c.indexOf(name) == 0) {
            return c.substring(name.length,c.length);
        }
    }
    return "";
} 



// Menu
var menu = {};
menu.init = function() {
    menu.$el = $('.header-menu');
    menu.$trigger = $('.header-menu-open-hamburger');

    menu.$trigger.on('click', function() {
        menu.$el.slideToggle();
    });
};

var sliderOccuped = false;
// Range slider (Checkout - Devis)
if (window.page === 'devis') {
    var checkoutSlider = document.getElementById('slider');

    noUiSlider.create(checkoutSlider, {
        start: [ 1000 ],
        step: 50,
        range: {
            'min': [ 500 ],
            'max': [ 10000 ]
        }
    });
    var checkoutInput = document.getElementById('qte');

    checkoutSlider.noUiSlider.on('update', function( values, handle ) {
        checkoutInput.value = Math.floor(values[handle]);
        if (!sliderOccuped) {
        	
        }
    });
    slider.noUiSlider.on('change', function(){
    	client_commande_devis_valoriser();
    });
    slider.noUiSlider.on('end', function(){
    	client_commande_devis_valoriser();
    });

    /*
     * 

    slider.noUiSlider.on('start', function(){
    	sliderOccuped = true;
    	console.log('slider start ' + zone_active);
    });
    
    checkoutSlider.addEventListener('mouseup', function( values, handle ) {
        $('#qte').change();
    });
    checkoutSlider.addEventListener('blur', function( values, handle ) {
        $('#qte').change();
    });
    */

    checkoutInput.addEventListener('input', function() {
    	if (this.value > 499) {
    		checkoutSlider.noUiSlider.set(this.value);
    		client_commande_devis_valoriser();
    	}
        
    });
    checkoutInput.addEventListener('keyup', function() {
    	if (this.value > 499) {
    		checkoutSlider.noUiSlider.set(this.value);
    		client_commande_devis_valoriser();
    	}
    });

}



/* Commande client */

function client_commande_maj_devis(data_panier){
	var xhr = new XMLHttpRequest();
    xhr.onreadystatechange = function(){
    	if (xhr.readyState == 4 && xhr.status == 200) {
    		var data_devis = JSON.parse(xhr.responseText);
            document.getElementById('commande-total').innerHTML = data_devis['total_ttc'];
            document.getElementById('commande-total-ht').innerHTML = data_devis['total_ht'];
            document.getElementById('commande-prix-litre').innerHTML = data_devis['prix_litre'];
            //document.getElementById('commande-livraison-prix').innerHTML = data_devis['livraison_prix'];
            document.getElementById('commande-fioul').innerHTML = data_devis['fioul_nom'];
            document.getElementById('commande-livraison').innerHTML = data_devis['livraison_nom'];
            document.getElementById('commande-qte').innerHTML = document.getElementById('qte').value;
            for (liv in data_devis['livraisons']){
            	//alert(liv + " - " + data_devis['livraisons'][liv]);
            	document.getElementById('commande-prix-livraison-' + liv).innerHTML = data_devis['livraisons'][liv];
            }
            document.getElementById('commande-livraison-date').innerHTML = document.getElementById('commande-livraison-date-' + data_panier['type_livraison']).innerHTML;
    	}
    };
    xhr.open('post', '/commande/valoriser/');
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.setRequestHeader('X-CSRFToken', getCookie('csrftoken'));
    xhr.send(JSON.stringify(data_panier));
}

var qte_save = 0;
var type_fioul_save = 0;
var type_livraison_save = 0;
function client_commande_devis_valoriser() {
	var qte = parseFloat(document.getElementById('qte').value);
	/*
	if (qte >= 500) {
		var reste = qte % 50;
		if (reste < 25) {
			qte = qte - reste
		} else {
			qte = qte + (50 - reste);
		}
	} else {
		return;
	}
	if (parseFloat(document.getElementById('qte').value) != qte) {
		document.getElementById('qte').value = qte;
	}
	*/
	form_panier = document.getElementById('form-panier');
    var type_fioul, type_livraison;
    $('[name=type_fioul]').each(function(index, field){
        if (field.checked) {
            type_fioul = field.value;
        }
    });
    $('[name=type_livraison]').each(function(index, field){
        if (field.checked) {
        	type_livraison = field.value;
        }
    });
	var data_panier = {
		qte: document.getElementById('qte').value,
        type_fioul: type_fioul,
        type_livraison: type_livraison,
        zone: zone_active
	}
	if (qte_save != qte || type_fioul_save != type_fioul || type_livraison_save != type_livraison){
		client_commande_maj_devis(data_panier);
		qte_save = qte;
		type_fioul_save = type_fioul;
		type_livraison_save = type_livraison;
	}
	
}



$(document).ready(function() {
    utils.init();
    menu.init();

    $('.popin').popin();
    $('.field').field();

    if ($('#messages').length > 0) $('#messages').data('popin').open();

    if (window.page === 'paiement') {
        var $depositContainer = $('.your-deposit-container'),
            $moneticoContainer = $('#commande-monetico-container');

        $('#yourDepositCgvCheckbox').on('change', function() {
            if ($(this).is(':checked')) {
                $depositContainer.addClass('opened');
                $moneticoContainer.slideDown();
            } else {
                $moneticoContainer.slideUp(400, function() {
                    $depositContainer.removeClass('opened');
                });
            }
        });
    }

    //fix for label on connexion page
    if (window.page === 'connexion') {
        $('#client-connexion-email, #client-connexion-password').on('input', function() {
            $('#client-connexion-email').parent().data('field').check();
            $('#client-connexion-password').parent().data('field').check();
        });
    }
});
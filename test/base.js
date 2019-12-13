//var casper = require('casper').create();
var utils = require('utils');

var base_url = casper.cli.get('base_url', 'http://localhost:8000');


casper.test.begin('HP et page de contenu', 2, function suite(test) {

	casper.start(base_url + "/"
	).then(function() {
	    test.assertTitle('Fioul Express');
	}).thenClick('nav.header-menu li.header-menu-item:last-child a', function() {
	    test.assertTitle('Fioul Express - Qui sommes nous');
	});
	
	casper.run(function() {
	    test.done();
	});

});

casper.test.begin('Commande', 4, function suite(test) {

	casper.start(base_url + "/"
	).then(function() {
	    this.fill('form#form-hp-cp',{'cp' : '75002'});
	    //var url_quisommesnous = this.getElementAttribute('nav.header-menu li.header-menu-item:last-child a', 'href');
	}).thenClick('form#form-hp-cp .hp-layer-btn', function() {
	    test.assertTitle('Fioul Express - Devis'); //
	}).wait(200, function() {
	    test.assert(this.getHTML('#commande-total') == '560', 'Valorisation devis ok');
	}).thenClick('#commande-continue', function() {
		test.assert(this.getHTML('#commande-total') == '560', 'Valorisation livraison ok');
		test.assert(this.getFormValues('form#commande-checkout')['adresse-livraison-detail_4'] == 'Paris 02', 'Ville correspondante au code postal');
		this.fill('form#commande-checkout', {
			'adresse-livraison-prenom' : 'Test prénom',
			'adresse-livraison-nom' : 'Test nom',
			'adresse-livraison-detail_1' : "2 rue de l'Adresse",
			'client-email' : 'casper@test.fr',
			'client-telephone' : '0123456789',
			'commentaire-commentaire' : 'Commentaire livraison'
		});
	}).thenClick('#commande-continue', function() {
		//this.capture('/tmp/aa.png');
	});
	
	casper.run(function() {
	    test.done();
	});

});

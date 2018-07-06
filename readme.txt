Link sajta: https://book-evaluator.herokuapp.com/
Kod: https://github.com/Vukan-Markovic/Book-evaluator

Tema za projekat: Web aplikacija za ocenjivanje, komentarisanje, čitanje i pretragu knjiga sa podržanom autentifikacijom.

Kratak opis aplikacije:

Registrovani korisnici imaju mogućnost ocenjivanja knjiga i njihovo komentarisanje, brisanje i menjanje svojih komentara i ocena,
čitanje pojedinih knjiga kao i kreiranje dnevnika pročitanih knjiga uz mogućnost pretrage. Svaki registrovani korisnik ima svoj profil
sa nekim osnovnim informacijama o njemu i njegovoj aktivnosti na sajtu i mogućnost pregleda profila drugih korisnika.
Neregistrovani mogu da pregledaju knjige, komentare, ocene, profile drugih korisnika i vrše pretragu knjiga bez ostalih mogućnosti.
Administator sajta ima sve mogućnosti registrovanog korisnika i takođe mogućnost brisanja i menjanja ocena i komentara svih korisnika
kao i pregleda svih registrovanih korisnika uz mogućnost njihovog brisanja.

Knjige se dobavljaju putem Google Books API-ja (https://developers.google.com/books/).

Tehnologije:

Za izradu aplikacije su korišćeni:
- Flask web python framework (http://flask.pocoo.org/)
- CS50.io razvojno okruženje (https://cs50.io)
- phpliteadmin baza podataka (https://www.phpliteadmin.org/) i
- heroku servis za hostovanje (https://www.heroku.com/).

Izvori:
- https://www.edx.org/course/cs50s-introduction-computer-science-harvardx-cs50x
- http://ellab.ftn.uns.ac.rs/moodle/course/view.php?id=560
- http://flask.pocoo.org
- https://stackoverflow.com
- https://www.youtube.com/watch?v=4_RYQJfiuVU
- https://bootswatch.com/minty

Insaliranje svih potrebnih paketa za pokretanje u CS50 okruženju izvršiti komandom: pip3 install --user -r requirements.txt.

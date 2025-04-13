# Changelog

## Viikko 3

- Käyttäjä voi luoda käyttäjä tunnuksen ja kirjautua sisään.
- Käyttäjä voi laskea oman pef viitearvon.
- Lisätty PefRepository-luokka, joka tallentaa käyttäjän syöttämät tiedot CVS-tiedostoon.
- Lisätty PefService-luokka, joka vastaa sovelluslogiikka osiosta.
- Testattu että UserRepository-luokka palautta luodun kayttäjän.
- Testattu että pef_repositoryssa pef-viitearvon lasku menee oikein.

## Viikko 4

- Käyttäjä voi laskea yksittäisten pef-arvojen muutoksia.
- Muokattu sovellus ikkunan kokoa, nappejen sijoitusta ja miten käyttäjä suorittaa toimintoja sisään kirjautuneena.
- Testejä muutettu sopimaan paremmin sovelluksen rekenteeseen, testi pef_repositoryssä pef-viitearvon lasku on poistettu.
- Testattu että pef_repositoryossa pef-viitearvon luominen menee oikein.

## Viikko 5

- Käyttäjä voi lisätä pef-seurannan mittauksia sovellukseen.
- Testejä lisätty uuteen pef_monitorin_repository.py tiedostolle ja pef_servises.py tiedostolle.
- Ulkonäkö parannuksia tehty käyttöliittymään, sovellus aukeaa isommassa ikkunassa, ja kirjautuneen näkymän nappien paikkoja ja näkymien avautumista muokattu.

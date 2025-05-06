# Changelog

## Viikko 3

- Käyttäjä voi luoda käyttäjätunnuksen ja kirjautua sisään.
- Käyttäjä voi laskea oman PEF-viitearvonsa.
- Lisätty `PefRepository`-luokka, joka tallentaa käyttäjän syöttämät tiedot CSV-tiedostoon.
- Lisätty `PefService`-luokka, joka vastaa sovelluslogiikasta.
- Testattu, että `UserRepository`-luokka palauttaa luodun käyttäjän.
- Testattu, että `PefRepository`-luokassa PEF-viitearvon lasku toimii oikein.

## Viikko 4

- Käyttäjä voi laskea yksittäisten PEF-arvojen muutoksia.
- Muokattu sovellusikkunan kokoa, nappien sijoittelua ja sitä, miten käyttäjä suorittaa toimintoja kirjautuneena.
- Testejä muokattu sopimaan paremmin sovelluksen rakenteeseen. Testi `PefRepository`-luokan PEF-viitearvon laskusta on poistettu.
- Testattu, että `PefRepository`-luokassa PEF-viitearvon luominen toimii oikein.

## Viikko 5

- Käyttäjä voi lisätä PEF-seurannan mittauksia sovellukseen.
- Testejä lisätty uusiin `pef_monitorin_repository.py`- ja `pef_services.py`-tiedostoihin.
- Ulkonäköparannuksia tehty käyttöliittymään: sovellus aukeaa isommassa ikkunassa ja kirjautuneen näkymän nappien paikkoja sekä näkymien avautumista on muokattu.

## Viikko 6

- Käyttäjä voi täyttää haluamansa pituisen PEF-seurannan, ja kun seuranta on täytetty halutulla pituudella, tulokset saa painamalla "Lopeta".
- Käyttäjä voi aloittaa uuden PEF-seurannan halutessaan. Vanhoja tuloksia voi tarkastella kohdasta "Katso aiemmat seurannat".
- Useampaan syötekenttään on lisätty validointeja estämään virheellisiä syötteitä.
- Käyttäjä voi tarkistaa ohjeista, miten sovellusta tulisi käyttää.

## Viikko 7

- Jos ohjelman käynnistää ilman tietokannan alustamista, siitä tulee virheilmoitus käyttäjälle, kun hän yrittää kirjautua tai luoda käyttäjän.
- Päällekkäin renderöityvät lomakkeet on korjattu.
- Käyttäjänimen pituusvaatimus on lisätty ja myös salasanan pituusvaatimus on määritetty.
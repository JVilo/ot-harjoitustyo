# Ohjelmistotekniikka, harjoitustyö

## Pef-sovellus

sovelluksen avulla käyttäjä voi seurata omia pef-puhallus tuloksia verrattuna viitearvoihin. Useampi rekisteröitynyt käyttäjä voi käyttää sovellusta, sovelluksessa heillä näkyy omat viitearvot ja voi tarkistaa omat mittaukset niihin peilaten.

## Dokumentaatio

- [Vaatimusmäärittely](./dokumentaatio/vaatimusmaarittely.md)
- [Työaikakirjanpito](./dokumentaatio/tuntikirjanpito.md)
- [Changelog](./dokumentaatio/changelog.md)
- [Arkkitehtuurikuvaus](./dokumentaatio/arkkitehtuuri.md)
- [Release](https://github.com/JVilo/ot-harjoitustyo/releases/tag/loppupalautus)
- [Käyttöohje](https://github.com/JVilo/ot-harjoitustyo/blob/main/dokumentaatio/kayttoohje.md)
- [Testausdokumentti](https://github.com/JVilo/ot-harjoitustyo/blob/loppupalautus/dokumentaatio/testaus.md)

## Asennus

1. Asenna tarvittavat riippuvuudet seuraavalla komennolla:

```bash
poetry install
```

2. Suorita tarvittavat alustustoimenpiteet komennolla:

```bash
poetry run invoke build
```

3. Käynnistä sovellus komennolla:

```bash
poetry run invoke start
```

## Komentorivitoiminnot

### Sovelluksen käynnistäminen

Sovelluksen voi käynnistää seuraavalla komennolla:

```bash
poetry run invoke start
```

### Testaus

Testit suoritetaan komennolla:

```bash
poetry run invoke test
```

### Testikattavuus

Testikattavuusraportin voi luoda komennolla:

```bash
poetry run invoke coverage-report
```

Raportti generoituu _htmlcov_-hakemistoon.

### Pylint

Tiedoston [.pylintrc](./.pylintrc) määrittelemät tarkistukset voi suorittaa komennolla:

```bash
poetry run invoke lint
```
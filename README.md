# Ohjelmistotekniikka, harjoitustyö

## Pef-sovellus

sovelluksen avulla käyttäjä voi seurata omia pef-puhallus tuloksia verrattuna viitearvoihin. Useampi rekisteröitynyt käyttäjä voi käyttää sovellusta, sovelluksessa heillä näkyy omat viitearvot ja voi tarkistaa omat mittaukset niihin peilaten.

## Dokumentaatio

- [Vaatimusmäärittely](./dokumentaatio/vaatimusmaarittely.md)
- [Työaikakirjanpito](./dokumentaatio/tuntikirjanpito.md)
- [Changelog](./dokumentaatio/changelog.md)

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

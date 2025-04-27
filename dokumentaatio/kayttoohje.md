# Käyttöohje

Lataa projektin viimeisimmän [releasen](...) lähdekoodi valitsemalla _Assets_-osion alta _Source code_.

## Ohjelman käynnistäminen

Ennen ohjelman käyttöönottamista, asenna tarvittavat riippuvuudet seuraavalla komennolla:

```bash
poetry install
```

Sen jälkeen suorita ohjelman alustaminen komennolla:

```bash
poetry run invoke build
```

Kun alustaminen on valmis, ohjelma voidaan käynnistää komennolla:

```
poetry run invoke start
```

## Kirjautuminen

Sovellus käynnistyy kirjautumisnäkymään:

![img.png](https://github.com/JVilo/ot-harjoitustyo/blob/main/dokumentaatio/kuvat/login.png)

Kirjautuminen tapahtuu syöttämällä olemassa oleva käyttäjätunnus ja salasana syötekenttiin, jonka jälkeen valitaan "Login"-painike.

![img.png](https://github.com/JVilo/ot-harjoitustyo/blob/main/dokumentaatio/kuvat/Login_whit_user.png)

## Uuden käyttäjän luominen

Kirjautumisnäkymästä voi siirtyä uuden käyttäjän rekisteröintinäkymään klikkaamalla "Create user" -painiketta.

Uuden käyttäjän luomiseksi täytä käyttäjätunnus, salasana ja vahvista salasana syötekenttiin, ja paina "Create"-painiketta.

![img.png](https://github.com/JVilo/ot-harjoitustyo/blob/main/dokumentaatio/kuvat/Create_user.png)

Kun käyttäjä on luotu onnistuneesti, siirrytään kirjautumisnäkymään.

## PEF-mittaukset

PEF-toimintojen aloittaminen tapahtuu kirjautumisen jälkeen seuraavasti:

![img.png](https://github.com/JVilo/ot-harjoitustyo/blob/main/dokumentaatio/kuvat/inlogged_view.png)

### PEF-mittauksen syöttäminen pef-seurantaan

- Yksi PEF-mittaus koostuu kolmesta peräkkäisestä puhalluksesta.
- Syötä PEF-arvot ja valitse mittauksen ajankohta (Aamu/Ilta) sekä merkitse, oliko mittaus ennen vai jälkeen lääkityksen.
- Kun olet täyttänyt halutun määrän pef mittauksia voit lopettaa/viimeistellä ppef surannan painamalla "lopeta" nappia.
- Ruudulle aukeaa ikkuna jossa on tehdyn pef seurannan kooste.

![img.png](https://github.com/JVilo/ot-harjoitustyo/blob/main/dokumentaatio/kuvat/pef_seuranta.png)

![img.png](https://github.com/JVilo/ot-harjoitustyo/blob/main/dokumentaatio/kuvat/pef_tulos.png)

### PEF-viitearvon laskeminen

Voit laskea PEF-viitearvot syöttämällä pituuden, iän ja sukupuolen ja painamalla "Näytä/Peitä PEF-viite"-painiketta.

![img.png](https://github.com/JVilo/ot-harjoitustyo/blob/main/dokumentaatio/kuvat/pef_viitearvo.png)

Laskennan jälkeen viitearvot näkyvät sovelluksen vasemmalla puolella vertailua varten.

### PEF-vertailut

Voit verrata yksittäisiä PEF-arvojasi eri mittauksista valitsemalla vertailunäkymän. Täällä voit tarkastella vuorokausivaihtelua ja bronkodilataatiovastetta tai vaan jompaakumpaa.

![img.png](https://github.com/JVilo/ot-harjoitustyo/blob/main/dokumentaatio/kuvat/laske_vertailu.png)

## Aiemmat seurantajakson tulokset

Aiemmat seurantajakson tulokset voidaan tarkastella painamalla "Katso aiemmat seurannat"-painiketta.

Valitse haluamasi jakso nähdäksesi yhteenvedon, joka sisältää yksityiskohtaisen analyysin PEF-arvojen vaihteluista ja lääkityksen vaikutuksesta.

![img.png](https://github.com/JVilo/ot-harjoitustyo/blob/main/dokumentaatio/kuvat/pef_katso_aiemmat.png)

![img.png](https://github.com/JVilo/ot-harjoitustyo/blob/main/dokumentaatio/kuvat/pef_aiemman_raportti.png)

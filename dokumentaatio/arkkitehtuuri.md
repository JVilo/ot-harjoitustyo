# Arkkitehtuurikuvaus

## Rakenne

Ohjelman rakenne noudattaa kolmitasoista kerrosarkkitehtuuria, ja koodin pakkausrakenne on seuraava:

![alt text](./kuvat/pakkaus.png)

Pakkaus ui vastaa käyttöliittymän toteutuksesta, pakkaus services sisältää sovelluslogiikan, ja pakkaus repositories huolehtii tietojen pysyväistallennuksesta. Pakkaus entities sisältää luokat, jotka edustavat sovelluksen käyttämiä tietokohteita.

## Käyttöliittymä

Käyttöliittymässä kolme erillistä näkymää:

- Kirjautuminen
- Uuden käyttäjän luominen
- Pef-toiminnot

Jokainen näkymä on toteutettu omana erillisenä luokkanaan. Vain yksi näkymä on aktiivisena kerrallaan, ja [UI](../src/ui/ui.py)-luokka huolehtii näkymien vaihtamisesta. Käyttöliittymä on täysin erotettu sovelluslogiikasta ja kommunikoi ainoastaan [PefService](../src/services/pef_service.py)-luokan tarjoamien metodien kautta.

Kun käyttäjä suorittaa PEF-toimenpiteen (esim. laskee referenssin tai tekee vertailuja), käyttöliittymä kutsuu PEFService-luokan vastaavia metodeja, kuten [calculate_pef_difference](https://github.com/JVilo/ot-harjoitustyo/blob/d49ccd076caaee7b330dac9481216666182a3d0e/src/services/pef_service.py#L110)ja [count_reference_pef](https://github.com/JVilo/ot-harjoitustyo/blob/d49ccd076caaee7b330dac9481216666182a3d0e/src/services/pef_service.py#L57), jotka huolehtivat PEF-arvojen laskemisesta ja vertaamisesta. Sovelluslogiikka suorittaa laskennan ja vertailun, ja sen jälkeen tulokset palautetaan käyttöliittymään, joka päivittää näkymän.

## Sovelluslogiikka

Sovelluksen loogisen tietorakenteen muodostavat luokat, kuten [User](https://github.com/JVilo/ot-harjoitustyo/blob/main/src/entities/user.py) ja [Pef](https://github.com/JVilo/ot-harjoitustyo/blob/main/src/entities/pef.py), jotka mallintavat käyttäjiä ja heidän PEF-arvojaan:

```mermaid
classDiagram
    User "1" --> "*" Pef
    class User {
        username
        password
    }

    class Pef {
        value
        user
        pef_id
    }
```

Toiminnallisten elementtien hallinnasta vastaa PefService-luokan ainoa olio. Tämä luokka tarjoaa erilliset metodit kaikille käyttöliittymän toiminnoille, kuten:

- `login(username, password)`
- `create_user(username, password, password2)`
- `create_pef(value, user)`
- `get_user_pef()`
- `count_reference_pef(height, age, gender, user)`
- `calculate_pef_differences(morning_before, morning_after, evening_before, evening_after)`
- `create_monitoring_session(username, start_date, end_date)`
- `get_sessions_by_username(username)`
- `def add_value_to_monitoring( date, username,value1, value2, value3, state, time)`
- `_build_monitoring_summary( over_20, over_15,monitored_days_count, highest, lowest, average)`
- `calculate_monitoring_difference_for_session(self, username, start_date, end_date)`

_PefService_ pääsee käsiksi käyttäjätietoihin ja pef-tietoihin pakkauksen repositories osassa olevien luokkien, kuten [PefRepository](https://github.com/JVilo/ot-harjoitustyo/blob/main/src/repositories/pef_repository.py) , [UserRepository](https://github.com/JVilo/ot-harjoitustyo/blob/main/src/repositories/user_repository.py) ja [PefMonitoringRepository](https://github.com/JVilo/ot-harjoitustyo/blob/main/src/repositories/pef_monitorin_repository.py), avulla. Nämä luokat injektoidaan sovelluslogiikkaan konstruktorin kautta.

`PefService`-luokan ja ohjelman muiden osien välinen suhde kuvataan seuraavassa luokka/pakkauskaaviossa:

![Pakkausrakenne ja luokat](./kuvat/Pakkausrakenne_ja_luokat.png)

## Tietojen pysyväistallennus

Pakkauksen **repositories** luokat `PefRepository` ja `UserRepository` huolehtivat tietojen tallentamisesta. `PefRepository`-luokka tallentaa tiedot tietokantaan, kun taas `UserRepository`-luokka käyttää SQLite-tietokantaa käyttäjien tietojen säilyttämiseen.

Nämä luokat noudattavat **Repository**-suunnittelumallia, jonka avulla tiedon tallennustavasta voidaan erottaa sovelluslogiikka. Tämä mahdollistaa tallennusratkaisujen vaihtamisen ilman, että sovelluslogiikkaa tarvitsee muuttaa. Esimerkiksi, jos sovelluksen tallennustapaa päätetään vaihtaa (esim. siirtyminen SQL-tietokannasta NoSQL-ratkaisuun), voidaan repository-luokkien toteutukset helposti vaihtaa uusiin ilman vaikutuksia muuhun sovellukseen.

Sovelluslogiikan testauksessa hyödynnetään tätä abstraktiota siten, että käytetään keskusmuistiin tallentavia repository-toteutuksia sen sijaan, että käytettäisiin oikeaa tiedostotallennusta tai tietokantaa.

### Tiedostot

Sovellus tallettaa käyttäjien ja PEF-arvojen tiedot erillisiin tiedostoihin.

Sovelluksen juureen sijoitettu konfiguraatiotiedosto `.env` määrittelee tiedostojen nimet.

Sovellus tallettaa PEF-arvot CSV-tiedostoon seuraavassa formaatissa:

```
5749b61f-f312-45ef-94a1-71a758feee2b;350.0;martta
65eef813-330a-4714-887b-2bda4d744487;400.7;minna
```

Eli PEF-arvon id (`pef_id`), PEF-arvo (`value`, desimaaliluku) ja käyttäjän käyttäjätunnus (`username`). Kenttien arvot erotellaan puolipisteellä (`;`).

Käyttäjät tallennetaan SQLite-tietokannan tauluun `users`, joka alustetaan [initialize_database.py](https://github.com/JVilo/ot-harjoitustyo/blob/main/src/initialize_database.py)-tiedostossa.

## Päätoiminnallisuudet

Seuraavaksi kuvataan sovelluksen toimintalogiikka muutamien päätoiminnallisuuksien osalta sekvenssikaavion avulla.

### Käyttäjän kirjaantuminen

Kun käyttäjä syöttää käyttäjätunnuksen ja salasanan kirjautumisnäkymän kenttiin ja painaa Login -painiketta, sovelluksen kontrolli etenee seuraavasti:

```mermaid
sequenceDiagram
  actor Eva
  participant UI
  participant PefService
  participant UserRepository
  Eva->>+UI: click "Login" button
  UI->>+PefService: login("eva", "eva321")
  PefService->>+UserRepository: find_by_username("eva")
  UserRepository-->>-PefService: user
  PefService-->>-UI: user
```

Kun käyttäjä painaa kirjautumispainiketta, [tapahtumankäsittelijä](https://github.com/JVilo/ot-harjoitustyo/blob/main/src/ui/login_view.py) kutsuu sovelluslogiikan PefService-luokan metodia [login](https://github.com/JVilo/ot-harjoitustyo/blob/d49ccd076caaee7b330dac9481216666182a3d0e/src/services/pef_service.py#L79) ja antaa sille käyttäjätunnuksen ja salasanan parametreina. Sovelluslogiikka käyttää `UserRepository`:a tarkistaakseen, onko kyseinen käyttäjätunnus olemassa. Jos tunnus löytyy, verrataan salasanaa tallennettuun arvoon. Mikäli salasanat täsmäävät, kirjautuminen onnistuu. Tämän jälkeen käyttöliittymä siirtyy `PefsView`-näkymään ja näyttää kirjautuneelle käyttäjälle hänen PEF-arvonsa.

### Uuden käyttäjän luominen

Kun uuden käyttäjän luomisnäkymässä on syötetty käyttäjätunnus, joka ei ole jo käytössä sekä salasana, jonka jälkeen klikataan painiketta "Create", etenee sovelluksen kontrolli seuraavasti:

```mermaid
sequenceDiagram
  actor User(eva)
  participant UI
  participant PefService
  participant UserRepository
  participant eva
  User(eva)->>+UI: click "Create user" button
  UI->>+PefService: create_user("eva", "eva321", "eva321")
  PefService->>+UserRepository: find_by_username("eva")
  UserRepository-->>-PefService: None
  PefService->>eva: User("eva", "eva321")
  PefService->>+UserRepository: create("eva")
  UserRepository-->>-PefService: user
  PefService-->>-UI: user
  UI->>UI: show_login_view()
```

[Tapahtumakäsittelijä](https://github.com/JVilo/ot-harjoitustyo/blob/main/src/ui/create_user_view.py) kutsuu sovelluslogiikan [create_user](https://github.com/JVilo/ot-harjoitustyo/blob/d49ccd076caaee7b330dac9481216666182a3d0e/src/services/pef_service.py#L155)-metodia ja välittää siihen uuden käyttäjän tiedot. Sovelluslogiikka tarkistaa `UserRepository`:n avulla, onko annetulla käyttäjätunnuksella jo olemassa olevaa tiliä. Jos käyttäjätunnus ei ole käytössä, luodaan uusi `User`-olio, joka tallennetaan kutsumalla `UserRepository`:n `create`-metodia. Tämän jälkeen käyttöliittymä vaihtaa näkymäksi `PefsView`:n ja uusi käyttäjä kirjataan automaattisesti sisään.

### Pef-viitearvon laskeminen

Kun käyttäjä valitsee 'Laske PEF-viitearvo' -painikkeen, sovelluksen toiminta etenee seuraavalla tavalla:

```mermaid
sequenceDiagram
  actor User
  participant UI
  participant PefService
  participant PefRepository
  User->>+UI: click "Laske PEF-viitearvo"
  UI->>+PefService: count_reference_pef( height, age, gender)
  PefService->>+PefRepository: create(reference_pef)
  PefRepository-->>-PefService: pef
  PefService-->>-UI: pef
  UI->>UI: update_reference_pef_ui()
```

[Tapahtumakäsittelijä](https://github.com/JVilo/ot-harjoitustyo/blob/main/src/ui/pef_view.py) kutsuu sovelluslogiikan metodia [calculate_pef_reference](https://github.com/JVilo/ot-harjoitustyo/blob/d49ccd076caaee7b330dac9481216666182a3d0e/src/services/pef_service.py#L57), antaen parametreina tarvittavat tiedot (esim. pituus, ikä, sukupuoli) PEF-viitearvon laskemiseksi. Sovelluslogiikka luo uuden `Pef`-olion kutsumalla `PefService`:n `count_reference_pef`-metodia ja tallentaa sen kutsumalla `PefRepository`:n `create`-metodia. Tämän seurauksena käyttöliittymä päivittää näytettävän PEF-viitearvon kutsumalla omaa metodiaan `_update_reference_pef_ui()`.

### Pef-seuranna täyttäminen

Kun käyttäjä painaa **"PEF-seuranta"**-painiketta, käyttöliittymä näyttää mittaustietojen syöttökentät. Käyttäjä syöttää PEF-arvot (aamu/ilta, ennen/jälkeen lääkkeen) ja painaa joko **"Tallenna ja jatka"** tai **"Tallenna ja sulje"** -painiketta.

Tallenna ja jatka

```mermaid
sequenceDiagram
  actor User
  participant UI
  participant PefService
  participant PefMonitoringRepository
  User->>+UI: click "PEF-seuranta"
  UI->>UI: show input fields
  User->>UI: fill fields + click "Tallenna ja jatka"
  UI->>+PefService: add_value_to_monitoring(username, date, values...)
  PefService->>+PefMonitoringRepository: add_value(PefMonitoring)
  PefMonitoringRepository-->>-PefService: OK
  PefService-->>-UI: return
  UI->>+PefService: get_monitoring_by_username()
  PefService->>+PefMonitoringRepository: find_monitoring_by_username(username)
  PefMonitoringRepository-->>PefService: monitoring rows
  PefService->>PefMonitoringRepository: order_by_date(rows)
  PefMonitoringRepository-->>-PefService: ordered rows
  PefService-->>-UI: updated list
  UI->>UI: refresh monitoring view
```

- Jos käyttäjä painaa **"Tallenna ja jatka"**, [tapahtumankäsittelijä](https://github.com/JVilo/ot-harjoitustyo/blob/main/src/ui/pef_view.py) kutsuu sovelluslogiikan [add_value_to_monitoring](https://github.com/JVilo/ot-harjoitustyo/blob/06b2996b4d65a09ae0ea4328759d3530ffddbd76/src/services/pef_service.py#L164)-metodia. Uudet tiedot tallennetaan tietokantaan `PefMonitoringRepository`:n kautta. Tämän jälkeen käyttöliittymä päivitetään ja näytetään ajantasainen lista syötetyistä arvoista kutsumalla [get_monitoring_by_username](https://github.com/JVilo/ot-harjoitustyo/blob/06b2996b4d65a09ae0ea4328759d3530ffddbd76/src/services/pef_service.py#L171)-metodia.

Tallenna ja sulje

```mermaid
sequenceDiagram
  actor User
  participant UI
  participant PefService
  participant PefMonitoringRepository
  User->>+UI: click "PEF-seuranta"
  UI->>UI: show input fields
  User->>UI: fill fields + click "Tallenna ja sulje"
  UI->>+PefService: add_value_to_monitoring(username, date, values...)
  PefService->>+PefMonitoringRepository: add_value(PefMonitoring)
  PefMonitoringRepository-->>-PefService: OK
  PefService-->>-UI: return
  UI->>UI: hide monitoring section
```
- Jos käyttäjä painaa **"Tallenna ja sulje"**, tiedot tallennetaan samalla tavalla, mutta tämän jälkeen syöttökentät piilotetaan käyttöliittymästä eikä näkymää päivitetä uusilla arvoilla.

### Muut toiminnallisuudet

Sama periaate pätee kaikkiin sovelluksen toiminnallisuuksiin: käyttöliittymän tapahtumakäsittelijä kutsuu sovelluslogiikan metodia, joka puolestaan päivittää pefin tai kirjautuneen käyttäjän tilan. Kun kontrolli palaa takaisin käyttöliittymään, päivitetään tarvittaessa näkymä.
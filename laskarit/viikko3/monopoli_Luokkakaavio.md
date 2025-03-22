```mermaid
classDiagram
    Monopolipeli "1" -- "1" Pelilauta
    Monopolipeli "1" -- "0..8" Pelaaja
    Monopolipeli "1" -- "2" Noppa
    Monopolipeli "1" -- "1" Aloitusruutu
    Monopolipeli "1" -- "1" Vankila

    Pelilauta "1" -- "40" Ruutu

    Ruutu "1" -- "1" Ruutu : seuraava
    Ruutu "1" -- "0..8" Pelinappula
    Ruutu "1" -- "1" SattumaYhteismaa
    Ruutu "1" -- "1" AsemaLaitos
    Ruutu "1" -- "1" Normaalikatu
    Ruutu "1" -- "1" Vankila
    Ruutu "1" -- "1" Aloitusruutu

    Pelinappula "1" -- "1" Pelaaja

    Pelaaja "2..8" -- "1" Monopolipeli
    Pelaaja "1" -- "1" Normaalikatu
    Pelaaja "1" -- "1" Rahaa
    Pelaaja "1" -- "1" Toiminto

    Aloitusruutu "1" -- "1" Toiminto
    Vankila "1" -- "1" Toiminto

    Sattuma "1" -- "1" Kortti
    Yhteismaa "1" -- "1" Kortti

    AsemaLaitos "1" -- "1" Toiminto

    Normaalikatu "1" -- "1" Toiminto
    Normaalikatu "1" -- "0..n" Pelaaja : Omistaja
    Normaalikatu "1" -- "1..4" RakennaTalo
    Normaalikatu "1" -- "1" RakennaHotelli
    
    Kortti "1" -- "1" Toiminto
    ```
import unittest
from kassapaate import Kassapaate

class TestKassapaate(unittest.TestCase):
    def setUp(self):
        self.kassapaate = Kassapaate()

    def test_initial_state(self):
        self.assertEqual(self.kassapaate.kassassa_rahaa, 100000)
        self.assertEqual(self.kassapaate.edulliset, 0)
        self.assertEqual(self.kassapaate.maukkaat, 0)

    def test_kassapaate_on_olemassa(self):
        self.assertNotEqual(self.kassapaate, None)
    
    def test_syo_edullisesti_kateisella_kassan_saldon_oikein(self):
        raha = self.kassapaate.syo_edullisesti_kateisella(300)
        self.assertEqual(raha, 60)
        self.assertEqual(self.kassapaate.kassassa_rahaa, 100240)
        self.assertEqual(self.kassapaate.edulliset, 1)
        
        self.kassapaate.kassassa_rahaa = 100000
        self.kassapaate.edulliset = 0
        raha1 = self.kassapaate.syo_edullisesti_kateisella(200)
        self.assertEqual(raha1, 200)
        self.assertEqual(self.kassapaate.kassassa_rahaa, 100000)
        self.assertEqual(self.kassapaate.edulliset, 0)

    def test_syo_maukkaasti_kateisella_kassan_saldon_oikein(self):
        rahaa = self.kassapaate.syo_maukkaasti_kateisella(500)
        self.assertEqual(rahaa,100)
        self.assertEqual(self.kassapaate.kassassa_rahaa, 100400)
        self.assertEqual(self.kassapaate.maukkaat, 1)

        self.kassapaate.kassassa_rahaa = 100000
        self.kassapaate.maukkaat = 0
        rahaa1 = self.kassapaate.syo_maukkaasti_kateisella(350)
        self.assertEqual(rahaa1, 350)
        self.assertEqual(self.kassapaate.kassassa_rahaa, 100000)
        self.assertEqual(self.kassapaate.maukkaat, 0)
    
    def test_syo_edullisesti_kortilla_kassan_saldon_oikein(self):
        class Kortti:
            def __init__(self, saldo):
                self.saldo = saldo

            def ota_rahaa(self, summa):
                if self.saldo >= summa:
                    self.saldo -= summa
        
        kortti = Kortti(300)
        result = self.kassapaate.syo_edullisesti_kortilla(kortti)
        self.assertEqual(result, True)
        self.assertEqual(self.kassapaate.edulliset, 1)
        self.assertEqual(self.kassapaate.kassassa_rahaa, 100000)

        kortti = Kortti(200)
        self.kassapaate.edulliset = 0
        result = self.kassapaate.syo_edullisesti_kortilla(kortti)
        self.assertEqual(result, False)
        self.assertEqual(self.kassapaate.edulliset, 0)
        self.assertEqual(self.kassapaate.kassassa_rahaa, 100000)
    
    def test_syo_maukkaasti_kortilla_kassan_saldon_oikein(self):
        class Kortti:
            def __init__(self, saldo):
                self.saldo = saldo

            def ota_rahaa(self, summa):
                if self.saldo >= summa:
                    self.saldo -= summa
        
        kortti = Kortti(500)
        result = self.kassapaate.syo_maukkaasti_kortilla(kortti)
        self.assertEqual(result, True)
        self.assertEqual(self.kassapaate.maukkaat, 1)
        self.assertEqual(self.kassapaate.kassassa_rahaa, 100000)

        kortti = Kortti(200)
        self.kassapaate.maukkaat = 0
        result = self.kassapaate.syo_maukkaasti_kortilla(kortti)
        self.assertEqual(result, False)
        self.assertEqual(self.kassapaate.maukkaat, 0)
        self.assertEqual(self.kassapaate.kassassa_rahaa_euroina(), 1000)
    
    def test_lataa_rahaa_kortille(self):
        class Kortti:
            def __init__(self, saldo):
                self.saldo = saldo

            def lataa_rahaa(self, summa):
                self.saldo += summa
        
        kortti = Kortti(500)
        self.kassapaate.lataa_rahaa_kortille(kortti, 200)
        self.assertEqual(kortti.saldo, 700)
        self.assertEqual(self.kassapaate.kassassa_rahaa, 100000+200)
        self.kassapaate.lataa_rahaa_kortille(kortti, -1)
        self.assertEqual(self.kassapaate.kassassa_rahaa, 100200)
        self.assertEqual(kortti.saldo,700)
    
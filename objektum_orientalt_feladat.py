from abc import ABC, abstractmethod
from datetime import datetime

#---------------------------------------------------------------------------------------
# \\\ Classok meghatározása ///

class Auto(ABC):
    def __init__(self, rendszam: str, tipus: str, berleti_dij: int):
        self._rendszam = rendszam
        self._tipus = tipus
        self._berleti_dij = berleti_dij
        self._elerheto = True

    def get_rendszam(self): return self._rendszam
    def set_rendszam(self, v): self._rendszam = v

    def get_tipus(self): return self._tipus
    def set_tipus(self, v): self._tipus = v

    def get_berleti_dij(self): return self._berleti_dij
    def set_berleti_dij(self, v): self._berleti_dij = v

    def get_elerheto(self): return self._elerheto
    def set_elerheto(self, v): self._elerheto = v

    @abstractmethod
    def info(self): pass


class Szemelyauto(Auto):
    def __init__(self, rendszam, marka, berleti_dij, ulohelyek):
        super().__init__(rendszam, marka, berleti_dij)
        self._ulohelyek = ulohelyek

    def get_ulohelyek(self): return self._ulohelyek
    def set_ulohelyek(self, v): self._ulohelyek = v

    def info(self):
        return f"{self.get_rendszam()} – {self.get_tipus()} – {self.get_ulohelyek()} ülés – {self.get_berleti_dij()} Ft/nap"


class Teherauto(Auto):
    def __init__(self, rendszam, marka, berleti_dij, teherbiras):
        super().__init__(rendszam, marka, berleti_dij)
        self._teherbiras = teherbiras

    def get_teherbiras(self): return self._teherbiras
    def set_teherbiras(self, v): self._teherbiras = v

    def info(self):
        return f"{self.get_rendszam()} – {self.get_tipus()} – {self.get_teherbiras()} kg – {self.get_berleti_dij()} Ft/nap"


class Berles:
    def __init__(self, auto: Auto, datum: str):
        self._auto = auto
        self._datum = datum
        self.fizetett_dij = auto.get_berleti_dij()

    def get_auto(self): return self._auto
    def get_datum(self): return self._datum
    def get_fizetett_dij(self): return self.get_fizetett_dij

    def info(self):
        a = self.get_auto()
        return f"{a.get_rendszam()} – {a.get_tipus()} – {self.get_datum()}"


class Autokolcsonzo:
    def __init__(self, nev: str):
        self._nev = nev
        self._autok = []
        self._berlesek = []

    def auto_hozzaad(self, a): self._autok.append(a)
    def berles_hozzaad(self, b): self._berlesek.append(b)

    def get_autok(self): return self._autok
    def get_berlesek(self): return self._berlesek

    def get_berlesek_autohoz(self, auto):
        return [b for b in self._berlesek if b.get_auto() == auto]

    #-----------------------------------------------------------------------------------
    # /// Bérlés \\\

    def berel_auto(self, auto, datum):
        try:
            datetime.strptime(datum, "%Y-%m-%d")
        except ValueError:
            raise Exception("Érvénytelen dátumformátum! (YYYY-MM-DD)")

        if not auto.get_elerheto():
            raise Exception("Az autó foglalt!")

        auto.set_elerheto(False)
        b = Berles(auto, datum)
        self._berlesek.append(b)
        return b.get_fizetett_dij()

    #------------------------------------------------------------------------------------
    # \\\ Bérlés lemondás ///

    def berles_lemond(self, berles):
        auto = berles.get_auto()
        fogl_datum = berles.get_datum()
        today = datetime.today().strftime("%Y-%m-%d")
        
        fiz_dij = berles.get_fizetett_dij()

        if fogl_datum >= today:
            vissza_dij = fiz_dij
        else:
            vissza_dij = 0

        auto.set_elerheto(True)
        self._berlesek.remove(berles)

        return vissza_dij

#-------------------------------------------------------------------------------------------------------
# \\\ Meglévő adatok, amik előzetesen kerülnek betöltésre ///

def inicializalas():
    k = Autokolcsonzo("Rent a Car")

    a1 = Szemelyauto("ABC-123", "Toyota Corolla", 12000, 5)
    a2 = Szemelyauto("XYZ-999", "VW Golf", 15000, 5)
    a3 = Teherauto("AAA-777", "Ford Transit", 20000, 1200)

    k.auto_hozzaad(a1)
    k.auto_hozzaad(a2)
    k.auto_hozzaad(a3)

    foglalasok =[
    (a1, "2026-04-10"),
    (a2, "2026-04-11"),
    (a3, "2026-04-12"),
    (a3, "2026-04-13")
    ]

    today = datetime.today().strftime("%Y-%m-%d")

    for auto, datum in foglalasok:
        b = Berles(auto, datum)
        k.berles_hozzaad(b)

        if datum == today:
            auto.set_elerheto(False)

    return k

#-----------------------------------------------------------------------------------------------
# \\\ Console felület működése ///

def autokivalasztas(k):
    print("\n=== Autók listája ===")
    autok = k.get_autok()

    for i, a in enumerate(autok):
        status = "Szabad" if a.get_elerheto() else "Foglalt"
        print(f"{i+1}. {a.info()} | {status}")

    while True:
        try:
            v = int(input("\nVálassz autót (sorszám): "))
            if 1 <= v <= len(autok):
                return autok[v-1]
        except:
            pass
        print("Érvénytelen választás.")


def automenü(k, auto):
    while True:
        print(f"\n=== Autó adatlap: {auto.get_rendszam()} ===")
        print(auto.info())
        print(f"Státusz: {'Szabad' if auto.get_elerheto() else 'Foglalt'}")

        print("\n1. Autó bérlése")
        print("2. Foglalások megtekintése")
        print("3. Foglalás lemondása")
        print("0. Vissza")

        valasz = input("Választás: ")

        if valasz == "1":
            datum = input("Dátum (YYYY-MM-DD): ")
            try:
                dij = k.berel_auto(auto, datum)
                print(f"\n Bérlés rögzítve!")
                print(f"Bérleti díj fizetve: {dij} Ft")
            except Exception as e:
                print("Hiba:", e)

        elif valasz == "2":
            fogl = k.get_berlesek_autohoz(auto)
            if not fogl:
                print("Nincs foglalás.")
            else:
                print("\nFoglalások:")
                for b in fogl:
                    print("-", b.info())

        elif valasz == "3":
            fogl = k.get_berlesek_autohoz(auto)
            if not fogl:
                print("Ehhez az autóhoz nincs foglalás.")
                continue

            print("\nFoglalások:")
            for i, b in enumerate(fogl):
                print(f"{i+1}. {b.info()}")

            try:
                idx = int(input("Melyik foglalást törlöd? ")) - 1
                ber = fogl[idx]
                vissza = k.berles_lemond(ber)
                print("\n Foglalás törölve.")
                print(f"Visszajáró bérleti díj: {vissza} Ft")
            except:
                print("Érvénytelen választás.")

        elif valasz == "0":
            return
        else:
            print("Érvénytelen opció.")


def menu():
    k = inicializalas()

    while True:
        print("\n===== AUTÓKÖLCSÖNZŐ =====")
        print("1. Autó kiválasztása")
        print("0. Kilépés")

        v = input("Választás: ")

        if v == "1":
            auto = autokivalasztas(k)
            automenü(k, auto)

        elif v == "0":
            print("Kilépés...")
            break

        else:
            print("Érvénytelen opció.")


if __name__ == "__main__":
    menu()
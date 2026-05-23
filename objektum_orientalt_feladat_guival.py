import tkinter as tk
from tkinter import messagebox, simpledialog, Toplevel, Listbox, END
from abc import ABC, abstractmethod
from datetime import datetime


#//////////////////////////////////////////////////////////////////////////////
# Autó adatok

class Auto(ABC):
    def __init__(self, rendszam: str, tipus: str, berleti_dij: int):
        self._rendszam = rendszam
        self._tipus = tipus
        self._berleti_dij = berleti_dij

    def get_rendszam(self): return self._rendszam
    def get_tipus(self): return self._tipus
    def get_berleti_dij(self): return self._berleti_dij

    @abstractmethod
    def info(self): pass


class Szemelyauto(Auto):
    def __init__(self, rendszam, marka, berleti_dij, ulohelyek):
        super().__init__(rendszam, marka, berleti_dij)
        self._ulohelyek = ulohelyek

    def get_ulohelyek(self): return self._ulohelyek

    def info(self):
        return f"{self.get_rendszam()} – {self.get_tipus()} – Ülőhelyek: {self.get_ulohelyek()} – {self.get_berleti_dij()} Ft"


class Teherauto(Auto):
    def __init__(self, rendszam, marka, berleti_dij, teherbiras):
        super().__init__(rendszam, marka, berleti_dij)
        self._teherbiras = teherbiras

    def get_teherbiras(self): return self._teherbiras

    def info(self):
        return f"{self.get_rendszam()} – {self.get_tipus()} – Teherbírás: {self.get_teherbiras()} kg – {self.get_berleti_dij()} Ft"


#//////////////////////////////////////////////////////////////////////////////
# Foglalás

class Berles:
    def __init__(self, auto: Auto, datum: str):
        self._auto = auto
        self._datum = datum

    def get_auto(self): return self._auto
    def get_datum(self): return self._datum

    def info(self):
        a = self.get_auto()
        return f"{a.get_rendszam()} – {a.get_tipus()} – {self._datum}"


#//////////////////////////////////////////////////////////////////////////////
# Kölcsönző logika

class Autokolcsonzo:
    def __init__(self, nev: str):
        self._nev = nev
        self._autok = []
        self._berlesek = []

    def auto_hozzaad(self, a): self._autok.append(a)
    def get_autok(self): return self._autok
    def get_berlesek(self): return self._berlesek

    def get_berlesek_autohoz(self, auto: Auto):
        return [b for b in self._berlesek if b.get_auto() == auto]

    def berel_auto(self, auto: Auto, datum: str):
        try:
            datetime.strptime(datum, "%Y-%m-%d")
        except ValueError:
            raise Exception("Érvénytelen dátum (YYYY-MM-DD)")

        today = datetime.today().date()

        van_foglalas = any(
            b.get_auto() == auto and
            datetime.strptime(b.get_datum(), "%Y-%m-%d").date() >= today
            for b in self._berlesek
        )

        if van_foglalas:
            raise Exception("Erre a napra már van foglalás!")

        self._berlesek.append(Berles(auto, datum))

        return auto.get_berleti_dij()

    def berles_lemond(self, berles: Berles):
        if berles in self._berlesek:
            self._berlesek.remove(berles)


#//////////////////////////////////////////////////////////////////////////////
# Inicializálás

def inicializalas():
    k = Autokolcsonzo("CityCar")

    a1 = Szemelyauto("ABC-123", "Toyota Corolla", 12000, 5)
    a2 = Szemelyauto("XYZ-999", "VW Golf", 15000, 5)
    a3 = Teherauto("AAA-777", "Ford Transit", 20000, 1200)

    k.auto_hozzaad(a1)
    k.auto_hozzaad(a2)
    k.auto_hozzaad(a3)

    k._berlesek = [
        Berles(a1, "2026-04-10"),
        Berles(a2, "2026-04-11"),
        Berles(a3, "2026-04-12"),
        Berles(a3, "2026-04-13"),
    ]

    return k


#//////////////////////////////////////////////////////////////////////////////
# GUI

class AutoKolcsonzoGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Autókölcsönző")
        self.k = inicializalas()

        tk.Label(root, text="Autók:").pack(pady=5)

        self.listbox = Listbox(root, width=60)
        self.listbox.pack(pady=10)

        self.frissit()

        tk.Button(root, text="Kiválaszt", command=self.kivalaszt).pack(pady=10)

    def frissit(self):
        self.listbox.delete(0, END)

        
        for a in self.k.get_autok():

            today = datetime.today().date()

            van_foglalas = any(
                b.get_auto() == a and
                datetime.strptime(b.get_datum(), "%Y-%m-%d").date() >= today
                for b in self.k.get_berlesek()
            )

            status = "Foglalt" if van_foglalas else "Szabad"

            self.listbox.insert(END, f"{a.get_rendszam()} – {a.get_tipus()} – {status}")

    def kivalaszt(self):
        idx = self.listbox.curselection()

        if not idx:
            messagebox.showerror("Hiba", "Nincs kiválasztva")
            return

        auto = self.k.get_autok()[idx[0]]
        AutoAblak(self.root, auto, self.k, self)


#//////////////////////////////////////////////////////////////////////////////
# Autó ablak

class AutoAblak:
    def __init__(self, root, auto, k, foablak):
        self.auto = auto
        self.k = k
        self.foablak = foablak

        self.win = Toplevel(root)
        self.win.title(auto.get_rendszam())

        tk.Label(self.win, text=auto.info()).pack(pady=10)

        tk.Button(self.win, text="Bérlés", command=self.berles).pack(pady=5)
        tk.Button(self.win, text="Foglalások", command=self.foglalasok).pack(pady=5)
        tk.Button(self.win, text="Lemondás", command=self.lemondas).pack(pady=5)

    def berles(self):
        datum = simpledialog.askstring("Bérlés", "YYYY-MM-DD")
        if not datum:
            return

        try:
            ar = self.k.berel_auto(self.auto, datum)
            messagebox.showinfo("OK", f"Sikeres foglalás: {ar} Ft")
        except Exception as e:
            messagebox.showerror("Hiba", str(e))

        self.foablak.frissit()

    def foglalasok(self):
        win = Toplevel(self.win)
        win.title("Foglalások")

        fogl = self.k.get_berlesek_autohoz(self.auto)

        if not fogl:
            tk.Label(win, text="Nincs foglalás").pack()
            return
        
        lb = Listbox(win, width=50)
        lb.pack(pady=10)

        for b in fogl:
            lb.insert(END, b.info())

    def lemondas(self):
        fogl = self.k.get_berlesek_autohoz(self.auto)

        if not fogl:
            messagebox.showerror("Hiba", "Nincs foglalás ehhez az autóhoz.")
            return

        win = Toplevel(self.win)
        win.title("Foglalás lemondása")

        lb = Listbox(win, width=50)
        lb.pack(pady=10)

        for b in fogl:
            lb.insert(END, b.info())

        def torles():
            idx = lb.curselection()
            if not idx:
                messagebox.showerror("Hiba", "Nincs kiválasztva!")
                return

            self.k.berles_lemond(fogl[idx[0]])
            messagebox.showinfo("OK", "Foglalás törölve")
            win.destroy()
            self.foablak.frissit()

        tk.Button(win, text="Kiválaszt és töröl", command=torles).pack(pady=5)

        self.foablak.frissit()


#//////////////////////////////////////////////////////////////////////////////
# Futtatás

root = tk.Tk()
AutoKolcsonzoGUI(root)
root.mainloop()
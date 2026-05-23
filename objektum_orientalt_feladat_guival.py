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
        return f"{self.get_rendszam()} – {self.get_tipus()} – Ülőhelyek: {self.get_ulohelyek()} – {self.get_berleti_dij()} Ft"


class Teherauto(Auto):
    def __init__(self, rendszam, marka, berleti_dij, teherbiras):
        super().__init__(rendszam, marka, berleti_dij)
        self._teherbiras = teherbiras

    def get_teherbiras(self): return self._teherbiras
    def set_teherbiras(self, v): self._teherbiras = v

    def info(self):
        return f"{self.get_rendszam()} – {self.get_tipus()} – Teherbírás: {self.get_teherbiras()} kg – {self.get_berleti_dij()} Ft"


class Berles:
    def __init__(self, auto: Auto, datum: str):
        self._auto = auto
        self._datum = datum

    def get_auto(self): return self._auto
    def get_datum(self): return self._datum

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

    def get_berlesek_autohoz(self, auto: Auto):
        return [b for b in self._berlesek if b.get_auto() == auto]

    def berel_auto(self, auto: Auto, datum: str):
        try:
            datetime.strptime(datum, "%Y-%m-%d")
        except ValueError:
            raise Exception("Érvénytelen dátumformátum. (YYYY-MM-DD)")

        if not auto.get_elerheto():
            raise Exception("Az autó foglalt!")

        auto.set_elerheto(False)
        b = Berles(auto, datum)
        self._berlesek.append(b)
        return auto.get_berleti_dij()

    def berles_lemond(self, berles: Berles):
        a = berles.get_auto()
        a.set_elerheto(True)
        self._berlesek.remove(berles)

#//////////////////////////////////////////////////////////////////////////////////
# Előzetesen megadott adatok

def inicializalas():
    k = Autokolcsonzo("CityCar")

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

#////////////////////////////////////////////////////////////////////////////////////
# GUI

class AutoKolcsonzoGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Autókölcsönző – Autó kiválasztása")
        self.k = inicializalas()

        tk.Label(root, text="Válassz egy autót:").pack(pady=5)

        self.listbox = Listbox(root, width=60)
        self.listbox.pack(pady=10)

        self.frissit_autolista()

        tk.Button(root, text="Kiválaszt", command=self.kivalaszt).pack(pady=10)

    def frissit_autolista(self):
        self.listbox.delete(0, END)
        for a in self.k.get_autok():
            status = "Szabad" if a.get_elerheto() else "Foglalt"
            self.listbox.insert(END, f"{a.get_rendszam()} – {a.get_tipus()} – {status}")

    def kivalaszt(self):
        idx = self.listbox.curselection()
        if not idx:
            messagebox.showerror("Hiba", "Nincs kiválasztva autó!")
            return

        auto = self.k.get_autok()[idx[0]]
        AutoAblak(self.root, auto, self.k, self)


class AutoAblak:
    def __init__(self, root, auto: Auto, kolcsonzo: Autokolcsonzo, foablak):
        self.auto = auto
        self.k = kolcsonzo
        self.foablak = foablak

        self.win = Toplevel(root)
        self.win.title(f"Autó adatlap: {auto.get_rendszam()}")

        tk.Label(self.win, text=auto.info()).pack(pady=10)

        tk.Button(self.win, text="Autó bérlése", width=30,
                  command=self.berles).pack(pady=5)

        tk.Button(self.win, text="Foglalásai", width=30,
                  command=self.foglalasok).pack(pady=5)

        tk.Button(self.win, text="Foglalás lemondása", width=30,
                  command=self.lemondas).pack(pady=5)

    def berles(self):
        datum = simpledialog.askstring("Bérlés", "Dátum (YYYY-MM-DD)")
        if not datum:
            return

        try:
            ar = self.k.berel_auto(self.auto, datum)
            messagebox.showinfo("Siker", f"Bérlés rögzítve! Ár: {ar} Ft")
        except Exception as e:
            messagebox.showerror("Hiba", str(e))

        self.foablak.frissit_autolista()

    def foglalasok(self):
        win = Toplevel(self.win)
        win.title("Foglalások")
        fogl = self.k.get_berlesek_autohoz(self.auto)

        if not fogl:
            tk.Label(win, text="Nincs foglalás").pack()
            return

        for b in fogl:
            tk.Label(win, text=b.info()).pack()

    def lemondas(self):
        fogl = self.k.get_berlesek_autohoz(self.auto)

        if not fogl:
            messagebox.showerror("Hiba", "Nincsenek foglalások ehhez az autóhoz.")
            return

        # Ha csak 1 foglalás van → automatikus
        if len(fogl) == 1:
            self.k.berles_lemond(fogl[0])
            messagebox.showinfo("OK", "Foglalás lemondva.")
        else:
            # Több foglalás esetén listából választás
            win = Toplevel(self.win)
            win.title("Foglalás kiválasztása")

            lb = Listbox(win, width=50)
            lb.pack(pady=10)

            for b in fogl:
                lb.insert(END, b.info())

            def valaszt():
                idx = lb.curselection()
                if not idx:
                    messagebox.showerror("Hiba", "Nincs kiválasztva foglalás!")
                    return
                self.k.berles_lemond(fogl[idx[0]])
                messagebox.showinfo("OK", "Foglalás lemondva.")
                win.destroy()

            tk.Button(win, text="Kiválaszt és töröl", command=valaszt).pack(pady=5)

        self.foablak.frissit_autolista()


# /////////////////////////////////////////////////////////////////////////////////////

root = tk.Tk()
AutoKolcsonzoGUI(root)
root.mainloop()
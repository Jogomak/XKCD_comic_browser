# -*- coding: utf-8 -*-
import random
import os
from bs4 import BeautifulSoup
import urllib2
import gi
import os.path

# wymagamy biblioteki w wersji min 3.0
gi.require_version('Gtk', '3.0')

from gi.repository import Gtk
from gi.repository import GdkPixbuf


class PrzegladarkaKomiksuXKCD:
    """Klasa implementująca przeglądarkę komiksu ze strony https://xkcd.com/."""
    def __init__(self):
        """Konstuktor klasy. Tworzy elementy interfejsu graficznego i ustawia domyślne wartości elementów i pól klasy."""
        self.comic_number = 0
        self.last_comic_number = 0
        self.image_width = 0
        self.image_height = 0
        self.image_scale = 1  # początkowe skalowanie obrazka

        scroll_window = Gtk.ScrolledWindow()
        self.main_window = Gtk.Window()
        main_vbox = Gtk.VBox()
        navigate_hbox = Gtk.HBox()
        navigate_hbox.set_halign(3)
        comic_title_hbox = Gtk.HBox()
        comic_title_hbox.set_halign(3)
        zoom_hbox = Gtk.HBox()
        zoom_hbox.set_halign(3)
        select_number_hbox = Gtk.HBox()
        select_number_hbox.set_halign(3)

        self.comic_image = Gtk.Image()
        self.comic_title_label = Gtk.Label()
        self.comic_number_label = Gtk.Label()
        self.select_comic_number = Gtk.Entry()

        change_comic_button = Gtk.Button('Change')
        button_first = Gtk.Button.new_with_label('<<')
        button_prev = Gtk.Button.new_with_label('<')
        button_random = Gtk.Button.new_with_label('Random')
        button_next = Gtk.Button.new_with_label('>')
        button_last = Gtk.Button.new_with_label('>>')
        button_zoom_in = Gtk.Button.new_with_label('zoom in')
        button_zoom_out = Gtk.Button.new_with_label('zoom out')

        self.main_window.add(scroll_window)
        scroll_window.add(main_vbox)
        main_vbox.pack_start(comic_title_hbox, False, False, 0)
        main_vbox.pack_start(navigate_hbox, False, False, 0)
        main_vbox.pack_start(self.comic_image, False, False, 0)
        main_vbox.pack_start(zoom_hbox, False, False, 0)
        main_vbox.pack_start(select_number_hbox, False, False, 0)
        comic_title_hbox.pack_start(self.comic_number_label, False, False, 0)
        comic_title_hbox.pack_start(self.comic_title_label, False, False, 0)
        zoom_hbox.pack_start(button_zoom_in, False, False, 0)
        zoom_hbox.pack_start(button_zoom_out, False, False, 0)
        select_number_hbox.pack_start(self.select_comic_number, False, False, 0)
        select_number_hbox.pack_start(change_comic_button, False, False, 0)
        navigate_hbox.pack_start(button_first, False, False, 0)
        navigate_hbox.pack_start(button_prev, False, False, 0)
        navigate_hbox.pack_start(button_random, False, False, 0)
        navigate_hbox.pack_start(button_next, False, False, 0)
        navigate_hbox.pack_start(button_last, False, False, 0)

        self.main_window.connect("delete-event", Gtk.main_quit)
        button_first.connect('clicked', self.change_comic_number, -2)
        button_prev.connect('clicked', self.change_comic_number, -1)
        button_random.connect('clicked', self.change_comic_number, 0)
        button_next.connect('clicked', self.change_comic_number, 1)
        button_last.connect('clicked', self.change_comic_number, 2)
        button_zoom_in.connect('clicked', self.scale_image, 0.2)
        button_zoom_out.connect('clicked', self.scale_image, -0.2)
        change_comic_button.connect('clicked', self.change_comic_number, 3)

        self.main_window.set_default_size(900, 500)
        self.main_window.show_all()

        self.load_comic_number()
        Gtk.main()

    def load_comic_number(self):
        """Metoda klasy pobierająca ze strony komiksu numer najnowszego komiksu."""
        data = urllib2.urlopen('https://xkcd.com/')
        soup = BeautifulSoup(data, 'html.parser')

        for html_list in soup.find_all('ul'):
            if html_list.has_attr('class') and html_list.get('class')[0] == 'comicNav':
                for html_list_element in html_list.find_all('li'):
                    if html_list_element.a.has_attr('rel') and html_list_element.a.get('rel')[0] == 'prev':
                        self.last_comic_number = int(html_list_element.a.get('href').strip('/')) + 1
                        self.comic_number = self.last_comic_number

        self.load_image()

    def check_dir_exists(self, path):
        if not os.path.isdir(path):
            os.makedirs(path)

    def get_image_url(self):
        """Metoda pobierająca ze strony komiksu tutuł komiksu i adres jego abrazka.

        Po pobraniu tytułu zapisuje go do pliku o nazwie '[numerkomiksu]_title' w podfolderze ./cache.
        Metoda zwraca string zawierający adres obrazka komiksu.
        """
        data = urllib2.urlopen('https://xkcd.com/' + str(self.comic_number))
        soup = BeautifulSoup(data, 'html.parser')

        for division in soup.find_all('div'):
            if division.has_attr('id') and division.get('id') == 'ctitle':
                title = division.text.strip()
                self.check_dir_exists('./cache')
                if not os.path.exists('./cache/' + str(self.comic_number) + '_title'):
                    with open('./cache/' + str(self.comic_number) + '_title', 'w') as file:
                        #zapisanie tytułu komiksu do pliku
                        file.write(title)
            elif division.has_attr('id') and division.get('id') == 'comic':
                if division.img.has_attr('src'):
                    image_url = 'https:' + division.img.get('src')

        return image_url

    def load_image(self):
        """Metoda aktualizująca tytuł komiksu i wyświetlająca nowy komiks w oknie.

        Jeśli obraz komiksu nie istnieje w folderze ./cache to pobiera adres url wywołując metodę self.get_image_url,
        następnie wszytuje obraz ze strony i zapisuje go do pliku o nazwie '[numerkomiksu]' w folderze ./cache.
        Następnie wczytuje obraz i tytuł komiksu z plików i aktualizuje nimi okno aplikacji.
        """
        self.check_dir_exists('./cache')
        if not os.path.exists('./cache/' + str(self.comic_number)):
            image = urllib2.urlopen(self.get_image_url())
            with open('./cache/' + str(self.comic_number), 'wb') as file:
                #zapisanie obrazu komiksu do pliku
                file.write(image.read())

        comic_pixbuf = GdkPixbuf.Pixbuf.new_from_file('./cache/' + str(self.comic_number))
        self.comic_image.set_from_pixbuf(comic_pixbuf)
        #pobranie oryginalnego rozmiaru obrazu
        self.image_width = comic_pixbuf.get_width()
        self.image_height = comic_pixbuf.get_height()
        self.image_scale = 1

        self.comic_number_label.set_text(str(self.comic_number) + '. ')
        with open('./cache/' + str(self.comic_number) + '_title', 'r') as file:
            self.comic_title_label.set_markup('<b>' + file.readline() + '</b>')

    def change_comic_number(self, button, change):
        """Metoda zmieniająca aktualnie wyświetlany komiks.

        button - przycisk który wysłał sygnał
        change - kod dzięki któremu rozpoznamy na jaki numer komiksu chcemy zmienić:
            -2 - pierwszy komiks
            -1 - poprzedni komiks
            0 - losowy komiks
            1 - następny komiks
            2 - najnowszy komiks
            3 - numer komiksu wczytany z pola pod komiksem
        W przypadku 3, gdy wpisany numer komiksu jest niepoprawny wyświetlane zostaje okno dialogowe informujące o tym.
        Na koniec zostaje wywołana metoda self.load_image uaktualniająca okno aplikacji.
        """
        if change:
            if change == -2:
                self.comic_number = 1
            elif change == 2:
                self.comic_number = self.last_comic_number
            elif change == 3:
                try:
                    number = int(self.select_comic_number.get_text())
                    if number > 0 and number <= self.last_comic_number:
                        self.comic_number = number
                    else:
                        raise Exception()
                    self.select_comic_number.set_text('')
                except:
                    warning_dialog = Gtk.MessageDialog(self.main_window, 0)
                    warning_dialog.set_markup('Bledny numer komiksu!')
                    warning_dialog.add_button('OK', 0)
                    warning_dialog.run()
                    warning_dialog.destroy()
            elif self.comic_number + change > 0 and self.comic_number + change <= self.last_comic_number:
                self.comic_number += change
        else:
            self.comic_number = random.randint(1, self.last_comic_number)

        self.load_image()

    def scale_image(self, button, change):
        """Metoda zmieniająca skalowanie obrazka i wyświetlająca go w nowej skali.

        button - przycisk który wysłał sygnał
        change - wartoś o jaką chcemy zmienić skalowanie
        Jeśli nowe skalowanie mieści się w przedziale [0.4, 2] to metoda pobiera obraz z pliku znajdującego się w
        folderze ./cache, przeskalowuje go i wyświetla w oknie.
        """
        if self.image_scale + change >= 0.4 and self.image_scale + change <= 2:
            self.image_scale += change
            comic_pixbuf = GdkPixbuf.Pixbuf.new_from_file('./cache/' + str(self.comic_number)).scale_simple(
                self.image_width * self.image_scale, self.image_height * self.image_scale, 3)
            self.comic_image.set_from_pixbuf(comic_pixbuf)

if __name__ == '__main__':
    PrzegladarkaKomiksuXKCD()
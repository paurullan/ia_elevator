#!/usr/bin/env python 
# -*- coding: utf-8 -*-

from __future__ import print_function

import PyQt4.QtCore

__version__ = "0.0.1"

class Elevator(PyQt4.QtCore.QObject):
    
    def __init__(self, n_floors=5, initial_floor=0):
        """ 
        Les accions pending són les que falten per processar. Les new són les
        que la interfície ha llançat i encara s'han d'afegir a la llista
        pending. El motiu de separació d'aquests conjunts és per no tenir
        problemes de concurrència i simular que l'ascensor no pot canviar
        d'opinió en segons quins moments

        El format de les accions són (tipus, pis objectiu), on els tipus són
        "up", "down", "open".
        
        open_floor_log és una cua on afegim els pisos que hem obert la
        porta. Molt útil per fer els unittest.
        """
        super(Elevator, self).__init__()

        self.pending = set()
        self.new = set()

        self.direction = "up"

        assert(n_floors > 0 )
        assert(initial_floor < n_floors)

        self.floor = initial_floor
        self.n_floors = n_floors
        self.bottom_floor = 0
        self.top_floor = n_floors-1

        self.open_floor_log = []
        self.last = "init"


    def emit_update(self):
        self.emit(PyQt4.QtCore.SIGNAL("update()"))


    def update_pending(self):
        self.pending.update(self.new)
        self.new = set()

    def add_list(self, cases):
        """La llista d'estímuls d'entrada s'afegeixen al conjunt d'estímuls
        pendents a actualitzar. Necessari pels unittest."""
        self.new.update(cases)

    @property
    def opposite(self):
        if self.direction == "up":
            return "down"
        else:
            return "up"

    def flip_direction(self):
        self.direction = self.opposite


    def present(self, action):
        return action in self.pending or action in self.new

    def next(self):
        """
        Funció clau de l'algorisme de l'ascensor que indica l'acció a fer.
        obrir, pujar, baixar o esperar i obrir per canviar de sentit. (open,
        up, down, wait, open_switch).

        Important que en els casos que obrim cal afegir a la llista de log de
        portes obertes.
        """
        if not self.pending:
            return "wait"
        if (self.floor, "open") in self.pending or (self.floor, self.direction) in self.pending or (self.floor, self.opposite) in self.pending:
            return self.calc_open()
        if self.direction == "up":
            return self.calc_up()
        elif self.direction == "down":
            return self.calc_down()
        
    def calc_open(self):
        """
        L'ascensor té una petició en el pis acutal, per tan s'ha de saber si
	s'ha d'obrir la porta, si s'ha d'obrir i canviar de sentit o si ha de
	seguir amb la direcció que anava.
        """
	
        upper_floors = range(self.floor+1, self.n_floors)
        lower_floors = range(self.floor-1, self.bottom_floor-1, -1)
	
	if (self.floor, self.direction) in self.pending:
	    return "open"
	if (self.floor, "open") in self.pending:
	    if (self.floor, self.opposite) in self.pending:
	        if self.direction == "up":
		    for i in upper_floors:
		        if (i, "open") in self.pending or \
		           (i, "down") in self.pending or \
		           (i, "up") in self.pending:
			    return "open"
		    return "open_switch"
	        else:
		    for i in lower_floors:
		        if (i, "open") in self.pending or \
		           (i, "down") in self.pending or \
		           (i, "up") in self.pending:
			    return "open"
	  	    return "open_switch"
	    else:
		return "open"
	else: #Nomes tenim l'opposite seleccionat
	    if self.direction == "up":
		return self.calc_up()
	    else:
		return self.calc_down()

    def calc_up(self):
        """
        L'ascensor està pujant, càlcul de l'acció a fer. Casos seguir pujant,
        pujar fins a poder canviar de sentit (més proper), canviar sentit i
        baixar fins tenir algú per baixar (proper), baixar fins recollir algú
        per pujar (més llunyà).
        """
        upper_floors = range(self.floor+1, self.n_floors)
        lower_floors = range(self.floor-1, self.bottom_floor-1, -1)
        up_to_floors = range(self.bottom_floor, self.floor)
        for i in upper_floors:
            if (i, "open") in self.pending or (i, "up") in self.pending:
                return "up"
        for i in upper_floors:
            if (i, "down") in self.pending:
                return "up"
        # canvi de sentit
        if (self.floor, "down") in self.pending:
            return "open_switch"
        # casos de trucades des de més avall
        for i in lower_floors:
            if (i, "down") in self.pending:
                return "down"
        for i in up_to_floors:
            if (i, "up") in self.pending or (i, "open") in self.pending:
                return "down"


    def calc_down(self):
        """
        L'ascensor està baixant, càlcul de l'acció. Casos de baixada: seguir
        baixant, baixar fins recollir un de pujada (més llunyà), pujar per
        recollir un de pujada (més proper), pujar fins recollir un de baixar
        (més llunyà),
        """
        upper_floors = range(self.floor+1, self.n_floors)
        lower_floors = range(self.floor-1, self.bottom_floor-1, -1)
        up_to_floors = range(self.bottom_floor-1, self.floor-1)
        down_to_floors = range(self.n_floors, self.floor, -1)

        for i in lower_floors:
            if (i, "open") in self.pending or (i, "down") in self.pending:
                return "down"
        for i in lower_floors:
            if (i, "up") in self.pending:
                return "down"
        # canvi de sentit
        if (self.floor, "up") in self.pending:
            return "open_switch"
        for i in upper_floors:
            if (i, "up") in self.pending:
                return "up"
        for i in down_to_floors:
            if (i, "down") in self.pending or (i, "open") in self.pending:
                return "up"

    def do(self):
        """Obté el valor de la següent acció, l'executa i la lleva de la llista
        d'estímuls pendents a respondre. En cas que es processi una acció en el
        pis local cal confirmar que llevam els possibles (local, "open").
        """
        if self.last == "init":
            action = "wait"
            return action
        if self.last == "open":
            action = "close"
            return action
        if not self.pending:
            return "wait"

        action = self.next()
        if action == "open_switch":
            action = "open"
            self.flip_direction()
        if action == "open":
            self.open_floor_log.append(self.floor)
            open_door = (self.floor, "open")
            get_person = (self.floor, self.direction)
            if open_door in self.pending:
                self.pending.remove(open_door)
            if get_person in self.pending:
                self.pending.remove(get_person)
        elif action == "up":
            self.floor += 1
            assert(self.floor < self.n_floors)
            self.direction = "up"
        elif action == "down":
            self.floor -= 1
            assert(self.floor >= 0)
            self.direction = "down"
        return action

    def floor_actions(self):
        """Calcula a una tupla els pisos a que s'ha d'obrir la porta en
        ordre. Útil pels unittest. Pot incloure repeticions com «(1, 2, 3, 2,
        1)». Afecta a l'estat de l'ascensor.
        """
        self.update_pending()
        while self.pending:
            self.last = self.do()
        return tuple(self.open_floor_log)

    def action(self):
        self.update_pending()
        self.last = self.do()
        self.emit_update()


    def __str__(self):
        s = "new: %s \n" % self.new
        s += "pending: %s\n" % self.pending
        s += "pis: %d\n" % self.floor
        s += "direcció: %s\n" % self.direction
        s += "darrera: %s" % self.last
        return s


if __name__ == '__main__':
    pass

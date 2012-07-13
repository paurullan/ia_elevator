#!/usr/bin/env python 
# -*- coding: utf-8 -*-

"""

Unittest de la pràctica de l'ascensor. La intenció és poder tenir tot el
conjunt de funcionalitats de la pràctica sense haver de fer cap interfície
gràfica. Amb els unittest també podrem confirmar casos extrems, com d'ascensors
que passen buits per anar a buscar més gent a pisos més avall, sense passar
pena de rompre el codi.

La codificació dels casos consisteix en dos vectors, un dels estímuls externs i
un que simbolitza els pisos on s'obren les portes i per ordre. Cal fixar-se que
el vector d'estímuls es refereix a l'estat en un moment determinat i deixarem
de banda temes de concurrència. Aquest vector també suposa que no tenim accions
repetides. També és important veure que l'ordre d'apertura de les portes si és
important i poden haver pisos repetits.

Usarem els símbols «d», per l'apertura (altgr+i), «b» per baixar (altgr+u) i «a»
per pujar (altgr+shift+u).
"""

from __future__ import print_function

import unittest

import elevator

__version__ = "0.0.1"

class TestElevator(unittest.TestCase):
    """Classe pròpia pels tests de l'ascensor"""

    def setUp(self):
        """ Creació de l'ascensor. Determinam 6 pisos i que l'ascensor comenci
        al zero."""
        self.elevator = elevator.Elevator(6, 0)

    def test_one(self):
        """
        Cas senzill de tot trucades internes.
        (0, 1d, 2d, 3d, 4d, 5d) -> (1, 2, 3, 4, 5)
        """
        cases = [(1,"open"), (2,"open"), (3,"open"), (4,"open"), (5,"open")]
        results = (1, 2, 3, 4, 5)
        self.elevator.add_list(cases)
        self.assertEqual(self.elevator.floor_actions(), results)

    def test_two(self):
        """
        Cas senzill de pujar
        (1, 2a, 3d) -> (2, 3)
        """
        cases = [(2, "up"), (3, "open")]
        results = (2, 3)
        self.elevator.floor = 1
        self.elevator.add_list(cases)
        self.assertEqual(self.elevator.floor_actions(), results)

    def test_three(self):
        """
        Cas senzill de baixada
        (5, 4b, 3d) -> (4, 3)
        """
        cases = [(4, "down"), (3, "open")]
        results = (4, 3)
        self.elevator.floor = 5
        self.elevator.add_list(cases)
        self.assertEqual(self.elevator.floor_actions(), results)

    def test_four(self):
        """
        Cas senzill de pujar
        (4, 3a) -> (3)
        """
        cases = [(3, "open")]
        results = (3,)
        self.elevator.floor = 4
        self.elevator.add_list(cases)
        self.assertEqual(self.elevator.floor_actions(), results)

    def test_five(self):
        """
        Cas senzill de pujar
        (4, 2a) -> (2)
        """
        cases = [(2, "open")]
        results = (2,)
        self.elevator.floor = 4
        self.elevator.add_list(cases)
        self.assertEqual(self.elevator.floor_actions(), results)


    def test_up_all(self):
        """
        Cas senzill de tot pujades.
        (0, 1a, 2a, 3a, 4a, 5a) -> (1, 2, 3, 4, 5)
        """
        cases = [(1, "up"), (2, "up"), (3, "up"), (4, "up"), (5, "up")]
        results = (1, 2, 3, 4, 5)
        self.elevator.add_list(cases)
        self.assertEqual(self.elevator.floor_actions(), results)

    def test_down_all(self):
        """
        Cas senzill de tot baixades. Cal fixar-se que l'ascensor amb aquest
        conjunt d'estímuls anirà primer de tot al pis d'adalt i llavors
        començarà a baixar.
        (0, 1b, 2b, 3b, 4b, 5b) -> (5, 4, 3, 2, 1)
        """
        cases = [(1, "down"), (2, "down"), (3, "down"), (4, "down"), (5,"down")]
        results = (5, 4, 3, 2, 1)
        self.elevator.add_list(cases)
        self.assertEqual(self.elevator.floor_actions(), results)


    def test_up_from_middle(self):
        """
        Cas particular on l'ascensor comença del centre i volem fer una pujada.
        (3, 2a, 4a) -> (4, 2)
        """
        cases = [(2, "up"), (4, "up")]
        results = (4, 2)
        self.elevator.floor = 3
        self.elevator.direction = "up"
        self.elevator.add_list(cases)
        self.assertEqual(self.elevator.floor_actions(), results)
    

    def test_down_from_middle(self):
        """
        Cas particular on l'ascensor comença del centre i volem fer una
        baixada. Lo interessant és que abans de començar a baixar pujarà un
        pis.
        (3, 2b, 4b) -> (4, 2)
        """
        cases = [(2, "down"), (4, "down")]
        results = (4, 2)
        self.elevator.floor = 3
        self.elevator.direction = "up"
        self.elevator.add_list(cases)
        self.assertEqual(self.elevator.floor_actions(), results)
    

    def test_mixed_up(self):
        """
        Primer cas complexe de pujades i baixades.
        (0 1a 2d 3b 4a 5d) -> (1, 2, 4, 5, 3) 
        """
        cases = [(1, "up"), (2, "open"), (3, "down"), (4, "up"), (5, "open")]
        results = (1, 2, 4, 5, 3)
        self.elevator.add_list(cases)
        self.assertEqual(self.elevator.floor_actions(), results)


    def test_mixed_up_from_middle(self):
        """
        Primer cas complexe de pujades i baixades però amb l'ascensor centrat.
        (3 4a 5b 2b 1a) -> (4, 5, 2, 1)
        """
        cases = [(1, "up"), (2, "down"), (4, "up"), (5, "down")]
        results = (4, 5, 2, 1)
        self.elevator.floor = 3
        self.elevator.add_list(cases)
        self.assertEqual(self.elevator.floor_actions(), results)


    def test_door_conflict(self):
        """
        Cas complexe on a un pis tenim vàries cridades i cal resoldre el servei
        sense obrir la porta dos pics seguits.
        (2, 3d, 3a, 3b, 4d, 1d) -> (3, 4, 3, 1)
        """
        cases = [(3, "open"), (3, "up"), (3, "down"), (4, "open"), (1, "open")]
        results = (3, 4, 3, 1)
        self.elevator.floor = 2
        self.elevator.add_list(cases)
        self.assertEqual(self.elevator.floor_actions(), results)


if __name__ == '__main__':
    unittest.main()

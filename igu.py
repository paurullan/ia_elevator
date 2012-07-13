#!/usr/bin/env python 
# -*- coding: utf-8 -*-

__version__ = "0.0.1"

import elevator

from PyQt4 import *
from PyQt4.QtCore import *
from PyQt4.QtGui import *

class MainWindow(QWidget):
    """Classe del widget principal. No cal fer una finestra principal perquè no
    tenim menus ni semblants"""

    def __init__(self):
        super(MainWindow, self).__init__()
        self.elev = elevator.Elevator(6, 0)
        self.connect(self.elev, SIGNAL("update()"), self.update)

        self.elevator = ElevatorWidget(self.elev)
        self.demo = DemoWidget(self.elev)

        exit_button = QPushButton("Tanca")
        exit_button.setIcon(QIcon("img/exit.svg"))
        self.connect(exit_button, SIGNAL("clicked()"), SLOT("close()"))

        control_pane = QVBoxLayout()
        control_pane.addWidget(self.demo)
        control_pane.addStretch()
        control_pane.addWidget(exit_button)

        main_pane = QHBoxLayout()
        main_pane.addWidget(self.elevator)
        main_pane.addStretch()
        main_pane.addLayout(control_pane)
        self.setLayout(main_pane)

        self.timer = QTimer()
        self.connect(self.timer, SIGNAL("timeout()"), self.elev.action)
        self.timer.start(1000)


    def update(self):
        self.elevator.update()
       

class FloorWidget(QGroupBox):
    """Classe del widget de gestió de l'ascensor. Té la lògica interna i desa
    les dades de l'ascensor"""

    def __init__(self, floor, elev):
        super(FloorWidget, self).__init__()
        self.floor = floor
        self.elevator = elev
        if self.floor == 0:
            self.setTitle(QString("PB"))
        else:
            self.setTitle(QString(str(self.floor)))

        self.open = OpenButton(self.floor, elev)
        self.up = UpButton(self.floor, elev)
        self.down = DownButton(self.floor, elev)

        floor_pane = QHBoxLayout()
        floor_pane.addWidget(self.open)
        floor_pane.addWidget(self.up)
        floor_pane.addWidget(self.down)
        self.setLayout(floor_pane)

    def update(self):
        self.open.update()
        self.up.update()
        self.down.update()

    def remove_down(self):
        """Desactiva la possibilitat d'anar per amunt. Necessari pel pis
        d'adalt del tot"""
        self.down.setEnabled(False)
        self.down.never_on = True
        self.down.setIcon(QIcon("img/empty.svg"))

    def remove_up(self):
        """Desactiva la possibilitat d'anar per avall. Necessari pel pis
        d'abaix"""
        self.up.setEnabled(False)
        self.up.never_on = True
        self.up.setIcon(QIcon("img/empty.svg"))

class ElevatorActionButton(QToolButton):
    """Botó de l'acció per introduir estímuls a l'ascensor. Està fet de tal
    manera que sigui molt senzill per generar subclasses d'obrir, pujar i
    baixar.

    El «never_on» serveix per posar els pisos inferior i superior desconnectats
    per no poder pujar i baixar més."""

    def __init__(self, floor, elev, action):
        super(ElevatorActionButton, self).__init__()
        self.setAutoRaise(True)
        self.floor = floor
        self.action = action
        self.elevator = elev
        self.connect(self, SIGNAL("clicked()"), self.do)
        filename = "img/%s.svg" % action
        self.setIcon(QIcon(filename))
        self.never_on = False

    def do(self):
        self.elevator.add_list([(self.floor, self.action)])
        self.setEnabled(False)

    def update(self):
        """Actualitza l'estat del botó segons si l'acció està pendent a processar"""
        super(ElevatorActionButton, self).update()
        if self.never_on:
            return
        present = self.elevator.present((self.floor, self.action))
        self.setEnabled(not present)


class OpenButton(ElevatorActionButton):

    def __init__(self, floor, elev):
        super(OpenButton, self).__init__(floor, elev, "open")

class UpButton(ElevatorActionButton):

    def __init__(self, floor, elev):
        super(UpButton, self).__init__(floor, elev, "up")

class DownButton(ElevatorActionButton):

    def __init__(self, floor, elev):
        super(DownButton, self).__init__(floor, elev, "down")


class ElevatorWidget(QWidget):
    """Classe del widget de gestió de l'ascensor. Té la lògica interna i desa
    les dades de l'ascensor"""

    def __init__(self, elev):
        super(ElevatorWidget, self).__init__()
        self.elevator = elev

        self.elevator_anim = ElevatorAnimation(self.elevator)

        elevator_buttons = QVBoxLayout()
        self.buttons = [FloorWidget(x, elev) for x in range(self.elevator.n_floors)]
        self.buttons[0].remove_down()
        self.buttons[-1].remove_up()
        self.buttons.reverse()
        [elevator_buttons.addWidget(x) for x in self.buttons]

        elevator_pane = QHBoxLayout()
        elevator_pane.addWidget(self.elevator_anim)
        elevator_pane.addLayout(elevator_buttons)
        self.setLayout(elevator_pane)
        self.update()


    def update(self):
        self.elevator_anim.update()
        for i in self.buttons:
            i.update()




class DemoWidget(QGroupBox):
    """Classe del widget de gestió de l'ascensor. Té la lògica interna i desa
    les dades de l'ascensor"""

    def __init__(self, elev):
        super(DemoWidget, self).__init__()
        cadena_titol = self.trUtf8("Demonstracions d'execució")
        self.setTitle(cadena_titol)
        cases = []
        cases.append(("Cridades internes",
                  [(0, "open"), (1,"open"), (2,"open"), 
                   (3,"open"), (4,"open"), (5,"open")]))
        cases.append(("Pujada simple",
                  [(2, "up"), (3, "open")]))
        cases.append(("Baixada simple",
                  [(4, "down"), (3, "open")]))
        cases.append(("Tot pujades",
                  [(0, "up"), (1, "up"), (2, "up"), (3, "up"), (4, "up")]))
        cases.append(("Tot baixades",
                  [(1, "down"), (2, "down"), (3, "down"), 
                   (4, "down"), (5,"down")]))
        cases.append(("Adalt des del mig",
                  [(2, "up"), (4, "up")]))
        cases.append(("Abaix des del mig",
                  [(2, "down"), (4, "down")]))
        cases.append(("Mescla des del mig",
                  [(1, "up"), (2, "open"), (3, "down"), 
                   (4, "up"), (5, "open")]))
        cases.append(("Cas complexe des del mig",
                  [(1, "up"), (2, "down"), (4, "up"), (5, "down")]))
        cases.append(("Conflicte de portes",
                  [(3, "open"), (3, "up"), (3, "down"), 
                   (4, "open"), (1, "open")]))
        buttons = [DemoButton(i, elev) for i in cases]
        demo_pane = QVBoxLayout()
        for i in buttons:
            demo_pane.addWidget(i)
        self.setLayout(demo_pane)


class DemoButton(QPushButton):
    """Classe del widget de gestió de l'ascensor. Té la lògica interna i desa
    les dades de l'ascensor"""

    def __init__(self, case, elev):
        title, actions = case[0], case[1]
        super(DemoButton, self).__init__()
        self.setText(QString(title))
        self.elevator = elev
        self.actions = actions
        self.connect(self, SIGNAL("clicked()"), self.add_actions)

    def add_actions(self):
        self.elevator.add_list(self.actions)




class ElevatorAnimation(QGraphicsView):
    """Animació de l'ascensor. El «delta» són els milisegons d'acció i
    transició d'obrir portes."""
    def __init__(self, elev):
        super(ElevatorAnimation, self).__init__()
        self.elevator = elev
        self.delta = 1*1000
        # tamany d'una cel.lla, com si fos una casella
        self.cell = 64

        self.max_width = self.cell*3
        self.max_height = self.cell*self.elevator.n_floors
        self.scene = QGraphicsScene(0, 0, self.max_width, self.max_height)
        self.setScene(self.scene)

        self.populate()

        self.animator = QTimer()
        self.animator.setInterval(self.delta)
        self.animator.timeout.connect(self.animate)
        self.update()


    def update(self):
        self.animate()


    def populate(self):
        """Posa els elements dins l'animació"""
        #self.pos = self.max_height - self.cell, self.cell

        pixmap = QPixmap("img/elevator.svg").scaledToHeight(self.cell)
        self.elev_back = QGraphicsPixmapItem(pixmap)
        pixmap = QPixmap("img/elevator_left.svg").scaledToHeight(self.cell)
        self.elev_left = QGraphicsPixmapItem(pixmap)
        pixmap = QPixmap("img/elevator_right.svg").scaledToHeight(self.cell)
        self.elev_right = QGraphicsPixmapItem(pixmap)
        pixmap = QPixmap("img/elevator_closed.svg").scaledToHeight(self.cell)
        self.elev_closed = QGraphicsPixmapItem(pixmap)
        # l.setZValue(-100)


        self.scene.addItem(self.elev_back)
        self.scene.addItem(self.elev_left)
        self.scene.addItem(self.elev_right)
        self.scene.addItem(self.elev_closed)
        self.elev_back.setVisible(False)
        self.elev_left.setVisible(False)
        self.elev_right.setVisible(False)
        self.elev_closed.setVisible(False)


    def animate(self):
        action = self.elevator.last
        if action == "up" or action == "down":
            self.animate_up_down()
        elif action == "open":
            self.animate_open()
        elif action == "close":
            self.animate_close()
        elif action == "wait":
            self.animate_wait()
        elif action == "init":
            self.animate_init()
        else:
            raise NotImplementedError

    def animate_to(self, when, item, x, y):
        animation = QGraphicsItemAnimation()
        timeline = QTimeLine(self.delta)
        timeline.setFrameRange(0, 60)
        animation.setPosAt(when, QPointF(x, y))
        animation.setItem(item)
        animation.setTimeLine(timeline)
        return animation

    def animate_open(self):
        self.elev_back.setPos(*self.pos)
        self.elev_left.setPos(*self.pos)
        self.elev_right.setPos(*self.pos)

        self.elev_closed.setVisible(False)
        self.elev_back.setVisible(True)
        self.elev_left.setVisible(True)
        self.elev_right.setVisible(True)
        self.anim_left = self.animate_to(0.2, self.elev_left, \
                                        self.cell*2, self.calc_where())
        self.anim_right = self.animate_to(0.2, self.elev_right, \
                                        0, self.calc_where())
        self.anim_left.timeLine().start()
        self.anim_right.timeLine().start()
        self.animator.start()

    def animate_wait(self):
        pass

    def animate_close(self):
        self.elev_closed.setVisible(False)
        self.elev_back.setVisible(True)
        self.elev_left.setVisible(True)
        self.elev_right.setVisible(True)
        self.anim_left = self.animate_to(0.2, self.elev_left, \
                                        self.cell, self.calc_where())
        self.anim_right = self.animate_to(0.2, self.elev_right, \
                                              self.cell, self.calc_where())
        self.anim_left.timeLine().start()
        self.anim_right.timeLine().start()
        self.animator.start()


    def animate_init(self):
        self.elev_closed.setVisible(True)
        self.elev_back.setVisible(False)
        self.elev_left.setVisible(False)
        self.elev_right.setVisible(False)
        self.anim = self.animate_to(0.2, self.elev_closed, \
                                        self.cell, self.calc_where())
        self.anim.timeLine().start()
        self.animator.start()

    def animate_up_down(self):
        self.elev_closed.setVisible(True)
        self.elev_back.setVisible(False)
        self.elev_left.setVisible(False)
        self.elev_right.setVisible(False)
        self.anim = self.animate_to(0.2, self.elev_closed, \
                                        self.cell, self.calc_where())
        self.anim.timeLine().start()
        self.animator.start()


    @property
    def pos(self):
        return self.cell, self.calc_where()

    def calc_where(self):
        offset = self.elevator.n_floors - (self.elevator.floor + 1)
        return self.cell * offset

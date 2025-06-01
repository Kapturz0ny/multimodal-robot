#!/usr/bin/env python3

from time import sleep, time
from enum import Enum

from ev3dev2.motor import (
    LargeMotor,
    MediumMotor,
    OUTPUT_A,
    OUTPUT_B,
    OUTPUT_D,
    SpeedPercent,
)
from ev3dev2.sensor import INPUT_1, INPUT_3, INPUT_4
from ev3dev2.sensor.lego import TouchSensor, ColorSensor


class LeftSideDetected(Exception):
    """Wykrycie zjazdu z lewej strony."""

    def __init__(self, *args):
        super().__init__(*args)


class RightSideDetected(Exception):
    """Wykrycie zjazdu z prawej strony."""

    def __init__(self, *args):
        super().__init__(*args)


class PackageAreaDetected(Exception):
    """Wykrycie strefy paczki."""

    def __init__(self, *args):
        super().__init__(*args)


class StopButtonPressed(Exception):
    """Sygnał zatrzymania programu."""

    def __init__(self, *args):
        super().__init__(*args)


class Task(Enum):
    # LINE_FOLLOWER = 0
    PICK_UP = 1
    DROP_OFF = 2


csensor_left = ColorSensor(INPUT_1)
csensor_right = ColorSensor(INPUT_4)
touch = TouchSensor(INPUT_3)

left_motor = LargeMotor(OUTPUT_A)
right_motor = LargeMotor(OUTPUT_B)
hook = MediumMotor(OUTPUT_D)

BASE_SPEED = 22
STRAIGHT_MULTIPLIER = 1.5
STEP = 0.01
BLACK_COLOR = ColorSensor.COLOR_BLACK
PICK_COLOR = ColorSensor.COLOR_GREEN
DROP_COLOR = ColorSensor.COLOR_RED


def is_color(sensor, color):
    """Sprawdza, czy wybrany czujnik wykrył podany kolor."""
    return sensor.color == color


def rotate_left(speed, time):
    """Obraca robota w lewo przez podany czas."""
    left_motor.on(SpeedPercent(-speed))
    right_motor.on(SpeedPercent(0))
    sleep(time)


def rotate_right(speed, time):
    """Obraca robota w prawo przez podany czas."""
    left_motor.on(SpeedPercent(0))
    right_motor.on(SpeedPercent(-speed))
    sleep(time)


def go_back(speed, time):
    """Jedź do tyłu przez podany czas."""
    left_motor.on(SpeedPercent(-speed))
    right_motor.on(SpeedPercent(-speed))
    sleep(time)


def go_fwd(time):
    """Jedź do przodu przez podany czas."""
    left_motor.on(SpeedPercent(BASE_SPEED))
    right_motor.on(SpeedPercent(BASE_SPEED))
    sleep(time)


def rotate_90(is_right):
    """Obrót o 90 stopni w lewo/prawo. Ponieważ czujniki kolorów znajdują się minimalnie przed osią kół, robot podjeżdza lekko do przodu przed wykonaniem obrotu."""
    left_motor.on(SpeedPercent(BASE_SPEED))
    right_motor.on(SpeedPercent(BASE_SPEED))
    sleep(0.3)
    turn = 1 if is_right else -1
    left_motor.on(SpeedPercent(BASE_SPEED * turn))
    right_motor.on(SpeedPercent(BASE_SPEED * -turn))
    sleep(0.9)


def rotate_75(is_right):
    """Obrót o 75 stopni w lewo/prawo. Ponieważ czujniki kolorów znajdują się minimalnie przed osią kół, robot podjeżdza lekko do przodu przed wykonaniem obrotu."""
    left_motor.on(SpeedPercent(BASE_SPEED))
    right_motor.on(SpeedPercent(BASE_SPEED))
    sleep(0.3)
    turn = 1 if is_right else -1
    left_motor.on(SpeedPercent(BASE_SPEED * turn))
    right_motor.on(SpeedPercent(BASE_SPEED * -turn))
    sleep(0.7)


def rotate_180():
    """Obrót o 180 stopni."""
    left_motor.on(SpeedPercent(BASE_SPEED))
    right_motor.on(SpeedPercent(-BASE_SPEED))
    sleep(1.9)


def go_fwd_to_line(color):
    """Wróć na trasę - zjedź z kolorowej strefy (paczki)."""
    left_color_match = True
    right_color_match = True
    while left_color_match or right_color_match:
        left_color_match = is_color(csensor_left, color)
        right_color_match = is_color(csensor_right, color)
        left_motor.on(SpeedPercent(BASE_SPEED))
        right_motor.on(SpeedPercent(BASE_SPEED))
        sleep(0.03)


def raise_obj():
    """Podnieś hak"""
    hook.on(SpeedPercent(40))
    sleep(0.25)
    hook.on(SpeedPercent(0))


def lower_obj():
    """Opuść hak"""
    hook.on(SpeedPercent(-40))
    sleep(0.25)
    hook.on(SpeedPercent(0))


def pick_up_object():
    """Wykonaj fazę odbioru paczki"""
    go_fwd(0.75)
    raise_obj()
    rotate_180()
    go_fwd_to_line(PICK_COLOR)


def drop_off_object():
    """Wykonaj fazę odstawienia paczki"""
    go_fwd(0.7)
    lower_obj()
    go_back(BASE_SPEED, 0.7)
    rotate_180()
    go_fwd_to_line(DROP_COLOR)


def line_follower():  # uruchamia podążanie za linią bez tranportera
    try:
        follow_line(BLACK_COLOR)
    except StopButtonPressed:
        return False


def transporter():  # główna funkcja transportera
    task = Task.PICK_UP
    is_right = True
    while True:
        if task == Task.PICK_UP:  # etap jazdy po paczkę
            task = Task.DROP_OFF

            # jedź za linią aż natrafisz na kolorowy zjazd
            try:
                follow_line(BLACK_COLOR, PICK_COLOR)
            except LeftSideDetected:
                is_right = False
            except RightSideDetected:
                is_right = True
            except PackageAreaDetected:
                pass
            except StopButtonPressed:
                return False

            # skręt w kolorowy zjazd
            print("ROTATE TO BOX PATH")
            left_motor.on(SpeedPercent(BASE_SPEED))
            right_motor.on(SpeedPercent(BASE_SPEED))
            sleep(0.3)
            rotate_90(is_right)

            # jazda do strefy odbioru paczki
            running = True
            while running:
                try:
                    follow_line(BLACK_COLOR, PICK_COLOR)
                except LeftSideDetected:
                    rotate_left(BASE_SPEED, STEP * 15)
                    pass
                except RightSideDetected:
                    rotate_right(BASE_SPEED, STEP * 15)
                    pass
                except PackageAreaDetected:
                    # odbierz paczkę
                    pick_up_object()
                    running = False
                except StopButtonPressed:
                    return False

            print("BOX COLLECTED")

            # wróć do głównej trasy
            running = True
            while running:
                try:
                    follow_line(BLACK_COLOR, PICK_COLOR, back_to_line=True)
                except LeftSideDetected:
                    rotate_left(BASE_SPEED, STEP * 15)
                    pass
                except RightSideDetected:
                    rotate_right(BASE_SPEED, STEP * 15)
                    pass
                except PackageAreaDetected:  # detected black line
                    running = False
                    print("BACK TO LINE CONFIRMED")
                except StopButtonPressed:
                    return False

            # skręć na główną trasę
            rotate_75(is_right)
            print("ROTATE 75")

        elif task == Task.DROP_OFF:  # etap dostarczania paczki
            task = Task.PICK_UP
            print("STARTED DROP OFF")

            # jedź do kolorowego zjazdu
            try:
                follow_line(BLACK_COLOR, DROP_COLOR)
            except LeftSideDetected:
                is_right = False
            except RightSideDetected:
                is_right = True
            except PackageAreaDetected:
                pass
            except StopButtonPressed:
                return False

            # skręć w kolorowy zjazd
            print("ROTATE 90")
            rotate_90(is_right)

            # jedź do strefy rozładunku
            running = True
            while running:
                try:
                    follow_line(BLACK_COLOR, DROP_COLOR)
                except LeftSideDetected:
                    rotate_left(BASE_SPEED, STEP * 15)
                    pass
                except RightSideDetected:
                    rotate_right(BASE_SPEED, STEP * 15)
                    pass
                except PackageAreaDetected:
                    drop_off_object()
                    return False  # zatrzymuje program po odstawieniu paczki
                    # można usunąć aby robot dalej kontyuuował jazdę
                    running = False
                except StopButtonPressed:
                    return False

            print("BOX DELIVERED")

            # wróć do głównej trasy
            running = True
            while running:
                try:
                    follow_line(BLACK_COLOR, DROP_COLOR, back_to_line=True)
                except LeftSideDetected:
                    rotate_left(BASE_SPEED, STEP * 15)
                    pass
                except RightSideDetected:
                    rotate_right(BASE_SPEED, STEP * 15)
                    pass
                except PackageAreaDetected:  # detected black line
                    running = False
                except StopButtonPressed:
                    return False

            # skręć do głównej trasy
            print("ROTATE 75")
            rotate_75(is_right)


# zmodyfikowany kod line followera o argument drugiego koloru (kolor zjazdu)
# oraz o flagę, czy wraca do głównej trasy (pozwala to na odróżnienie trasy od skrzyżowania)
def follow_line(color, snd_color=None, back_to_line=False):
    straight_counter = 30
    speed = 20
    while True:
        if touch.is_pressed:  # obsługa zatrzymania kodu
            sleep(0.5)
            raise StopButtonPressed

        left_color_match = is_color(csensor_left, color)
        right_color_match = is_color(csensor_right, color)

        print("\nCOLORS:")
        print(csensor_left.color)
        print(csensor_right.color)

        if straight_counter > 30:
            speed = STRAIGHT_MULTIPLIER * BASE_SPEED  # prędkość na prostych
            go_back_steps = 10
        else:
            speed = BASE_SPEED  # prędkość na zakrętach
            go_back_steps = 5

        # wykryty dodatkowy kolor na obu czujnikach
        if is_color(csensor_left, snd_color) and is_color(csensor_right, snd_color):
            raise PackageAreaDetected

        # kolorwy zjaz z lewej strony
        elif is_color(csensor_left, snd_color):
            print("csensor_left.color: ", csensor_left.color)
            print("snd_color: ", snd_color)
            print("LEFT COLORED EXIT")
            if is_color(csensor_right, color):
                raise PackageAreaDetected
            go_back(speed, STEP * go_back_steps)
            raise LeftSideDetected

        # kolorwy zjaz z prawej strony
        elif is_color(csensor_right, snd_color):
            print("csensor_right.color: ", csensor_right.color)
            print("snd_color: ", snd_color)
            print("RIGHT COLORED EXIT SKRĘT")
            if is_color(csensor_left, color):
                raise PackageAreaDetected
            go_back(speed, STEP * go_back_steps)
            raise RightSideDetected

        # stan jedź prosto
        if not left_color_match and not right_color_match:
            print("STRAIIGHT")
            straight_counter += 1
            left_motor.on(SpeedPercent(speed))
            right_motor.on(SpeedPercent(speed))
            sleep(STEP * 0.3)

        else:
            speed = BASE_SPEED
            if straight_counter > 30:
                if left_color_match and not right_color_match:
                    print("LEFT TURN DETECTED")
                    rotate_left(speed, STEP * 5)

                elif right_color_match and not left_color_match:
                    print("RIGHT TURN DETECTED")
                    rotate_right(speed, STEP * 5)
                go_back(speed, STEP * 20)

            elif straight_counter > 5:
                go_back(speed, STEP * 5)

            straight_counter = 0

            if left_color_match and not right_color_match:
                # Czarna linia po lewej – skręć w lewo
                print("LEFT TURN DETECTED")
                rotate_left(speed, STEP * 15)

            elif right_color_match and not left_color_match:
                # Czarna linia po prawej – skręć w prawo
                print("RIGHT TURN DETECTED")
                rotate_right(speed, STEP * 15)

            else:
                if back_to_line:  # powrót na trasę
                    print("BACK TO LINE")
                    raise PackageAreaDetected

                print("CROSSROADS")
                left_motor.on(SpeedPercent(speed))
                right_motor.on(SpeedPercent(speed))
                sleep(STEP * 16)


def test_func():
    # raise_obj()
    # lower_obj()
    # go_fwd(0.75)
    # go_fwd_to_line(DROP_COLOR)
    # rotate_180()
    # go_back(BASE_SPEED, 0.5)
    # rotate_90(True)
    return False


def run():  # pętla uruchamiająca właściwą funkcję, wspiera obsługę przycisku
    running = False
    if touch.is_pressed:
        running = True
        sleep(0.5)
    while running:
        # running = test_func() # do testowania i kalibrowania funkcji pomocniczych
        # running = line_follower() # samo podążanie za linią bez transportowania paczki (dla testowania)
        running = transporter()


running = False
print("READY")
while True:
    left_motor.off()
    right_motor.off()
    hook.off()
    run()

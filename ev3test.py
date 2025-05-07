#!/usr/bin/env python3

from time import sleep, time

from ev3dev2.motor import LargeMotor, MediumMotor, OUTPUT_A, OUTPUT_B, OUTPUT_D, SpeedPercent

from ev3dev2.sensor import INPUT_1, INPUT_3, INPUT_4
from ev3dev2.sensor.lego import TouchSensor, ColorSensor

BASE_SPEED = 20
STRAIGHT_MULTIPLIER = 2
STEP = 0.01

color_left = ColorSensor(INPUT_1)
color_right = ColorSensor(INPUT_4)
touch = TouchSensor(INPUT_3)

left_motor = LargeMotor(OUTPUT_A)
right_motor = LargeMotor(OUTPUT_B)
hook = MediumMotor(OUTPUT_D)


def is_black(sensor):
    return sensor.color == ColorSensor.COLOR_BLACK


def rotate_left_easy(speed, time):
	left_motor.on(SpeedPercent(-speed))
	right_motor.on(SpeedPercent(0))
	sleep(time)


def rotate_right_easy(speed, time):
	left_motor.on(SpeedPercent(0))
	right_motor.on(SpeedPercent(-speed))
	sleep(time)

def go_back(speed, time):
	left_motor.on(SpeedPercent(-speed))
	right_motor.on(SpeedPercent(-speed))
	sleep(time)


def follow_line():
	straight_counter = 30
	speed = 20
	while True:
		if touch.is_pressed:
			sleep(0.5)
			return False
		left_black = is_black(color_left)
		right_black = is_black(color_right)

		if straight_counter > 30:
			speed = STRAIGHT_MULTIPLIER * BASE_SPEED # prędkość na prostych
		else:
			speed = BASE_SPEED # prędkość na zakrętach
		

		if not left_black and not right_black:
			# stan jedź prosto
			straight_counter += 1
			left_motor.on(SpeedPercent(speed))
			right_motor.on(SpeedPercent(speed))
			sleep(STEP * 0.3) 

		else:
			if straight_counter > 30:
				speed = BASE_SPEED
				if left_black and not right_black:
					rotate_left_easy(speed, STEP * 5)
				elif right_black and not left_black:
					rotate_right_easy(speed, STEP * 5)
				go_back(speed, STEP * 30)
				
			elif straight_counter > 5:
				speed = BASE_SPEED
				go_back(speed, STEP * 5)

			straight_counter = 0
			speed = BASE_SPEED
			# stan na zakręcie
			if left_black and not right_black:
				# Czarna linia po lewej – skręć w lewo
				rotate_left_easy(speed, STEP * 5)


			elif right_black and not left_black:
				# Czarna linia po prawej – skręć w prawo
				rotate_right_easy(speed, STEP * 5)
				
			else:
				# skrzyżowanie lub prosto na łuku
				left_motor.on(SpeedPercent(speed))
				right_motor.on(SpeedPercent(speed))
				sleep(STEP * 16)


def run():
	running = False
	if touch.is_pressed:
		running = True
		sleep(0.5)
	while running:
		running = follow_line()


running = False
print("READY")
while True:
	left_motor.off()
	right_motor.off()
	hook.off()
	run()

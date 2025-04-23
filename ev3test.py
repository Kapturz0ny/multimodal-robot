#!/usr/bin/env python3

from time import sleep

from ev3dev2.motor import LargeMotor, MediumMotor, OUTPUT_A, OUTPUT_B, OUTPUT_D, SpeedPercent

from ev3dev2.sensor import INPUT_1, INPUT_3, INPUT_4
from ev3dev2.sensor.lego import TouchSensor, ColorSensor

color_left = ColorSensor(INPUT_1)
color_right = ColorSensor(INPUT_4)
touch = TouchSensor(INPUT_3)

left_motor = LargeMotor(OUTPUT_A)
right_motor = LargeMotor(OUTPUT_B)
hook = MediumMotor(OUTPUT_D)

base_speed = 10
turn_multiplier = 0.5

def is_black(sensor):
    return sensor.color == ColorSensor.COLOR_BLACK


# def loop(sign, speed):
# 	left_motor.on(sign*speed)
# 	right_motor.on(sign*speed)
# 	# hook.on(sign*speed)
# 	sign = -1 * sign
# 	print('Color 1 ' + str(color_left.rgb) + ' detected as ' + str(color_left.color_name) + '.')
# 	print('Color 2 ' + str(color_right.rgb) + ' detected as ' + str(color_right.color_name) + '.')
# 	print('Button state: ' + str(touch.is_pressed) + '\nRunning' + str(running))
# 	sleep(1.0)


def rotate_left(speed):
	left_motor.on(SpeedPercent(0))
	right_motor.on(SpeedPercent(speed))

def rotate_right(speed):
	left_motor.on(SpeedPercent(speed))
	right_motor.on(SpeedPercent(0))

def follow_line():
	straight_counter = 40
	freq = 0.05
	while True:
		if touch.is_pressed:
			sleep(0.5)
			return False
		left_black = is_black(color_left)
		right_black = is_black(color_right)

		if straight_counter > 40:
			speed = base_speed
			freq = 0.05
		
		else:
			speed = base_speed * turn_multiplier
			freq //= 10
		
		if not left_black and not right_black:
			# stan jedź prosto
			straight_counter += 1
			left_motor.on(SpeedPercent(speed))
			right_motor.on(SpeedPercent(speed))

		else:
			straight_counter = 0
			speed = base_speed * turn_multiplier
			# stan na zakręcie
			if left_black:
				# Czarna linia po lewej – skręć w lewo
				rotate_left(speed)
				
			elif right_black:
				# Czarna linia po prawej – skręć w prawo
				rotate_right(speed)
				
			else:
				# skrzyżowanie lub prosto na łuku
				left_motor.on(SpeedPercent(speed))
				right_motor.on(SpeedPercent(speed))

		sleep(0.005)


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

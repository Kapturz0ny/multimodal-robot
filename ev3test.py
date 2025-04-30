#!/usr/bin/env python3

from time import sleep, time

from ev3dev2.motor import LargeMotor, MediumMotor, OUTPUT_A, OUTPUT_B, OUTPUT_D, SpeedPercent

from ev3dev2.sensor import INPUT_1, INPUT_3, INPUT_4
from ev3dev2.sensor.lego import TouchSensor, ColorSensor

MAX_TURN_SPEED = 25
MAX_SPEED = 50

color_left = ColorSensor(INPUT_1)
color_right = ColorSensor(INPUT_4)
touch = TouchSensor(INPUT_3)

left_motor = LargeMotor(OUTPUT_A)
right_motor = LargeMotor(OUTPUT_B)
hook = MediumMotor(OUTPUT_D)

base_speed = 25
turn_multiplier = 0.5
step = 0.01
rotate_time = 1

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

def rotate_left_hard():
	while is_black(color_left):
		left_motor.on(SpeedPercent(-MAX_TURN_SPEED))
		right_motor.on(SpeedPercent(MAX_TURN_SPEED))


def rotate_right_hard():
	while is_black(color_right):
		left_motor.on(SpeedPercent(MAX_TURN_SPEED))
		right_motor.on(SpeedPercent(MAX_TURN_SPEED))


def follow_line():
	straight_counter = 40
	rotate_counter = 0
	speed = 20
	while True:
		if touch.is_pressed:
			sleep(0.5)
			return False
		left_black = is_black(color_left)
		right_black = is_black(color_right)

		if straight_counter > 30:
			speed = base_speed # prędkość na prostych
		else:
			speed = base_speed * turn_multiplier # prędkość na zakrętach
		

		if not left_black and not right_black:
			# stan jedź prosto
			straight_counter += 1
			rotate_counter = 0
			left_motor.on(SpeedPercent(speed))
			right_motor.on(SpeedPercent(speed))
			sleep(step)

		else:
			if straight_counter > 30:
				speed = base_speed * turn_multiplier
				go_back(speed, 0.1)

			straight_counter = 0
			speed = base_speed * turn_multiplier
			# stan na zakręcie
			if left_black:
				print("left")
				# Czarna linia po lewej – skręć w lewo
				rotate_counter += 1
				if rotate_counter > rotate_time / step:
					# rotate_left_hard(speed, step)
					pass
				else:
					rotate_left_easy(speed, step)


			elif right_black:
				print("right")
				# Czarna linia po prawej – skręć w prawo
				rotate_counter += 1
				if rotate_counter > rotate_time / step:
					# rotate_right_hard(speed, step)
					pass
				else:
					rotate_right_easy(speed, step)
				
			else:
				print("crossroads")
				# skrzyżowanie lub prosto na łuku
				left_motor.on(SpeedPercent(speed))
				right_motor.on(SpeedPercent(speed))
				sleep(step)



def run():
	running = False
	if touch.is_pressed:
		running = True
		sleep(0.5)
	while running:
		running = follow_line()
    

# def measure_rotate_time():
# 	speed = 20
# 	start = time()
# 	sleep(0.5)
# 	left_motor.on(SpeedPercent(-speed))
# 	right_motor.on(SpeedPercent(speed))
# 	if is_black(color_left) and is_black(color_right):
# 		stop = time()
# 		print("time elapsed: ", stop-start)
# 		left_motor.off()
# 		right_motor.off()

running = False
print("READY")
while True:
	left_motor.off()
	right_motor.off()
	hook.off()
	run()

#!/usr/bin/env python3

from time import sleep, time
from enum import Enum

from ev3dev2.motor import LargeMotor, MediumMotor, OUTPUT_A, OUTPUT_B, OUTPUT_D, SpeedPercent

from ev3dev2.sensor import INPUT_1, INPUT_3, INPUT_4
from ev3dev2.sensor.lego import TouchSensor, ColorSensor

# BASE_SPEED , 0.5 sleep = 45 rotation

class LeftSideDetected(Exception):
	def __init__(self, *args):
		super().__init__(*args)

class RightSideDetected(Exception):
	def __init__(self, *args):
		super().__init__(*args)

class PackageAreaDetected(Exception):
	def __init__(self, *args):
		super().__init__(*args)

class StopButtonPressed(Exception):
	def __init__(self, *args):
		super().__init__(*args)

class Task(Enum):
	LINE_FOLLOWER = 0
	PICK_UP = 1
	DROP_OFF = 2

csensor_left = ColorSensor(INPUT_1)
csensor_right = ColorSensor(INPUT_4)
touch = TouchSensor(INPUT_3)

left_motor = LargeMotor(OUTPUT_A)
right_motor = LargeMotor(OUTPUT_B)
hook = MediumMotor(OUTPUT_D)

BASE_SPEED = 20
STRAIGHT_MULTIPLIER = 1
STEP = 0.01
BLACK_COLOR = ColorSensor.COLOR_BLACK
PICK_COLOR = ColorSensor.COLOR_GREEN
DROP_COLOR = ColorSensor.COLOR_RED

def is_black(sensor):
    return sensor.color == BLACK_COLOR

def is_color(sensor, color):
	return sensor.color == color


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

def go_fwd(time):
	left_motor.on(SpeedPercent(BASE_SPEED))
	right_motor.on(SpeedPercent(BASE_SPEED))
	sleep(time)
	
def rotate_90(is_right):
	left_motor.on(SpeedPercent(BASE_SPEED))
	right_motor.on(SpeedPercent(BASE_SPEED))
	sleep(0.3)
	turn = 1 if is_right else -1
	left_motor.on(SpeedPercent(BASE_SPEED*turn))
	right_motor.on(SpeedPercent(BASE_SPEED*-turn))
	sleep(0.9)

def rotate_180():
	left_motor.on(SpeedPercent(BASE_SPEED))
	right_motor.on(SpeedPercent(-BASE_SPEED))
	sleep(1.9)

def go_fwd_to_line(color):
	left_color_match = True
	right_color_match = True
	while left_color_match or right_color_match:
		left_color_match = is_color(csensor_left, color)
		right_color_match = is_color(csensor_right, color)
		left_motor.on(SpeedPercent(BASE_SPEED))
		right_motor.on(SpeedPercent(BASE_SPEED))
		sleep(0.03)

def raise_obj():
	hook.on(SpeedPercent(40))
	sleep(0.25)
	hook.on(SpeedPercent(0))

def lower_obj():
	hook.on(SpeedPercent(-40))
	sleep(0.25)
	hook.on(SpeedPercent(0))

def pick_up_object():
	# drive fwd, raise object, turn 180, drive to edge
	go_fwd(0.75)
	raise_obj()
	rotate_180()
	go_fwd_to_line(PICK_COLOR)

def drop_off_object():
	# drive fwd, lower object, turn 180, drive to edge
	go_fwd(0.7)
	lower_obj()
	go_back(BASE_SPEED, 0.7)
	rotate_180()
	go_fwd_to_line(DROP_COLOR)
	
def line_follower():
	try:
		follow_line(BLACK_COLOR)
	except StopButtonPressed:
		return False

def transporter():
	task = Task.PICK_UP
	is_right = True
	while True:
		if task == Task.PICK_UP:
			try:
				follow_line(BLACK_COLOR, PICK_COLOR)
			except LeftSideDetected:
				is_right=False
			except RightSideDetected:
				is_right=True
			except PackageAreaDetected:
				pass
			except StopButtonPressed:
				return False
			
			print("ROTATE BOX")
			rotate_90(is_right)
			
			xdd = True
			while xdd:
				try:
					follow_line(BLACK_COLOR, PICK_COLOR)
				except LeftSideDetected:
					rotate_left_easy(BASE_SPEED, STEP * 5)
				except RightSideDetected:
					rotate_right_easy(BASE_SPEED, STEP * 5)
				except PackageAreaDetected:
					pick_up_object()
					xdd = False
				except StopButtonPressed:
					return False
			
			print("PACZKA ODEBRANA")
			xdd = True
			while xdd:	
				try:
					follow_line(BLACK_COLOR, PICK_COLOR, back_to_line=True)
				except LeftSideDetected:
					rotate_left_easy(BASE_SPEED, STEP * 5)
				except RightSideDetected:
					rotate_right_easy(BASE_SPEED, STEP * 5)
				except PackageAreaDetected: # detected black line
					xdd = False
				except StopButtonPressed:
					return False
			
			print("ROTATE 90")
			rotate_90(is_right)
			
			task = Task.DROP_OFF

		elif task == Task.DROP_OFF:
			print("STARTED DROP OFF")
			try:
				follow_line(BLACK_COLOR, DROP_COLOR)
			except LeftSideDetected:
				is_right=False
			except RightSideDetected:
				is_right=True
			except PackageAreaDetected:
				pass
			except StopButtonPressed:
				return False
			
			print("ROTATE 90")
			rotate_90(is_right)
			
			xdd = True
			while xdd:
				try:
					follow_line(BLACK_COLOR, DROP_COLOR)
				except LeftSideDetected:
					rotate_left_easy(BASE_SPEED, STEP * 5)
				except RightSideDetected:
					rotate_right_easy(BASE_SPEED, STEP * 5)
				except PackageAreaDetected:
					drop_off_object()
					return False
					xdd = False
				except StopButtonPressed:
					return False

			print("PACZKA ODSTAWIONA")
			xdd = True
			while xdd:	
				try:
					follow_line(BLACK_COLOR, DROP_COLOR, back_to_line=True)
				except LeftSideDetected:
					rotate_left_easy(BASE_SPEED, STEP * 5)
				except RightSideDetected:
					rotate_right_easy(BASE_SPEED, STEP * 5)
				except PackageAreaDetected: # detected black line
					xdd = False
				except StopButtonPressed:
					return False
			
			print("ROTATE 90")
			rotate_90(is_right)
			
			task = Task.PICK_UP

	
def follow_line(color, snd_color=None, back_to_line=False):
	straight_counter = 30
	speed = 20
	while True:
		if touch.is_pressed:
			sleep(0.5)
			raise StopButtonPressed
		left_color_match = is_color(csensor_left, color)
		right_color_match = is_color(csensor_right, color)

		print("\nCOLORS:")
		print(csensor_left.color)
		print(csensor_right.color)

		if straight_counter > 30:
			speed = STRAIGHT_MULTIPLIER * BASE_SPEED # prędkość na prostych
			go_back_steps = 10
		else:
			speed = BASE_SPEED # prędkość na zakrętach
			go_back_steps = 5
		

		if is_color(csensor_left, snd_color) and is_color(csensor_right, snd_color):
			raise PackageAreaDetected

		elif is_color(csensor_left, snd_color):
			print("LEWY KOLOROWY SKRĘT")
			if is_color(csensor_right, color):
				raise PackageAreaDetected
			go_back(speed, STEP * go_back_steps)
			raise LeftSideDetected

		elif is_color(csensor_right, snd_color):
			print("PRAWY KOLOROWY SKRĘT")
			if is_color(csensor_left, color):
				raise PackageAreaDetected
			go_back(speed, STEP * go_back_steps)
			raise RightSideDetected

		if not left_color_match and not right_color_match:
			print("PROSTO")
			# stan jedź prosto
			straight_counter += 1
			left_motor.on(SpeedPercent(speed))
			right_motor.on(SpeedPercent(speed))
			sleep(STEP * 0.3) 

		else:
			if straight_counter > 30:
				speed = BASE_SPEED
				
				if left_color_match and not right_color_match:
					print("LEWO WYKRYTE")
					rotate_left_easy(speed, STEP * 5)
				
				elif right_color_match and not left_color_match:
					print("PRAWO WYKRYTE")
					rotate_right_easy(speed, STEP * 5)
				go_back(speed, STEP * 30)
				
			elif straight_counter > 5:
				speed = BASE_SPEED
				go_back(speed, STEP * 5)

			straight_counter = 0
			speed = BASE_SPEED
			
			if left_color_match and not right_color_match:
				# Czarna linia po lewej – skręć w lewo
				print("LEWO")
				rotate_left_easy(speed, STEP * 5)

			elif right_color_match and not left_color_match:
				# Czarna linia po prawej – skręć w prawo
				if is_color(csensor_left, snd_color):
					raise PackageAreaDetected
				print("PRAWO")
				rotate_right_easy(speed, STEP * 5)
				
			else:
				if back_to_line:
					print("BACK TO LINE")
					raise PackageAreaDetected
				
				print("SKRZYŻOWANIE")
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

def run():
	running = False
	if touch.is_pressed:
		running = True
		sleep(0.5)
	while running:
		# running = test_func()
		# running = line_follower()
		running = transporter()
    

running = False
print("READY")
while True:
	left_motor.off()
	right_motor.off()
	hook.off()
	run()

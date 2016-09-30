#! /usr/bin/env python
# encoding: utf-8

from com.dtmilano.android.viewclient import ViewClient
import os, sys, time

device, serialno = ViewClient.connectToDeviceOrExit(verbose=False)
print "Device initialized... SerialNo: " + serialno

def say(message):
  os.system("say \"" + message + "\"")

def sleep(delay):
  if delay > 0:
    time.sleep(delay)

def plusPoint(point1, point2):
  x1, y1 = point1
  x2, y2 = point2
  return (x1 + x2, y1 + y2)

def drag(start, end, message, delay = 0):
  device.drag(start, end, 500)
  print "Drag " + message
  sleep(delay)

def touch(point, message, delay = 0):
  x, y = point
  device.touch(x, y)
  print "Touch " + message
  sleep(delay)

def takeSnapshot():
  return device.takeSnapshot(reconnect = device.reconnect)

def getColor(point, image = None):
  image = image or takeSnapshot()
  return image.getpixel(point)

def ensureColor(point, color, message, threshold = 0, interval = 0):
  for _ in enumerateEnsureColor(point, color, message, threshold, interval):
    pass

def enumerateEnsureColor(point, color, message, threshold = 0, interval = 0):
  image = takeSnapshot()
  while not compareColor(getColor(point, image), color, threshold):
    print "Ensure " + message
    yield image
    sleep(interval)
    image = takeSnapshot()
  print "Done " + message

def findColor(color, region = ((0, 0), (1920, 1080)), image = None):
  for point in enumerateFindColor(color, region, image):
    return point

def enumerateFindColor(color, region = ((0, 0), (1920, 1080)), image = None):
  image = image or takeSnapshot()
  pixels = image.load()
  for y in xrange(region[0][1], region[1][1]):
    for x in xrange(region[0][0], region[1][0]):
      if compareColor(pixels[x, y], color):
        yield (x, y)

def compareColor(color1, color2, threshold = 0):
  r1, g1, b1, a1 = color1
  r2, g2, b2, a2 = color2
  if threshold > 0:
    return ((r1 - r2) ** 2 + (g1 - g2) ** 2 + (b1 - b2) ** 2) < threshold
  return color1 == color2








DIALOG_POINT = (345, 200)
DIALOG_COLOR = (72, 55, 39, 255)

BATTLE_POINT = (1910, 100)
BATTLE_COLOR = (152, 110, 53, 255)

STAGE_POINT = (1910, 75)
STAGE_COLOR = (120, 71, 29, 255)

def closeDialog(image):
  if compareColor(getColor((725, 625), image), (221, 105, 81, 255)):
    touch((725, 625), "关闭对话框")


def enterType1Step1(section):
  drag((1800, 300), (1800, 1000), "章节")
  drag((1800, 300), (1800, 1000), "章节")
  drag((1800, 300), (1800, 1000), "章节", 1)

  for _ in xrange((section - 1) // 4):
    drag((1800, 800), (1800, 310), "章节", 1)

  point = (1800, 300 + 150 * ((section - 1) % 4))
  touch(point, "章节" + str(section), 1)
  for image in enumerateEnsureColor(DIALOG_POINT, DIALOG_COLOR, "对话框"):
    closeDialog(image)
  enterType1Step2()

def enterType1Step2():
  touch((700, 350), "困难", 1)
  touch((1450, 800), "探索", 5)
  for image in enumerateEnsureColor(STAGE_POINT, STAGE_COLOR, "进入章节"):
    closeDialog(image)

def battleType1(section):
  times = 0
  for image in enumerateEnsureColor(BATTLE_POINT, BATTLE_COLOR, "进入战场", 100):
    times += 1

    closeDialog(image)

    region = ((0, 300), (1920, 800))

    if compareColor(getColor((1910, 200), image), (111, 70, 29, 255)):
      say("mission complete")
      enterType1Step1(section)

    if compareColor(getColor((345, 200), image), (72, 55, 38, 255)):
      enterType1Step2()

    if not compareColor(getColor((1500, 970), image), (69, 86, 214, 255)):
      touch((1500, 970), "自动准备")

    point = findColor((239, 16, 16, 255), region, image) # 首领
    if point:
      touch(point, "选择首领")
      continue

    point = findColor((144, 144, 185, 255), region, image) # 喽啰
    if point:
      touch(point, "选择喽啰")
      continue

    point = findColor((255, 244, 211, 255), region, image) # 奖励
    if point:
      touch(point, "收取奖励", 2)
      touch(STAGE_POINT, "收取奖励")
      continue

    if times % 10 < 5:
      drag((800, 500), (200, 500), "寻找怪物")
    else:
      drag((200, 500), (800, 500), "寻找怪物")

  for image in enumerateEnsureColor(STAGE_POINT, STAGE_COLOR, "离开战场"):
    closeDialog(image)
    touch(STAGE_POINT, "离开战场")

def startType1(section):
  if compareColor(getColor((1910, 200)), (111, 70, 29, 255)):
    enterType1Step1(section)
  while True:
    battleType1(section)

def battleType2(point):
  for image in enumerateEnsureColor(BATTLE_POINT, BATTLE_COLOR, "进入战场", 100):
    closeDialog(image)

    if compareColor(getColor((1726, 820), image), (255, 242, 206, 255), 100):
      touch((1726, 820), "准备", 2)
      continue

    if not findColor((244, 178, 95, 255), (point, plusPoint(point, (300, 200))), image):
      touch(point, "选择对手", 1)
      continue

    touch(plusPoint(point, (120, 210)), "攻击", 1)

  for image in enumerateEnsureColor((1600, 75), (72, 55, 38, 255), "离开战场"):
    closeDialog(image)
    touch((1600, 75), "离开战场")

def startType2():
  image = takeSnapshot()
  for y in (167, 345, 523):
    for x in (470, 960, 1450):
      point = (x, y)
      print "选择对手 " + str(point)
      if compareColor(getColor(point, image), (203, 194, 178, 255), 100):
        battleType2((x, y))
        image = takeSnapshot()
  say("mission complete")

def startType3():
  while True:
    touch((1470, 900), "开始战斗")
    touch((1750, 850), "准备")
    touch((1210, 650), "继续组队")






# 第一章
startType1(10)

# 结界突破
# startType2()

# 组队
# startType3()






# while True:
#   print getColor((1500, 970))
#   sleep(1)

# print findColor((244, 225, 215, 255), ((1090, 370), (1300, 460)))

# color = getColor((900, 167))
# print color
# for point in enumerateFindColor(color):
#   print point

# def inRegion(point, region):
#   return point[0] > region[0][0] and point[1] > region[0][1] and point[0] < region[1][0] and point[1] < region[1][1]

# def findBestMatchColor(region):
#   image = takeSnapshot()
#   pixels = image.load()
#   colors = {}
#   for y in xrange(region[0][1], region[1][1]):
#     for x in xrange(region[0][0], region[1][0]):
#       color = pixels[x, y]
#       if color in colors:
#         colors[color] += 1
#       else:
#         colors[color] = 1

#   sorted_items = sorted(colors.items(), key = lambda item: item[1])[::-1]

#   for item in sorted_items:
#     point = findColor(item[0], image = image)
#     if inRegion(point, region):
#       print item

# findBestMatchColor(((1090, 370), (1300, 460)))

# takeSnapshot().save("snapshots/2.png")

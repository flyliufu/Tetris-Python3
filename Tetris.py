import time
import random
import threading
import os
from tkinter import *
import tkinter.messagebox as messagebox

# 核心模块
class Core():
	mainMatrixBuffer = 2						# 缓冲大小
	row = 20									# 面板格子行数
	column = 15									# 面板格子列数
	matrixRow = row + mainMatrixBuffer			# 矩阵行数
	matrixColumn = column + mainMatrixBuffer	# 矩阵列数

	score = 0			# 分数
	interval = 0.1		# 方块下落速度

	mainMatrix = []		# 主矩阵

	# 方块信息
	tetromino = {
		'I': (((1, 0), (1, 1), (1, 2), (1, 3)), 
			((0, 1), (1, 1), (2, 1), (3, 1))), 
		'O': (((0, 1), (0, 2), (1, 1), (1, 2)), ), 
		'T': (((0, 1), (1, 0), (1, 1), (1, 2)), 
			((0, 1), (1, 1), (1, 2), (2, 1)), 
			((1, 0), (1, 1), (1, 2), (2, 1)), 
			((0, 1), (1, 0), (1, 1), (2, 1))), 
		'L': (((0, 1), (1, 1), (2, 1), (2, 2)), 
			((1, 0), (1, 1), (1, 2), (2, 0)), 
			((0, 0), (0, 1), (1, 1), (2, 1)), 
			((0, 2), (1, 0), (1, 1), (1, 2))), 
		'J': (((0, 1), (1, 1), (2, 0), (2, 1)), 
			((0, 0), (1, 0), (1, 1), (1, 2)), 
			((0, 1), (0, 2), (1, 1), (2, 1)), 
			((1, 0), (1, 1), (1, 2), (2, 2))), 
		'S': (((0, 1), (1, 1), (1, 2), (2, 2)), 
			((0, 1), (0, 2), (1, 0), (1, 1))), 
		'Z': (((0, 1), (1, 1), (1, 0), (2, 0)), 
			((0, 0), (0, 1), (1, 1), (1, 2)))
	}

	# 初始化
	def __init__(self):
		self.initMainMatrix()

	# 主矩阵初始化
	def initMainMatrix(self):
		for i in range(self.matrixRow):	# 矩阵外围一圈为缓冲区
			self.mainMatrix.append([])
			for j in range(self.matrixColumn):
				self.mainMatrix[i].append(0)

	# 生成种子
	def generateSeed(self):
		types = "IOTLJSZ"
		seed = {
			'type': None, 
			'state': None
		}
		seed['type'] = types[random.randint(0, len(types) - 1)]
		seed['state'] = random.randint(0, len(self.tetromino[seed['type']]) - 1)
		return seed

	# 生成一个 dict 形式的方块信息
	def generateTetromino(self, seed):
		block = {
			'x': 1, 
			'y': 7, 
			'type': 'X',
			'state': 0
		}
		matrixInfo = self.tetromino[seed['type']][seed['state']]
		block['type'] = seed['type']
		block['state'] = seed['state']
		return block

	# 将方块写入主矩阵
	def writeTetromino(self, block):
		matrixInfo = self.tetromino[block['type']][block['state']]
		for i in range(4):
			self.mainMatrix[1 + matrixInfo[i][0]][7 + matrixInfo[i][1]] = 1

	# 生成一个 4*4 的 list 形式的方块信息矩阵
	def generateBlockMatrix(self, block):
		matrixInfo = self.tetromino[block['type']][block['state']]
		x = block['x']
		y = block['y']
		BlockMatrix = []

		for i in range(4):
			BlockMatrix.append([])
			for j in range(4):
				BlockMatrix[i].append(0)

		for i in matrixInfo:
			BlockMatrix[i[0]][i[1]] = 1

		return BlockMatrix

	# 获取方块边界信息
	def getAllBorder(self, block):
		matrixInfo = self.tetromino[block['type']][block['state']]
		border_all = {
			'l_min': matrixInfo[0][1], 
			'r_max': matrixInfo[0][1], 
			'bottom_max': matrixInfo[0][0], 
			'Left': [], 
			'Right': [], 
			'bottom': []
		}

		row_i = [[], [], [], []]	# 区分每行的信息
		column_i = [[], [], [], []]	# 区分每列的信息
		for i in range(4):
			for j in range(4):
				if matrixInfo[j][0] == i:
					row_i[i].append(matrixInfo[j])
				if matrixInfo[j][1] == i:
					column_i[i].append(matrixInfo[j])

		for i in range(4):
			# 若该行不为空
			if len(row_i[i]) != 0:
				sorted_column = sorted(row_i[i], key = lambda e: e[1])	# 按 y 值排序
				border_all['Left'].append(sorted_column[0])
				border_all['Right'].append(sorted_column[len(sorted_column) - 1])
				if sorted_column[0][1] < border_all['l_min']:
					border_all['l_min'] = sorted_column[0][1]
				if sorted_column[len(sorted_column) - 1][1] > border_all['r_max']:
					border_all['r_max'] = sorted_column[len(sorted_column) - 1][1]
				if i > border_all['bottom_max']:
					border_all['bottom_max'] = i
			# 若该列不为空
			if len(column_i[i]) != 0:
				sorted_row = sorted(column_i[i], key = lambda e: e[0])	# 按 x 值排序
				border_all['bottom'].append(sorted_row[len(sorted_row) - 1])

		return border_all

	# 移动检测函数
	def moveCheck(self, block, direction):
		matrixInfo = self.tetromino[block['type']][block['state']]
		x = block['x']
		y = block['y']
		border = self.getAllBorder(block)	# 边界极值信息
		if direction == 'Right':
			if border['r_max'] + y >= self.column:
				return False
			y += 1
			for i in border['Right']:
				if self.mainMatrix[x + i[0]][y + i[1]] == 1:
					return False
		elif direction == 'Left':
			if border['l_min'] + y <= 1:
				return False
			y -= 1
			for i in border['Left']:
				if self.mainMatrix[x + i[0]][y + i[1]] == 1:
					return False
		elif direction == 'Down':
			if border['bottom_max'] + x >= self.row:
				return False
			x += 1
			for i in border['bottom']:
				if self.mainMatrix[x + i[0]][y + i[1]] == 1:
					return False
		return True

	# 移动函数
	def move(self, block, direction, autoDown = False):
		matrixInfo = self.tetromino[block['type']][block['state']]
		x = block['x']
		y = block['y']

		# 右移
		if direction == 'Right':
			if self.moveCheck(block, 'Right') == True:
				for i in range(4):
					self.mainMatrix[x + matrixInfo[i][0]][y + matrixInfo[i][1]] = 0
				y += 1
				block['y'] += 1
				for i in range(4):
					self.mainMatrix[x + matrixInfo[i][0]][y + matrixInfo[i][1]] = 1

		# 左移
		elif direction == 'Left':
			if self.moveCheck(block, 'Left') == True:
				for i in range(4):
					self.mainMatrix[x + matrixInfo[i][0]][y + matrixInfo[i][1]] = 0
				y -= 1
				block['y'] -= 1
				for i in range(4):
					self.mainMatrix[x + matrixInfo[i][0]][y + matrixInfo[i][1]] = 1

		# 下移
		elif direction == 'Down':

			# 手动下移
			if autoDown == False:
				while self.moveCheck(block, 'Down') == True:
					block['x'] += 1
				for i in range(4):
					self.mainMatrix[x + matrixInfo[i][0]][y + matrixInfo[i][1]] = 0
				x = block['x']
				for i in range(4):
					self.mainMatrix[x + matrixInfo[i][0]][y + matrixInfo[i][1]] = 1
				return 1		# 方块以固定

			# 自动下移
			elif autoDown == True:
				if self.moveCheck(block, 'Down') == True:
					block['x'] += 1
				else:
					return 1		# 方块以固定
				for i in range(4):
					self.mainMatrix[x + matrixInfo[i][0]][y + matrixInfo[i][1]] = 0
				x = block['x']
				for i in range(4):
					self.mainMatrix[x + matrixInfo[i][0]][y + matrixInfo[i][1]] = 1

	# 旋转检测函数
	def rotateCheck(self, block):
		x = block['x']
		y = block['y']
		length = len(self.tetromino[block['type']])

		# 原方块参数
		prevState = block['state']
		prevMatrixInfo = self.tetromino[block['type']][prevState]

		# 新方块参数
		newState = (prevState + 1) % length
		newMatrixInfo = self.tetromino[block['type']][newState]
		newBlock = block.copy()
		newBlock['state'] = newState

		border = self.getAllBorder(newBlock)	# 新方块边界极值信息
		if border['r_max'] + y > self.column or \
			border['l_min'] + y < 1 or \
			border['bottom_max'] + x > self.row:
			return False
		for i in range(4):
			self.mainMatrix[x + prevMatrixInfo[i][0]][y + prevMatrixInfo[i][1]] = 0
		for i in range(4):
			if self.mainMatrix[x + newMatrixInfo[i][0]][y + newMatrixInfo[i][1]] == 1:
				for i in range(4):
					self.mainMatrix[x + prevMatrixInfo[i][0]][y + prevMatrixInfo[i][1]] = 1
				return False
		for i in range(4):
			self.mainMatrix[x + prevMatrixInfo[i][0]][y + prevMatrixInfo[i][1]] = 1
		return True

	# 旋转函数
	def rotate(self, block):
		matrixInfo = self.tetromino[block['type']][block['state']]
		x = block['x']
		y = block['y']
		length = len(self.tetromino[block['type']])
		if self.rotateCheck(block) == True:
			state = (block['state'] + 1) % length
			block['state'] = state
			for i in range(4):
				self.mainMatrix[x + matrixInfo[i][0]][y + matrixInfo[i][1]] = 0
			matrixInfo = self.tetromino[block['type']][state]
			for i in range(4):
				self.mainMatrix[x + matrixInfo[i][0]][y + matrixInfo[i][1]] = 1

	# 消除检测 (返回可以被消除的行号)
	def rmRowDetect(self, startRow):
		for i in range(startRow, 0, -1):
			counter = 0
			for j in range(1, self.column + 1):
				if self.mainMatrix[i][j] == 1:
					counter += 1
			if counter == self.column:
				return i 		# 返回行号
			if counter == 0:	# 若为空行，则可停止搜索
				return -1
		return 0

	# 递归消除满行
	def rmRow(self, startRow = 20):
		row = self.rmRowDetect(startRow)
		if row > 0:
			for i in range(row, 0, -1):
				for j in range(1, self.column + 1):
					self.mainMatrix[i][j] = self.mainMatrix[i - 1][j]
			self.score += 1
			self.interval /= 2 ** int(self.score / 10)
			self.rmRow(startRow = row)
		elif row == 0 or row == -1:
			return

	# 失败检测
	def isLose(self):
		for i in range(4):
			for j in range(4):
				if self.mainMatrix[1 + i][7 + j] == 1:
					return True
		return False

	# 在控制台输出矩阵信息(测试用)
	def ConsolePrintMainMatrix(self):
		for i in range(self.matrixRow):
			print(self.mainMatrix[i])


# 控制模块
class Control():

	core = None				# 用于保存核心对象
	block = None			# 用于保存当前方块信息
	nextBlockSeed = None	# 用于保存下一方块种子

	pause = False 			# 存放暂停状态信息

	# 初始化
	def __init__(self, core):
		self.core = core 	# 复制核心对象
		self.nextBlockSeed = self.core.generateSeed()	# 生成第一个方块种子
		self.nextBlock()	# 激活第一个方块

	# 操作函数
	def operation(self, key, autoDown = False):

		# 操作反馈信息
		operationInfo = {
			'isBottom': None, 
			'Exit': False
		}

		# 方向操作
		if self.pause == False:
			# WASD 控制方向
			wasd = {
				'w': 'Up', 
				'a': 'Left', 
				's': 'Down', 
				'd': 'Right'
			}
			if key in wasd:
				key = wasd[key]
			# 移动操作
			if key == 'Right' or \
				key == 'Left' or \
				key == 'Down':
				operationInfo['isBottom'] = self.core.move(self.block, key, autoDown)
				if operationInfo['isBottom'] == 1:
					self.core.rmRow()
					operationInfo['isBottom'] = 1
					return operationInfo
			# 旋转操作
			elif key == 'Up':
				self.core.rotate(self.block)

		# 暂停
		if key == 'p':
			if self.pause == True:
				self.pause = False
			else:
				self.pause = True

		# 退出
		if key == 'Escape':
			self.pause = True
			operationInfo['Exit'] = True
			
		return operationInfo

	# 激活下一方块
	def nextBlock(self):
		self.block = self.generateNextBlock()
		self.nextBlockSeed = self.core.generateSeed()
		self.core.writeTetromino(self.block)

	# 生成下一方块信息
	def generateNextBlock(self):
		return self.core.generateTetromino(self.nextBlockSeed)

	# 获取 4*4 矩阵
	def getBlockMatrix(self, block):
		return self.core.generateBlockMatrix(block)

	# 获取核心参数
	def getParameter(self):
		return {
			'column': self.core.column, 
			'row': self.core.row, 
			'score': self.core.score, 
			'interval': self.core.interval, 
			'mainMatrix': self.core.mainMatrix
		}

	# 返回是否输信息
	def getIsLose(self):
		return self.core.isLose()


# 图像模块
class Graph():

	# 窗体对象
	mainPanel = Tk()
	mainPanel.title("Tetris")		# 标题
	mainPanel.geometry("640x480")	# 窗口大小
	mainPanel.resizable(width = False, height = False)	# 窗体大小不可变

	control = None			# 用于保存控制对象

	autoFallThread = None	# 用于保存自动下落线程

	graphMatrix = []		# 图像面板矩阵
	nextBlockMatrix = []	# 下一方块图像面板矩阵

	# 用于存放暂停提示框
	pauseBox = {
		'rectangle': [], 
		'text': []
	}

	scoreText = None		# 记分板 (面板)

	cv = Canvas(
		mainPanel, 
		bg = 'black', 
		width = 640, 
		height = 480
		)

	def __init__(self, control):

		# 初始化
		self.control = control
		self.initGraph()
		self.initGraphMatrix()

		# 显示方块
		self.draw()
		self.drawNext(self.control.generateNextBlock())

		# 监听键盘事件
		self.mainPanel.bind('<KeyPress>', self.onKeyboardEvent)

		# 建立方块下落线程
		self.autoFallThread = threading.Thread(target = self.autoRun, args = ())
		self.autoFallThread.setDaemon(True)
		self.autoFallThread.start()

		# 进入消息循环
		self.mainPanel.mainloop()
		
	# 界面初始化
	def initGraph(self):

		# 双线主方框
		self.cv.create_rectangle(
			36, 36, 44 + 15 * 20, 44 + 20 * 20, 
			outline = 'lightgray', 
			fill = 'black'
		)
		self.cv.create_rectangle(
			39, 39, 41 + 15 * 20, 41 + 20 * 20,
			outline = 'lightgray', 
			fill = 'black'
		)

		# 下一方块提示框
		self.cv.create_rectangle(
			400, 40, 580, 140, 
			outline = 'white', 
			fill = 'black'
		)
		self.cv.create_text(
			425, 50, 
			text = 'Next:', 
			fill = 'white'
		)

		# 记分板
		self.cv.create_rectangle(
			400, 200, 580, 250, 
			outline = 'white', 
			fill = 'black'
		)
		self.cv.create_text(
			425, 210, 
			text = 'Score:', 
			fill = 'white'
		)
		self.scoreText = self.cv.create_text(
			475, 210, 
			text = str(self.control.getParameter()['score']), 
			fill = 'white'
		)

		# 暂停提示框
		self.pauseBox['rectangle'].append(self.cv.create_rectangle(
			380, 380, 600, 430, 
			outline = 'black', 
			fill = 'black'
		))
		self.pauseBox['rectangle'].append(self.cv.create_rectangle(
			382, 382, 598, 428, 
			outline = 'black', 
			fill = 'black'
		))
		self.pauseBox['text'].append(self.cv.create_text(
			380, 403, 
			text = """
				         Pause
				Press P to continue
			""", 
			fill = 'black'
		))

		self.cv.pack()

	# 图像面板矩阵初始化
	def initGraphMatrix(self):
		parameter = self.control.getParameter()
		# 图像面板矩阵初始化
		for i in range(parameter['row']):	# 矩阵外围一圈为缓冲区
			self.graphMatrix.append([])
			for j in range(parameter['column']):
				rectangle = self.cv.create_rectangle(
					40 + j * 20, 40 + i * 20, 60 + j * 20, 60 + i * 20, 
					outline = '', 
					fill = 'black'
				)
				self.graphMatrix[i].append(rectangle)

		# 下一方块面板矩阵初始化
		x, y = 470, 50		# 参考坐标
		for i in range(4):
			self.nextBlockMatrix.append([])
			for j in range(4):
				rectangle = self.cv.create_rectangle(
					x + j * 20, y + i * 20, x + 20 + j * 20, y + 20 + i * 20, 
					outline = '', 
					fill = 'black'
				)
				self.nextBlockMatrix[i].append(rectangle)

	# 将主矩阵信息映射到图像面板矩阵
	def draw(self):
		parameter = self.control.getParameter()
		for i in range(parameter['row']):
			for j in range(parameter['column']):
				if parameter['mainMatrix'][i + 1][j + 1] == 1:
					self.cv.itemconfig(
						self.graphMatrix[i][j], 
						outline = 'black', 
						fill = 'cyan'
					)
				elif parameter['mainMatrix'][i + 1][j + 1] == 0:
					self.cv.itemconfig(
						self.graphMatrix[i][j], 
						outline = 'black', 
						fill = 'black'
					)

	# 下一方块提示显示
	def drawNext(self, block):
		BlockMatrix = self.control.getBlockMatrix(block)
		for i in range(4):
			for j in range(4):
				if BlockMatrix[i][j] == 1:
					self.cv.itemconfig(
						self.nextBlockMatrix[i][j], 
						outline = 'black', 
						fill = 'cyan'
					)
				else:
					self.cv.itemconfig(
						self.nextBlockMatrix[i][j], 
						outline = 'black', 
						fill = 'black'
					)

	# 暂停提示
	def showPauseBox(self, swich):
		if swich == 'On':
			for e in self.pauseBox['rectangle']:
				self.cv.itemconfig(
					e, 
					outline = 'lightgreen', 
					fill = 'black'
				)
			self.cv.itemconfig(
				self.pauseBox['text'][0], 
				fill = 'lightgreen'
			)
		else:
			for e in self.pauseBox['rectangle']:
				self.cv.itemconfig(
					e, 
					outline = 'black', 
					fill = 'black'
				)
			self.cv.itemconfig(
				self.pauseBox['text'][0], 
				fill = 'black'
			)

	# 显示分数
	def showScore(self):
		self.cv.itemconfig(
			self.scoreText,  
			text = str(self.control.getParameter()['score']), 
			fill = 'white'
		)

	# 键盘事件处理函数
	def onKeyboardEvent(self, event):
		operationInfo = self.control.operation(event.keysym)
		self.draw()

		# 询问是否退出
		if operationInfo['Exit'] == True:
			if messagebox.askokcancel("Verify",'Do you really want to quit?'):
				os._exit(0)
			else:
				self.control.pause = False

		# 方块已下降至最底
		if operationInfo['isBottom'] == 1:
			self.draw()
			self.showScore()

		# 显示暂停提示框
		if self.control.pause == True:
			self.showPauseBox('On')
		else:
			self.showPauseBox('Off')

	# 自动下落函数
	def autoRun(self):
		while True:
			while self.control.pause == False:
				self.draw()
				operationInfo = self.control.operation('Down', autoDown = True)
				if operationInfo['isBottom'] == 1:		# 方块已下降至最底
					self.draw()
					self.showScore()
					if self.control.getIsLose() != True:		# 未输
						self.control.nextBlock()
						self.drawNext(self.control.generateNextBlock())
						self.draw()
						
					else:		# 输
						messagebox.showinfo('Message', 'You lose!')
						os._exit(0)
				time.sleep(self.control.getParameter()['interval'])


Graph(Control(Core()))
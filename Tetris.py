import time
import random
import threading
import os
import ast
from tkinter import *
import tkinter.messagebox as messagebox
import tkinter.font as tkFont
from tkinter.filedialog import askdirectory
from tkinter import filedialog

# 核心模块
class Core():
	mainMatrixBuffer = 2						# 缓冲大小
	row = 20									# 面板格子行数
	column = 15									# 面板格子列数
	matrixRow = row + mainMatrixBuffer			# 矩阵行数
	matrixColumn = column + mainMatrixBuffer	# 矩阵列数

	score = 0					# 分数
	initInterval = 0.5			# 方块下落初始速度
	interval = initInterval 	# 方块下落当前速度

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
			self.score += 1		# 分数增加
			if self.interval > 0.1:
				self.interval = self.initInterval - 0.1 * int(self.score / 10)	# 自动下落时间间隔衰减
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
	block = {				# 用于保存当前方块信息
		'x': None, 
		'y': None, 
		'type': None, 
		'state': None
	}
	nextBlockSeed = {		# 用于保存下一方块种子
		'type': None, 
		'state': None
	}

	stopThread = True		# 控制自动下落线程的开关
	pause = False 			# 用于判断是否为暂停状态
	start = False 			# 用于判断游戏是否已开始
	helpPage = False 		# 用于判断帮助页是否打开

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

		# 游戏操作
		if self.start == True:
			# 方向操作
			if self.pause == False:
				# WASD 控制方向
				wasd = {
					'w': 'Up', 
					'a': 'Left', 
					's': 'Down', 
					'd': 'Right', 
					'W': 'Up', 
					'A': 'Left', 
					'S': 'Down', 
					'D': 'Right'
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
					self.stopThread = False
					self.pause = False
				else:
					self.stopThread = True
					self.pause = True

			if key == '\x13':
				self.stopThread = True
				self.pause = True
				File().save(str(self.getAllInfo()))

		# 退出
		if key == 'Escape':
			self.stopThread = True
			if self.start == True:
				self.pause = True
			operationInfo['Exit'] = True

		# 开始游戏
		if key == 'n' or key == 'N':
			if self.start == False:
				self.pause = False
				self.stopThread = False
				self.start = True

		# 加载存档
		if key == 'l' or key == 'L':
			if self.start == False:
				File().load(self.core, self)
			
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

	# 获取用于保存文件的所有参数
	def getAllInfo(self):
		return {
			'mainMatrix': self.core.mainMatrix, 
			'score': self.core.score, 
			'interval': self.core.interval, 
			'block': self.block, 
			'nextBlockSeed': self.nextBlockSeed, 
			'stopThread': self.stopThread, 
			'pause': self.pause, 
			'start': self.start, 
			'helpPage': self.helpPage
		}

	# 返回是否输信息
	def getIsLose(self):
		return self.core.isLose()


# 文件模块
class File():

	# 读档
	def load(self, core, control):
		path = filedialog.askopenfilename()		# 获取存档路径
		try:
			if path:
				with open(path, 'r') as f:
					content = ast.literal_eval(f.read())	# 读取文件

					# 写入数据
					try:
						for i in range(1, core.row + 1):
							for j in range(1, core.column + 1):
								core.mainMatrix[i][j] = content['mainMatrix'][i][j]
						core.score = content['score']
						core.interval = content['interval']
						control.block['x'] = content['block']['x']
						control.block['y'] = content['block']['y']
						control.block['type'] = content['block']['type']
						control.block['state'] = content['block']['state']
						control.nextBlockSeed['type'] = content['nextBlockSeed']['type']
						control.nextBlockSeed['state'] = content['nextBlockSeed']['state']
						control.stopThread = True
						control.pause = True
						control.start = True
					except BaseException as err:
						messagebox.showerror('Error', 'Unknown error')	# 游戏参数错误
		except BaseException as e:
			messagebox.showerror('Error', e)	# 文件读写错误

	# 存档
	def save(self, content):
		saveAs = filedialog.asksaveasfile()
		if saveAs:
			try:
				with open(saveAs.name, 'w') as f:
					f.write(content)
			except BaseException as e:
				messagebox.showerror('Error', e)



# 图像模块
class Graph():

	# 窗体对象
	mainPanel = Tk()
	mainPanel.title("Tetris")		# 标题
	mainPanel.geometry("640x480")	# 窗口大小
	mainPanel.resizable(width = False, height = False)	# 窗体大小不可变

	control = None			# 用于保存控制对象

	startRun = False 		# 用于判断启动动画是否播放过

	autoFallThread = None	# 用于保存自动下落线程

	graphMatrix = []		# 图像面板矩阵
	nextBlockMatrix = []	# 下一方块图像面板矩阵

	# 主画布
	cv = Canvas(
		mainPanel, 
		bg = 'black', 
		width = 640, 
		height = 480
	)

	gameWindow = None		# 用于存放游戏界面
	gameCv = None			# 用于存放游戏界面画布
	pauseBox = None			# 用于存放暂停提示框
	startWindow = None		# 用于存放启动页面
	startCv = None			# 用于存放启动画布
	menuWindow = None		# 用于存放菜单页面
	helpWindow = None		# 用于存放帮助页面
	scoreText = None		# 记分板面板

	titleFont = tkFont.Font(size = 25)	# Title 字号
	itemFont = tkFont.Font(size = 15)	# Item 字号

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
		self.createStartWindow()	# 创建启动页面
		self.createMenuWindow()		# 创建菜单页面
		self.createGameWindow()		# 创建游戏界面
		self.createHelpPage()		# 创建帮助页面
		self.createPauseBox()		# 创建暂停提示框
		self.cv.pack()

	# 创建启动页面
	def createStartWindow(self):
		self.startCv = Canvas(
			self.mainPanel, 
			bg = 'black', 
			width = 640, 
			height = 480
		)
		self.startCv.create_rectangle(
			80, 100, 560, 200,  
			outline = 'white', 
			fill = 'black'
		)
		self.startCv.create_rectangle(
			83, 103, 557, 197,   
			outline = 'white', 
			fill = 'black'
		)
		self.startCv.create_rectangle(
			40, 400, 600, 420, 
			outline = 'white', 
			fill = 'black'
		)
		self.startCv.create_text(
			310, 130, 
			text = 'Tetris', 
			font = self.titleFont, 
			fill = 'white'
		)
		self.startCv.create_text(
			310, 180, 
			text = 'Loading...', 
			font = self.itemFont, 
			fill = 'white'
		)
		self.startWindow = self.cv.create_window(
			320, 240, 
			window = self.startCv, 
			state = HIDDEN
		)

	# 播放启动动画
	def runStartWindow(self):
		temp = []
		self.cv.itemconfig(
			self.startWindow, 
			state = NORMAL
		)
		for i in range(41, 600):
			temp.append(self.startCv.create_line(
				i, 401, i, 420,  
				fill = 'yellow'
			))
			time.sleep(0.001)
		time.sleep(1)
		self.cv.itemconfig(
			self.startWindow, 
			state = HIDDEN
		)
		self.cv.itemconfig(
			self.menuWindow, 
			state = NORMAL
		)
		for i in temp:
			self.startCv.delete(i)

	# 创建菜单页面
	def createMenuWindow(self):
		menuCv = Canvas(
			self.mainPanel, 
			bg = 'black', 
			width = 640, 
			height = 480
		)
		menuCv.create_rectangle(
			80, 100, 560, 200,  
			outline = 'white', 
			fill = 'black'
		)
		menuCv.create_rectangle(
			83, 103, 557, 197,   
			outline = 'white', 
			fill = 'black'
		)
		menuCv.create_text(
			310, 130, 
			text = 'Tetris', 
			font = self.titleFont, 
			fill = 'white'
		)
		menuCv.create_text(
			310, 180, 
			text = 'Menu', 
			font = self.itemFont, 
			fill = 'white'
		)
		menuCv.create_text(
			310, 250, 
			text = """\n\n(N)New game\n\n(H)Help\n\n(L)Load""", 
			font = self.itemFont, 
			fill = 'yellow'
		)
		self.menuWindow = self.cv.create_window(
			320, 240, 
			window = menuCv, 
			state = HIDDEN
		)

	# 创建帮助页面
	def createHelpPage(self):
		helpCv = Canvas(
			self.mainPanel, 
			bg = 'black', 
			width = 640, 
			height = 480
		)
		helpCv.create_text(
			310, 50, 
			text = "帮助", 
			font = self.titleFont, 
			fill = 'yellow'
		)
		helpCv.create_text(
			300, 200, 
			text = """
			\n ↑ ← ↓ → : .......用于控制方块移动方向
			\n N : ...........................开始新游戏
			\n H : .................................帮助
			\n P : .............................暂停游戏
			\n Esc : ...........................退出游戏
			\n L : .............................加载存档
			\n Ctrl + S : ......................保存游戏
			""", 
			font = self.itemFont, 
			fill = 'yellow'
		)
		helpCv.create_text(
			300, 400, 
			text = "Press any key to return...", 
			font = self.itemFont, 
			fill = 'yellow'
		)
		self.helpWindow = self.cv.create_window(
			320, 240, 
			window = helpCv, 
			state = HIDDEN
		)

	# 创建游戏界面
	def createGameWindow(self):
		self.gameCv = Canvas(
			self.mainPanel, 
			bg = 'black', 
			width = 640, 
			height = 480
		)
		# 双线主方框
		self.gameCv.create_rectangle(
			36, 36, 44 + 15 * 20, 44 + 20 * 20, 
			outline = 'lightgray', 
			fill = 'black'
		)
		self.gameCv.create_rectangle(
			39, 39, 41 + 15 * 20, 41 + 20 * 20,
			outline = 'lightgray', 
			fill = 'black'
		)

		# 下一方块提示框
		self.gameCv.create_rectangle(
			400, 40, 580, 140, 
			outline = 'white', 
			fill = 'black'
		)
		self.gameCv.create_text(
			425, 50, 
			text = 'Next:', 
			fill = 'white'
		)

		# 记分板
		self.gameCv.create_rectangle(
			400, 200, 580, 250, 
			outline = 'white', 
			fill = 'black'
		)
		self.gameCv.create_text(
			425, 210, 
			text = 'Score:', 
			fill = 'white'
		)
		self.scoreText = self.gameCv.create_text(
			475, 210, 
			text = str(self.control.getParameter()['score']), 
			fill = 'white'
		)
		self.gameWindow = self.cv.create_window(
			320, 240, 
			window = self.gameCv, 
			state = HIDDEN
		)

	# 创建暂停提示框
	def createPauseBox(self):
		pauseBoxCv = Canvas(
			self.mainPanel, 
			bg = 'black', 
			width = 220, 
			height = 50
		)
		pauseBoxCv.create_rectangle(
			4, 4, 219, 49, 
			outline = 'lightgreen', 
			fill = 'black'
		)
		pauseBoxCv.create_text(
			0, 25, 
			text = """
				         Pause
				Press P to continue
			""", 
			fill = 'lightgreen'
		)
		self.pauseBox = self.gameCv.create_window(
			490, 405, 
			window = pauseBoxCv, 
			state = HIDDEN
		)

	# 图像面板矩阵初始化
	def initGraphMatrix(self):
		parameter = self.control.getParameter()
		# 图像面板矩阵初始化
		for i in range(parameter['row']):	# 矩阵外围一圈为缓冲区
			self.graphMatrix.append([])
			for j in range(parameter['column']):
				rectangle = self.gameCv.create_rectangle(
					40 + j * 20, 40 + i * 20, 60 + j * 20, 60 + i * 20, 
					outline = 'black', 
					fill = 'cyan', 
					state = HIDDEN
				)
				self.graphMatrix[i].append(rectangle)

		# 下一方块面板矩阵初始化
		x, y = 470, 50		# 参考坐标
		for i in range(4):
			self.nextBlockMatrix.append([])
			for j in range(4):
				rectangle = self.gameCv.create_rectangle(
					x + j * 20, y + i * 20, x + 20 + j * 20, y + 20 + i * 20, 
					outline = 'black', 
					fill = 'cyan', 
					state = HIDDEN
				)
				self.nextBlockMatrix[i].append(rectangle)

	# 将主矩阵信息映射到图像面板矩阵
	def draw(self):
		parameter = self.control.getParameter()
		for i in range(parameter['row']):
			for j in range(parameter['column']):
				if parameter['mainMatrix'][i + 1][j + 1] == 1:
					self.gameCv.itemconfig(
						self.graphMatrix[i][j], 
						state = NORMAL
					)
				elif parameter['mainMatrix'][i + 1][j + 1] == 0:
					self.gameCv.itemconfig(
						self.graphMatrix[i][j], 
						state = HIDDEN
					)

	# 下一方块提示显示
	def drawNext(self, block):
		BlockMatrix = self.control.getBlockMatrix(block)
		for i in range(4):
			for j in range(4):
				if BlockMatrix[i][j] == 1:
					self.gameCv.itemconfig(
						self.nextBlockMatrix[i][j], 
						state = NORMAL
					)
				else:
					self.gameCv.itemconfig(
						self.nextBlockMatrix[i][j], 
						state = HIDDEN
					)

	# 暂停提示
	def showPauseBox(self, swich):
		if swich == 'On':
			self.gameCv.itemconfig(
				self.pauseBox, 
				state = NORMAL
			)
		else:
			self.gameCv.itemconfig(
				self.pauseBox, 
				state = HIDDEN
			)

	# 显示分数
	def showScore(self):
		self.gameCv.itemconfig(
			self.scoreText,  
			text = str(self.control.getParameter()['score']), 
			fill = 'white'
		)

	# 键盘事件处理函数
	def onKeyboardEvent(self, event):
		
		# 预先捕捉的事件处理
		if self.control.start == False:		# 进入帮助页
			if self.control.helpPage == False:
				if event.keysym == 'h' or event.keysym == 'H':
					self.control.helpPage = True
					self.cv.itemconfig(
						self.helpWindow, 
						state = NORMAL
					)
					return
			if self.control.helpPage == True:	# 退出帮助页
				self.control.helpPage = False
				self.cv.itemconfig(
					self.menuWindow, 
					state = NORMAL
				)
				self.cv.itemconfig(
					self.helpWindow, 
					state = HIDDEN
				)
				return
		if self.control.start == True:	# 捕获 Ctrl 状态
			if event.state == 4:
				operationInfo = self.control.operation(event.char)
			if self.control.pause == True:	# 暂停提示框
				self.showPauseBox('On')
			else:
				self.showPauseBox('Off')

		# 交给控制模块处理
		operationInfo = self.control.operation(event.keysym)
		self.draw()

		# 开始
		if self.control.start == True:

			self.drawNext(self.control.generateNextBlock())

			self.cv.itemconfig(
				self.menuWindow, 
				state = HIDDEN
			)
			self.cv.itemconfig(
				self.gameWindow, 
				state = NORMAL
			)

			# 方块已下降至最底
			if operationInfo['isBottom'] == 1:
				self.draw()
				self.showScore()

			# 暂停提示框
			if self.control.pause == True:
				self.showPauseBox('On')
			else:
				self.showPauseBox('Off')

		# 询问是否退出
		if operationInfo['Exit'] == True:
			if messagebox.askokcancel("Verify",'Do you really want to quit?'):
				os._exit(0)
			else:
				if self.control.start == True:
					self.control.pause = False
					self.control.stopThread = False
					self.showPauseBox('Off')

	# 自动下落函数
	def autoRun(self):
		while True:
			if self.startRun == False:
				self.runStartWindow()
				self.startRun = True
			while self.control.stopThread == True:
				time.sleep(0.001)
			while self.control.pause == False and self.control.start == True:
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
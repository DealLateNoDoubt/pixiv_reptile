import os
import sqlite3
import datetime
import collections

from . import defines

def CheckFileIsExists(sFilePath):
    # 检查文件是否存在
    if os.path.exists(sFilePath):
        return True
    return False

def ExchangeFilePath(sFilePath):
    # 切换字符
    sFilePath = sFilePath.replace("\\", "[反斜杠]")
    sFilePath = sFilePath.replace("/", "[斜杠]")
    sFilePath = sFilePath.replace(":", "[冒号]")
    sFilePath = sFilePath.replace("*", "[星号]")
    sFilePath = sFilePath.replace("?", "[问号]")
    sFilePath = sFilePath.replace("\"", "[双引号]")
    sFilePath = sFilePath.replace("<", "[小于号]")
    sFilePath = sFilePath.replace(">", "[大于号]")
    sFilePath = sFilePath.replace("|", "[竖线]")
    return sFilePath

def CoutLog(sLog, bTime=True):
    # 打印日志
    sLogPath = os.path.join(defines.SAVE_PATH, '_log.ini')
    if os.path.exists(sLogPath):
        with open(sLogPath, 'r') as file:
            lines = collections.deque(file, maxlen=defines.LOG_MAX_LENGTH)
    else:
        lines = collections.deque(maxlen=defines.LOG_MAX_LENGTH)
    sLog = ''.join([sLog, '\n'])
    if bTime == True:
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        sLog = ''.join([now, '      ', sLog])
    print(sLog)
    lines.append(sLog)
    with open(sLogPath, 'w') as file:
        file.writelines(lines)
        file.close()


def InitLocalInfo(iPainterId, sPainterName):
    sSavePath = os.path.join(defines.SAVE_PATH, '_'.join([iPainterId, ExchangeFilePath(sPainterName)]))
    if not os.path.exists(sSavePath):
        os.makedirs(sSavePath)
    _createDB(sSavePath)
    return sSavePath


def CheckHavePicture(sSavePath, iPictureID):
    # 检查是否已经存在图片
    sDBPath = os.path.join(sSavePath, defines.PICTURES_DB)
    if not os.path.exists(sDBPath):
        _createDB(sSavePath)
        return False
    conn = sqlite3.connect(sDBPath)
    cursor = conn.cursor()
    cursor.execute('SELECT 1 FROM pictures WHERE picture_id = ?', (str(iPictureID),))
    rows = cursor.fetchall()
    conn.close()
    return bool(len(rows)>0)

def InsertPicture(sSavePath, iPictureID):
    # 插入图片
    sDBPath = os.path.join(sSavePath, defines.PICTURES_DB)
    conn = sqlite3.connect(sDBPath)
    cursor = conn.cursor()
    cursor.execute('INSERT INTO pictures (picture_id) VALUES (?)', (str(iPictureID),))
    conn.commit()
    conn.close()

def _createDB(sSavePath):
    # 创建数据库
    sDBPath = os.path.join(sSavePath, defines.PICTURES_DB)
    if os.path.exists(sDBPath):
        return
    conn = sqlite3.connect(sDBPath)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pictures (
            picture_id TEXT PRIMARY KEY
        )
    ''')
    conn.commit()
    conn.close()
import os
import datetime
import collections

from . import defines


# def _getSavePath():
#     now = datetime.datetime.now()
#     year = str(now.year)
#     month = str(now.month).zfill(2)
#     sPath = ''.join([year, '-', month, '月'])
#     sSavePath = os.path.join(defines.SAVE_PATH, sPath)
#     if not os.path.exists(sSavePath):
#         os.makedirs(sSavePath)
#     return sSavePath
# LOG_PATH = _getSavePath()


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
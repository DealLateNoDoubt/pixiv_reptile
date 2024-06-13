import os
import bs4
import json
import time
import copy
import random
import shutil
import imageio
import zipfile
import urllib3
import requests
import threading
from . import defines
from . import ctrl_common

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)  # 取消警告

class CReptileBase:       # 爬虫基类

    def __init__(self):
        self._initData()

    def OnStart(self):
        self.SetCookie(defines.PIXIV_COOKIES)
        self._sendRequest(sUrl=defines.PIXIV_URL, dctHeaders=self.m_dctHeaders, timeout=5)

    def SetCookie(self, sCookie):
        self.m_dctHeaders["Cookie"] = "".join([defines.COOKIE_HEAD, sCookie])


    def RunDownThread(self):
        num_batch = len(self.m_lstInfoItems)
        elements = num_batch // defines.NUM_THREAD
        remaining_elements = num_batch % defines.NUM_THREAD

        for i in range(defines.NUM_THREAD):
            start = i * elements + min(i, remaining_elements)
            end = start + elements + (1 if i < remaining_elements else 0) - 1
            thread = threading.Thread(target=self._downByThread, args=(start, end))
            self.m_lstThread.append(thread)
            thread.start()

        for thread in self.m_lstThread:
            thread.join()

        print("清空线程列表")
        del self.m_lstThread[:]

    def _downByThread(self, start, end):
        for i in range(start, end + 1):
            self._getPicture(self.m_lstInfoItems[i])

    def _initData(self):
        self.m_oSession = requests.session()    # 请求对象
        # 代理信息
        self.m_dctHeaders = {
            'User-Agent': defines.REPTILE_AGENT,
            'Referer': defines.PIXIV_URL,

            # 通用固定信息
            'content-type': 'application/x-www-form-urlencoded',
            'Connection': 'keep-alive',

            # 登录Cookie
            'Cookie': '',
        }
        # 数据列表
        self.m_lstInfoItems = []
        # 线程
        self.m_lstThread = []

    def _sleep(self, fSleepTime=0):
        if fSleepTime == 0:
            fSleepTime = random.uniform(1, 1.5)
        time.sleep(fSleepTime)

    def _sendRequest(self, sUrl, dctHeaders=None, timeout=15):
        if dctHeaders is None:
            dctHeaders = self.m_dctHeaders
        iRestartTime = defines.RESTART_TIMES
        while True:
            try:
                oResponse = self.m_oSession.get(sUrl, headers=dctHeaders, timeout=timeout)
                return oResponse
            except Exception as e:
                print("iRestartTime", iRestartTime)
                iRestartTime -= 1
                if iRestartTime < 0:
                    raise Exception("err-url:{0}".format(sUrl))     # 中断
                self._sleep(0.5)

    def _getPageJsonData(self, sUrl):
        # Json格式网页数据
        self._sleep()
        sHtml = self.m_oSession.get(sUrl, headers=self.m_dctHeaders, timeout=5).text
        return json.loads(sHtml)

    def _getPicture(self, dctInfo):
        iPictureID = dctInfo['pictureId']
        dctHeaders = copy.deepcopy(self.m_dctHeaders)
        dctHeaders['Referer'] = defines.PICTURE_URL.format(iPictureID)
        self._sleep()
        sPictureAjaxUrl = defines.PICTURE_AJAX_URL.format(iPictureID)
        oAjaxData = self._sendRequest(sPictureAjaxUrl, dctHeaders=dctHeaders, timeout=15)
        oSoup = bs4.BeautifulSoup(oAjaxData.text, 'html.parser')
        dctIllustDetials = json.loads(str(oSoup))['body']['illust_details']
        # 动图
        bGif = bool(dctIllustDetials.get('ugoira_meta'))
        # 多图
        bManga = bool(dctIllustDetials.get('manga_a'))

        sPictureName = ctrl_common.ExchangeFilePath(dctInfo['title'])
        sPainterName = ctrl_common.ExchangeFilePath(dctInfo['painterName'])
        iPainterID = dctInfo['pictureId']
        dctHeaders = copy.deepcopy(self.m_dctHeaders)
        sSavePath = os.path.join(defines.SAVE_PATH, sPainterName)
        if bGif:
            sSavePath = os.path.join(sSavePath, 'gif')
        if not ctrl_common.CheckFileIsExists(sSavePath):
            os.makedirs(sSavePath)
        if bGif:
            sZipUrl = dctIllustDetials['ugoira_meta']['src']
            sZipPath = '_'.join([iPictureID, sPictureName, sZipUrl[-4:]])
            dictFrams = {d['file']: d['delay'] for d in dctIllustDetials['ugoira_meta']['frames']}
            sDownPath = os.path.join(sSavePath, sZipPath)
            sTempPath = os.path.join(sSavePath, 'temp_{}'.format(iPictureID))
            lstTempFile = self._unZip(sDownPath, sTempPath, sZipUrl, dctHeaders)
            self._mergerZipGif(lstTempFile, dictFrams, sTempPath, sDownPath)
        elif bManga:
            # 多图
            pre = dctIllustDetials['manga_a']
            for i in range(len(pre)):
                sDownUrl = pre[i]['url_big']
                sPictureSuffix = sDownUrl[-6:]
                sPicturePath = sPictureSuffix
                if sPictureSuffix[0] == 'p':
                    sPicturePath = '_'.join([iPictureID, sPictureName, sPictureSuffix[1:]])
                sDownPath = os.path.join(sSavePath, sPicturePath)
                self._downOne(sDownUrl, dctHeaders, sDownPath)
        else:
            # 单图
            sDownUrl = dctIllustDetials['url_big']
            sPicturePath = '_'.join([iPainterID, sPictureName, sDownUrl[-4:]])
            sDownPath = os.path.join(sSavePath, sPicturePath)
            self._downOne(sDownUrl, dctHeaders, sDownPath)

    def _downOne(self, sDownUrl, dctHeaders, sDownPath):
        # 下载单个内容
        if ctrl_common.CheckFileIsExists(sDownPath):
            return
        dctHeaders['Referer'] = sDownUrl
        oSession = self._sendRequest(sDownUrl, dctHeaders=dctHeaders, timeout=15)
        with open(sDownPath, 'ab') as file:
            file.write(oSession.content)
            file.close()

    def _unZip(self, sDownPath, sTempPath, sZipUrl, dctHeaders):
        self._downOne(sZipUrl, dctHeaders, sDownPath)
        lstTempFile = []
        with zipfile.ZipFile(sDownPath, 'r') as zip_ref:
            for sImgName in zip_ref.namelist():
                lstTempFile.append(sImgName)
            zip_ref.extractall(sTempPath)
            zip_ref.close()
        return lstTempFile

    def _mergerZipGif(self, lstTempFile, dictFrams, sTempPath, sDownPath):
        sGifPath = sDownPath.replace('.zip', '.gif')
        lstImg = []
        lstDelay = []
        for sImgName in lstTempFile:
            lstDelay.append(dictFrams[sImgName])
            lstImg.append(imageio.imread(os.path.join(sTempPath, sImgName)))
        imageio.mimsave(sGifPath, lstImg, duration=lstDelay, loop=0)
        os.remove(sDownPath)
        if os.path.exists(sTempPath):
            shutil.rmtree(sTempPath)

    def _checkIsR18(self, dctInfo):
        if dctInfo['xRestrict'] == 1 or 'R-18' in dctInfo['tags']:
            return True
        return False

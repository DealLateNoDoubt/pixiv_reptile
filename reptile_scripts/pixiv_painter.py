import json

from . import reptile_base
from . import ctrl_common


# region 画师信息
PAINTER_ID = 101490306
# endregion

# region 画师地址信息
URL_PAINTER_ILLUSTS_ID = 'https://www.pixiv.net/ajax/user/{0}/profile/all?lang=zh'
URL_PAINTER_ILLUSTS = 'https://www.pixiv.net/ajax/user/{0}/profile/illusts?{1}work_category=illustManga&is_first_page=1&lang=zh'
IDS = 'ids%5B%5D={0}&'
# endregion

class CPixivPainter(reptile_base.CReptileBase):
    # 【指定画师】

    def OnStart(self):
        super().OnStart()

        ctrl_common.CoutLog("开始爬取【指定画师:{0}】".format(PAINTER_ID))
        sPainterUrl = URL_PAINTER_ILLUSTS_ID.format(PAINTER_ID)
        dctPageData = self._getPageJsonData(sPainterUrl)
        lstInfoItems = self._getAnalysisDate(dctPageData)
        for dctItem in lstInfoItems:
            self._getPicture(dctItem)

    def _getAnalysisDate(self, dctPageData):
        # 获取作品信息
        lstPictureID = []
        if isinstance(dctPageData['body']['illusts'], dict):
            lstPictureID += list(dctPageData['body']['illusts'].keys())
        if isinstance(dctPageData['body']['manga'], dict):
            lstPictureID += list(dctPageData['body']['manga'].keys())

        self.m_dctHeaders['Referer'] = URL_PAINTER_ILLUSTS_ID.format(PAINTER_ID)

        lstInfoItems = []
        for i in range(0, len(lstPictureID), 50):
            ids_str = ''
            iEnd = min(len(lstPictureID), i+50)
            for sID in lstPictureID[i:iEnd]:
                ids_str += "ids%5B%5D={0}&".format(sID)
            sUrl = URL_PAINTER_ILLUSTS.format(PAINTER_ID, ids_str)
            sHtml = self._sendRequest(sUrl, dctHeaders=self.m_dctHeaders, timeout=15).text
            dctData = json.loads(sHtml)
            dctWorks = dctData['body']['works']
            for dctInfo in dctWorks.values():
                lstInfoItems.append({
                    'pictureId': str(dctInfo['id']),  # 图片ID
                    'painterId': dctInfo['userId'],  # 画师ID
                    'painterName': dctInfo['userName'],  # 画师名字
                    'title': dctInfo['title'],  # 标题
                    'tags': dctInfo['tags'],  # 标签
                    'xRestrict': dctInfo['xRestrict'],  # 限制（R18）
                })
        return lstInfoItems
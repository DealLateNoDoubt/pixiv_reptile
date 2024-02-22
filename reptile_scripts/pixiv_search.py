import copy
from bs4 import BeautifulSoup

from . import ctrl_common
from . import reptile_base

# region 杂项
# 关键词
WORDS = '碧蓝航线'

# 页签
PAGE_START = 1
PAGE_END = 50

# 收藏值
COLLECTION_THRESHOLD = 500
R18_COLLECTION_THRESHOLD = 500
# endregion

# region 搜索地址
URL_SEARCH = 'https://www.pixiv.net/ajax/search/artworks/{0}?word={1}&p={2}'
URL_DETAIL = 'https://www.pixiv.net/bookmark_detail.php?illust_id={0}'
# endregion


class CPixivSearch(reptile_base.CReptileBase):

    def OnStart(self):
        super().OnStart()
        ctrl_common.CoutLog("开始爬取【指定关键词:{0}】".format(WORDS))
        for iPage in range(PAGE_START, PAGE_END+1):
            ctrl_common.CoutLog("当前进度【第{0}页】".format(iPage))
            sSearchUrl = URL_SEARCH.format(WORDS, WORDS, iPage)
            dctPageData = self._getPageJsonData(sSearchUrl)
            lstInfoItems = self._getAnalysisDate(dctPageData)
            for dctItem in lstInfoItems:
                self._getPicture(dctItem)

    def _getAnalysisDate(self, dctPageData):
        lstMangaData = dctPageData['body']['illustManga']['data']
        lstInfoItems = []
        for dctInfo in lstMangaData:
            if 'id' in dctInfo and self._checkCollection(dctInfo):
                lstInfoItems.append({
                    'pictureId': str(dctInfo['id']),  # 图片ID
                    'painterId': dctInfo['userId'],  # 画师ID
                    'painterName': dctInfo['userName'],  # 画师名字
                    'title': dctInfo['title'],  # 标题
                    'tags': dctInfo['tags'],  # 标签
                    'xRestrict': dctInfo['xRestrict'],  # 限制（R18）
                })
        return lstInfoItems

    def _checkCollection(self, dctInfo):
        iCollection = COLLECTION_THRESHOLD
        if self._checkIsR18(dctInfo):
            iCollection += R18_COLLECTION_THRESHOLD
        sDetailsUrl = URL_DETAIL.format(dctInfo['id'])
        dctHeaders = copy.deepcopy(self.m_dctHeaders)
        dctHeaders['Referer'] = sDetailsUrl
        sHtml = self._sendRequest(sDetailsUrl, dctHeaders=dctHeaders, timeout=15).text
        soup = BeautifulSoup(sHtml, 'html.parser')
        try:
            sPictureCollection = soup.find_all('span', {'class': 'count-badge'})[0].text
            if sPictureCollection[-1] == '人':
                return int(sPictureCollection[0:-1]) >= iCollection
        except:
            pass
        return False
from . import reptile_base
from . import ctrl_common

# 爬取页数
PAGE_START = 1
PAGE_END = 10

# region 已关注用户的作品地址
DYNAMIC_URL = 'https://www.pixiv.net/ajax/follow_latest/illust?p={0}&mode=all&lang=zh'
# endregion

class CPixivDynamic(reptile_base.CReptileBase):
    # 【已关注用户的作品】

    def OnStart(self):
        super().OnStart()
        ctrl_common.CoutLog("开始爬取【已关注用户的作品】")
        for iPage in range(PAGE_START, PAGE_END+1):
            ctrl_common.CoutLog("当前进度【第{0}页】".format(iPage))
            sUrl = DYNAMIC_URL.format(iPage)
            dctPageData = self._getPageJsonData(sUrl)
            lstInfoItems = self._getAnalysisDate(dctPageData)
            for dctItem in lstInfoItems:
                self._getPicture(dctItem)

    def _getAnalysisDate(self, dctPageData):
        dctIllust = dctPageData['body']['thumbnails']['illust'] # 根据网页格式强制获取数据
        lstInfoItems = []
        for dctInfo in dctIllust:
            lstInfoItems.append({
                'pictureId': str(dctInfo['id']),   # 图片ID
                'painterId': dctInfo['userId'],    # 画师ID
                'painterName': dctInfo['userName'], # 画师名字
                'title': dctInfo['title'],  # 标题
                'tags': dctInfo['tags'],    # 标签
                'xRestrict': dctInfo['xRestrict'], # 限制（R18）
            })
        return lstInfoItems

from reptile_scripts import *

if __name__ == '__main__':
   # 【已关注用户的作品】
   # CDynamic = pixiv_dynamic.CPixivDynamic()
   # pixiv_dynamic.PAGE_START = 1
   # pixiv_dynamic.PAGE_END = 3
   # CDynamic.OnStart()
   #
   # 【指定画师】
   CPainter = pixiv_painter.CPixivPainter()
   pixiv_painter.PAINTER_ID = 9016
   CPainter.OnStart()

   # 【关键词】
   # CSearch = pixiv_search.CPixivSearch()
   # pixiv_search.WORDS = "イラスト"
   # CSearch.OnStart()
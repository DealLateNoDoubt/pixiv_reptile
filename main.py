
from reptile_scripts import *

if __name__ == '__main__':
   # # 【已关注用户的作品】
   # CDynamic = pixiv_dynamic.CPixivDynamic()
   # CDynamic.OnStart()
   #
   # # 【指定画师】
   # CPainter = pixiv_painter.CPixivPainter()
   # pixiv_painter.PAINTER_ID = 0
   # CPainter.OnStart()

   # 【关键词】
   CSearch = pixiv_search.CPixivSearch()
   pixiv_search.WORDS = "女の子"
   CSearch.OnStart()
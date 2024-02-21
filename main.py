
import reptile_scripts

if __name__ == '__main__':

   # 【已关注用户的作品】
   # CDynamic = reptile_scripts.CPixivDynamic()
   # CDynamic.OnStart()

   # 【指定画师】
   # CPainter = reptile_scripts.CPixivPainter()
   # reptile_scripts.PAINTER_ID = 9016
   # CPainter.OnStart()

   # 【关键词】
   CSearch = reptile_scripts.CPixivSearch()
   reptile_scripts.WORDS = '崩坏'
   CSearch.OnStart()
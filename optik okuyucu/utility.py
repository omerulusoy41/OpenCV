import cv2 as cv
import numpy as np

# Optik form tam anlamıyla frame dumduz ve framein tum alanlarına kpalı bır sekılde fonsıondan fitrelendi
def preprocess(img):
    h,w = (400,900) #resmin uzunluk ve genişligini ayarlıyorum
    tmpdraw = img.copy()  #büyük dikdörtgeni çizmek için gercek resmin bir kopyası alındı bu sadece görmek adına(yarı kısım sonrası sıl)
    bigcount = img.copy() #büyük dikdörtgeni çizmek için gercek resmin bir kopyası alındı
    canny = cv.Canny(img,10,50) # resmin kenarları algılandı
    countours,hierarchy = cv.findContours(canny,cv.RETR_EXTERNAL,cv.CHAIN_APPROX_NONE)#resimde ki kenarlar çizildi
    cv.drawContours(tmpdraw,countours,-1,(255,0,0),10) #Kenarların çizilmesi gerçekleşti
    # Buraya kadar sunulacak
    # cv imshow ve waitkey i kopylayıp bakmak istediğiniz imgleri inceleyın
    big = rectangles(countours) # burada en büük dikdörtgeni almak için fonksıyon cagırıldı

    
    biggestCount = getCornerRect(big)  #en buyuk dikdörtgenin en uc noktalarını x y koordinatlaruı alınıyor
    cv.drawContours(bigcount,biggestCount,-1,(255,0,0),10) # en buyuk dikdörtgen çizildi

    biggestCount =  reorder(biggestCount) # enbüyük dikdörtgenin uç noktalar belirlenşiyor
    pt1=np.float32(biggestCount) # perspective uygulanması adına referans matris oluşturuldu
    pt2=np.float32([[0,0],[w,0],[0,h],[w,h]]) # yukarıda belirlenen h,w değelere göre yeni resmin referansı olusturuldu
    matr = cv.getPerspectiveTransform(pt1,pt2) # perspective dnüşümü uygulandı
    imgwarp = cv.warpPerspective(img,matr,(w,h)) # warp perspective ile h,w ile belilenmiş yeni foto oluştu
    # artık sadece karsımızda en büyük dikdörtgen yani optigin ta kendisi 400,900 boyutlarında karsımızda
    return imgwarp

# Asıl işlevi dikdörtgenkeri bul ve en buyugune geri yolla
def rectangles(countours):
    rect = []
    for i in countours:
        area = cv.contourArea(i) #çizilen kenarların her bırı ıcın bır alan hesabı yapıldı
        if area > 500: # alan hesabı 500 den buyuk olanı almak adına kosul
            peri = cv.arcLength(i,True) # arclength cevre hesabı yapar
            aprox = cv.approxPolyDP(i,peri * 0.02,True) # approxplydp ile çizilen kenarın kac kenarlı oldugu bulmaya calısılır
            if len(aprox) == 4: #kenar sayısı 4 olanları al
                rect.append(i) # rect dizisine ekle
    rect = sorted(rect,key=cv.contourArea,reverse=True)#dikdörtgenler sıralnadı
    return rect[0] #en buyuk dikdörtgen alındı

# en buyuk dikdörtgenin en uc noktaları gerı yollandı
def getCornerRect(cont):
     peri = cv.arcLength(cont,True) #cevre
     aprox = cv.approxPolyDP(cont,0.02*peri,True) 
     return aprox 
# en büyük dikdörtgen için perpective kullanabilme adına kenarların x,y koordınatları kesın ve net bir şekilde  ayarlanıyor
# hangi nokta dikdörtgenin neresinde burada bulunur
def reorder(points):
    points = points.reshape((4,2))  # 3 boyutlu matrisin bir içerisine girildi
    newp = np.zeros((4,1,2),np.uint32) # np ile yeni matris olusturuldu değeleri 0
    add = points.sum(1) # değer toplamaları yapıldı
    newp[0] = points[np.argmin(add)] # sol ust
    newp[3] = points[np.argmax(add)] # sag ust
    diff = np.diff(points,axis=1)
    newp[1] = points[(np.argmin(diff))] #sol alt
    newp[2] = points[(np.argmax(diff))] # sağ alt
    return newp
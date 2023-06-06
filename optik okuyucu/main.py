import cv2 as cv
import numpy as np
import utility as ut
import csv
import os
import tkinter as tk
from tkinter import ttk,filedialog
from tkinter import *
from tkinter import messagebox

def esikle(img):
    img = cv.cvtColor(img,cv.COLOR_BGR2GRAY) # fotografı gri tona ayarlıyor
    return cv.adaptiveThreshold (img,255,cv.ADAPTIVE_THRESH_GAUSSIAN_C,cv.THRESH_BINARY_INV,21,2) # adaptive thrshhold ile yogunluga göre eşikleme yapılıyor

# cevap kısımlarının ve ögrnonun kırpılması gercekleşiyor
def ilkOn(img):
    return esikle(img[134:400,290:400])
def ikiOn(img):
    return esikle(img[134:400,455:565])
def ucOn(img):
    return esikle( img[134:400,615:725])
def dortOn(img):
    return esikle(img[134:400,775:885])
def ogrNo(img):
    return esikle(img[134:400,0:250])

# tum cevapları tek bir diziye atama işlemi gercekleşiyor
def allanswer(img):
    answers =[]
    ans1 = ilkOn(img) 
    ans1 = cv.resize(ans1,(110,270)) # resize ile foto boyutunu tam sayıya esitledim
    sp1 = np.vsplit(ans1,10) # ilk onluk cevabı tek 10 a kesme işlemi gercekleşiyor
    for i in sp1:
        answers.append(i) # her soru için kesme işlemi gerceklesen fotoyu answera ekle 
    # alt kısımlarda aynı
    ans2 = ikiOn(img)
    ans2 = cv.resize(ans2,(110,270))
    sp2 = np.vsplit(ans2,10)
    for i in sp2:
        answers.append(i)
    ans3 = ucOn(img)
    ans3 = cv.resize(ans3,(110,270))
    sp3 = np.vsplit(ans3,10)
    for i in sp3:
        answers.append(i)
    ans4 = dortOn(img)
    ans4 = cv.resize(ans4,(110,270))
    sp4 = np.vsplit(ans4,10)
    for i in sp4:
        answers.append(i)
    return answers
def ogrnoBul(img):
    ogrno = ogrNo(img)
    ogrno = cv.resize(ogrno,(250,270))
    coloums = np.hsplit(ogrno,10) # ogrno için dikey kesim gercekleşiyor
    no = 0
    #bu döngüde ögrnonun tum haneleri bulunacak
    for i in coloums:
        boxes = np.vsplit(i,10) # dikey kesim gercekleştikten sonra ilk sutun için satır kesimi yapılıyor
        box = (boxes[0])[9:22,8:16] # kırpma işlemi yapılyıor
        ind = 0
        max = cv.countNonZero(box) # siyah olmayan piksel sayısını maxa eşitledim
        # burada en buyuk siyah olmayan değer bulunuyor
        for j in range(1,10):
            box = (boxes[j])[9:22,8:16]
            if max < cv.countNonZero(box): # eğerki siyah olmayan piksel sayısı max dan buyukse yeni max değeri o oluyor
                max=cv.countNonZero(box) # indisde ona eşitleniyor
                ind = j
                if max < 60:
                    ind = -1
        if max < 60: # düzgün karalanmayan sıkları bos yani yanlış olması adına siyah olmama sayısı eşiğini 60 ayarladım
            ind = -1 # eşiği gecemeyen değerler -1 oldu
        if ind != -1: # -1 olmayan değerler girdi
            no = (no*10) + ind
    return no
def findAnswer(answers):
    res = []
    for ans in answers:
        boxes= np.hsplit(ans,5)
        box = (boxes[0])[4:22,4:18]
        max = cv.countNonZero(box)
        ind = 0
        for i in range(1,5):
            box = (boxes[i])[4:22,4:18]
            if max < cv.countNonZero(box):
                max= cv.countNonZero(box)
                ind = i
                if max < 170:
                    ind = -1
        if max < 170:
                    ind = -1
        res.append(ind)
    return res


def CevapAnahtari():
    cvppath = filedialog.askopenfilename()
    cevapanahtari = cv.imread(cvppath) #(imread img okuma yapar) cevap anahtarı okunuyor
    cevapanahtari = ut.preprocess(cevapanahtari)  # ut = utilty.py dosyasının kısaltılması oraya işaret eder. o fonksyıonu ıncele
    ans = allanswer(cevapanahtari) # allanswer ile tum cevaplar için resimde kırpma işlemleri uygulanıyor
    ans = findAnswer(ans) # ceaplar bulunuyor
    return ans
# bu fonksiyonda ögrenci cevapları ve cevap anahtarındakı değgerler karsılastırılıyor
def getResult(answers,ans):
    result = 0
    for i in range(0,int(text_area.get("1.0",END))): 
        if answers[i] == ans[i]:
            answers[i] = "T" # excell de gösterilmek adına yeni deger True nun t si
            result +=  (100 / int(text_area.get("1.0",END))) # 20 soru varsa her doğru cevap için 5 puan resulta eklenıyor
        else:
             answers[i] = "F" # excell de gösterilmek adına yeni deger false nun f si
    return result

def ogrenciCevaplari():
    messagebox.showinfo("Warning", "Cevap Anahtarini Sec")
    ans = CevapAnahtari()
    messagebox.showinfo("Warning", "Ogrenci Cevaplari dizinini Sec")
    cvppath = filedialog.askdirectory()
    photos = os.listdir(cvppath)    
    writingFile =  open("result.csv","w",encoding='utf-8') 
    # bu dongude tum fotograflar belirtilen diziden teker teker okunuyor ve sonuc excelle yazılıyor
    for i in range(0,len(photos)):
        imgs = cv.imread(cvppath+"/"+photos[i]) # fotograflar dızınıdekı tum sırayla fotoları oku
        imgs = ut.preprocess(imgs) #fotgrafı biçimlendir
        answers = allanswer(imgs) # allanswer ile tum cevaplar için resimde kırpma işlemleri uygulanıyor
        answers = findAnswer(answers) # ögrencinin işaretlediği şıklar bulunuyor
        csvWriter = csv.writer(writingFile) #(csv excell yazmak için api) dosya belirtiliyo
        writingrow = [str(ogrnoBul(imgs)),str(getResult(answers,ans)),answers[0:int(text_area.get("1.0",END))]] # ogrno , sonuc, ve yapılan hatalar excel e yazılmak adına diziye alındı
        csvWriter.writerow(writingrow) # excele yazma işlmei gerçekleşti
    messagebox.showinfo("Warning", "result.csv is ready")
    
root = Tk()
root.geometry("1200x600")
root.resizable(False, False)
notebook = ttk.Notebook(root)
notebook.pack(expand=True, fill=BOTH)

tab1 = ttk.Frame(notebook,width=500, height=500)
notebook.add(tab1, text="Dosya Ekle")

askNo = Label(tab1, text="How Many Questions ? : ")
askNo.grid(row=0, column=0, padx=400, pady=5, sticky="w")

text_area = tk.Text(tab1, height=2, width=10)
text_area.grid(row=0,column=0,padx=10, pady=5)

button2 = Button(tab1, text="let's Do it", command=ogrenciCevaplari,height=5, width=120)
button2.grid(row=2, column=0, padx=200, pady=50)
root.mainloop()






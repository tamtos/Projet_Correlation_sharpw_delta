#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Oct 17 15:28:06 2018

@author: iris
"""
import numpy as np

import matplotlib.pyplot as plt
import scipy.signal as sp
import scipy
from scipy import interpolate
from scipy.interpolate import UnivariateSpline
time=60
global t0
t0=30
chemin ='/Users/iris/Desktop/Projet_Rech/Exemple/EEG_58_Sig/Donnes_signaux/' #à changer selon les ordinateurs 
global val_fig #gestion des figures
val_fig=4
#global fig1
#fig1=plt.figure(0)
# Traitement des fichier exporté en format .txt sur Matlab


        
def open_data(char):
    """char : the path to file
        returns the list of the element of the signal"""
        #Eventuellement modifier en fonction des informations que l'on veut garder
    mon_sig=open(char,'r')
    line=mon_sig.read()
    sig=line.split("\n")[2:-1] #on enlève le titre et Y et le dernier caracère foire...
    mon_sig.close()
    return [float(elem) for elem in sig]
#Il faudrait récupérer le nom des electrodes

def normal(char):
    """normalise les valeurs"""
    list=open_data(char)
    st=np.std(list)
    list=list/st
    #list =list/np.sqrt(len(list))
    return list
    
    
def trace(char,T):
    """char : path to the file
        plot the signal
        T: list containing the time"""
    Y=open_data(char)[0:time*512]
    #T=open_data(chemin+'BP1-BP2_Temps.txt')[0:20*512]
    #plt.figure()
    plt.xlabel("Temps en seconde")
    plt.ylabel("En mv")
    plt.plot(T,Y)
    plt.grid()
    plt.title(char[66:-4]) #-4 delete the .txt and the 66 delete the chemin
    plt.show()

    
def trace2(char1,char2):
    """char1,char2 : path two the both signals we want to compare
    plot the signal on a window"""
    Y1=open_data(char1)[0:time*512]
    Y2=open_data(char2)[0:time*512]
    
    T=open_data('BP1-BP2_Temps.txt')[0:time*512]
    plt.figure(figsize=(15,15))
    plt.subplot(2,1,1)
    plt.plot(T,Y1,color='red')
    plt.title(char1[0:-4])
    plt.ylabel("En mv")
    plt.subplot(2,1,2)
    plt.plot(T,Y2)
    plt.title(char2[0:-4])
    plt.ylabel("En mv")
    plt.xlabel("Temps en seconde")
    #plt.close()
    

    
def compare(Y1,Y2,title,mode='brut',T=[]): #A modifier, revoir la correlation entre deux signaux
    """retourne le coefficent de correlation. Affiche 4 graphiques : les deux signaux, le signal1 en fonction du signal2 et le coefficent de corrélation
    mod : peut valoir brut ou puissance caractérise l'état du signal à traiter"""
    #Y1=open_data(char1)[0:20*512]
    #Y2=open_data(char2)[0:20*512]
    if mode=='brut':
        T=open_data(chemin+'/BP1-BP2_Temps.txt')[0:time*512]
    plt.figure(figsize=(15,30))

    plt.grid()
    plt.subplot(2,1,1)
    plt.scatter(Y1,Y2,s=0.5)
    #plt.title(" B3-B2 en fonction de B2-B1")
    #plt.title(char1[:-4] + " en fonction de " + char2[:-4] )
    
    plt.subplot(2,1,2)
    y12=sp.correlate(Y1,Y2,"full")
    y12=y12/(np.linalg.norm(Y1)*np.linalg.norm(Y2))#Exactement des valeurs pour tout les points
    #print(y12.shape)
    decalage=np.argmax(abs(y12))-len(Y1) #avoir la valeur du décalage soit le moment du maximum de correlation
    plt.plot(y12) #Il y a le double de points que deux point analysés quand option full...
    plt.title('Le tracé de la correlation '+title)
    d,ordo,r2,p_val,stderr=scipy.stats.linregress(Y1,Y2)  #regression linéaire 
    
    plt.figure(2)
    plt.subplot(2,1,1)
    plt.plot(T,Y1,color='red',linewidth=0.5)
    #plt.title(title1)
    plt.ylabel("En mv")
    plt.xlabel("Temps en seconde")
    plt.grid()
    #plt.title(char1[0:-4])
    #plt.ylabel("En mv")
    
           
    plt.subplot(2,1,2)
    plt.plot(T,Y2,color='blue',linewidth=0.5)
    plt.ylabel("En mv")
    plt.xlabel("Temps en seconde")
    plt.grid()
    #plt.title(title2)
    plt.close()
    #plt.title(char2[0:-4])
    
    plt.show()
    #plt.close()
    y=sp.correlate(Y1,Y2,'valid')
    y=y/(np.linalg.norm(Y1)*np.linalg.norm(Y2))#Je ne comprends pas bien à quoi correspond ce coefficient
    return(y,d,'decalage= ', decalage/512)



def filtre(char,T,opt='ripples'):
    """"filtre le signal par défaut on considère qu'il s'agit d'un ripple
    char : chemin du fichier de données à tracer
    T: list contenant le temps
    return : le signal filtré """
    
    nyq=0.5*512 #à changer en fonction de la fréquence d'échantillongage
    Y=open_data(char)[0:time*512]
    #T=open_data('BP1-BP2_Temps.txt')[0:20*512]
    if opt=='ripples' : 
        low,high=120/nyq,250/nyq
    if opt=='delta':
        low,high=1/nyq,4/nyq #correspond à la bande de fréquence du filtrage
    b,a = sp.butter(2,[low,high],btype="bandpass")
    #print(len(data))
    
    filtered=sp.filtfilt(b,a,Y)
    
    #if val_fig==1:
    #print(val_fig)
#    plt.figure(figsize=(20,30))
#    plt.subplot(2,1,1)
#    plt.plot(T,filtered)
#    plt.title("Signal filtré")
#    plt.show()
#    a commenter lorsqu'on veut afficher comparaison en puissance    
    
    return filtered
    

def calc_puiss(char,T,h=20,opt='ripples'):
    """retourne un vecteur puissance du signal sur une portion delta et par saut de h. on compte en nombre de point"""
    Y=filtre(char,T,opt)
    #T=open_data('BP1-BP2_Temps.txt')[0:20*512]
    
    puiss=[]
    Tpuiss=[]
    #Ti=[] #contient les i pour correspondant au temps
    if opt=='ripples':
        delta=25
    if opt =='delta':
        delta=250 #correspond à la variation de la fenetre
    i=delta
    while i<512*time-delta:
        #print(i+delta)
        puiss+=[np.linalg.norm(Y[i-delta:i+delta])]#portion de environ 20ms
        Tpuiss+=[i/512]
        #Ti+=[i]
        i=i+h
    #print(len(Tpuipuiss))
    
   
    return (puiss,Tpuiss)

def aff_puiss(char,T,h=20,opt='ripples'):
    global val_fig
    Tpuiss,puiss=calc_puiss(char,T,h,opt)[1],calc_puiss(char,T,h,opt)[0]
    #plt.subplot(2,1,2)
#    plt.plot(Tpuiss,puiss,c='orange')  
    if opt=='delta':
        #plt.subplot(2,1,2)
        plt.plot(Tpuiss,puiss,c='orange')
    else:
#        plt.subplot(2,1,2)
        plt.plot(Tpuiss,puiss,c='orange')
#    if val_fig==1: # à commenter lorsqu'on est pas dans le cadre de la fonction detec_delta_sharp_ripples
#        
#        plt.xlabel("Temps en secondes")
 
        
    plt.title("Puissance du signal "+char[66:-4])
    plt.grid()
    plt.show()
  
    
    

def compar_delta_ripples(T,char=chemin+"B'3-B'2N3.txt",char2=chemin+"O'9-O'8N3.txt"):
    """Compare les signaux issus de char avec les signaux de O'9-O'8"""
    #plt.figure()
    #plt.subplot(2,1,1)
    #aff_puiss(char,T)
    #plt.subplot(2,1,2)
    #aff_puiss(char2,T,opt='delta')#Ne faut il pas faire changer h et d la manière dont on calcule la puissance ?
    
def corr_sig_puiss(char1,char2,T):
    """Calcule la correlation entre deux signaux"""
    
    Y1=calc_puiss(char1,T)[0]
    #Y2=calc_puiss(char2,T,h=20,opt='delta')[0]#cas ou le signal vient de zone O
    Y2=calc_puiss(char2,T)[0]
    aff_puiss(char1,T)
    aff_puiss(char2,T,h=20,opt='delta')
    y12=sp.correlate(Y1,Y2)
    y12=y12/(np.linalg.norm(Y1)*np.linalg.norm(Y2))
    decalage=(np.argmax(abs(y12))-len(Y1))*20/512
    plt.figure(figsize=(15,30))
    plt.title("Correlation des signaux puissances "+ char1[66:-4]+" "+char2[66:-4])
    plt.plot(y12)
    plt.show()
    print(decalage)
    
    
def periode_corr(char1,char2,seuil=0.11,opt=1,part=1):
    """Calcule la différence de temps qui sépare deux pics sur la graphe de la corrélation
    char1 et char2 représentent les deux données à comparer
    seuil correspond au critère pour lequel on repère un pic
    Le seuil choisit correspond à celui qui fait les meilleur résultat (pas de pics à côté)
    part: correspond au "côté" de la corrélation étudié soit un décalage positif ou négatif
    opt : correspond à un calcule des point au dessus de 0 peut prendre pour valeur -1 ou 1"""
    Y1=open_data(char1)[0:time*512]
    Y2=open_data(char2)[0:time*512]
    y12=sp.correlate(Y1,Y2,"full")
    y12=y12/(np.linalg.norm(Y1)*np.linalg.norm(Y2))
    plt.figure()
    plt.title(char1[66:-4] +" en fonction de " + char2[66:-4])
    plt.plot(y12)
    max=[]
    per=[]#contiendra les différence de temps entre chaque pic
    Y=[]
    if part==0:
        Y=y12[0:512*time]
    if part==1:
        Y=y12[512*time:-1]
    for i in range(len(Y)):
        if Y[i]*opt>seuil:
            max+=[[Y[i],i]]
            #plt.plot(i,y12[i],'r.')#on remarque qu'il s'agit des bons pics qui sont détéctés ! 
            if Y[i-1]*opt<seuil and len(per)>0: # regarde si l'élément précédent n'était pas au dessus du seuil
                per[-1]=i-per[-1]
        else:
            if Y[i-1]*opt>seuil: #regarde si l'élément d'avant était dans le pic
                per+=[i]
                plt.plot(0+i+part*512*time,Y[i],'g*')
    return [elem/512 for elem in per][0:-1] #le dernier element ne correspond pas à une différence de temps : on l'enlève

def detec_pic(char1,T,opt='ripples',fact=3,max_fact=10,h=20):
    """retourne la liste des abscisses du maximum d'amplitude des sharpw ripples"""
    #Y1=open_data(char1)[0:time*512]
    global val_fig
    Y=calc_puiss(char1,T,h,opt)[0]
    Tp=calc_puiss(char1,T,h,opt)[1]
    ecart=np.std(Y)
    moy=np.mean(Y)
    #print(moy)
    seuil=moy+fact*ecart
    #print(seuil)
    list_max=[]
    list_time_max=[]#la liste retournée contient les indices des max d'amplitude des sharpw
    list_ripples=[[0,0]] #Initialisation
    list_ind=[[0,0]]#contient les indices des moment ou un pic est détectée
    #fin_ripples=[]#contient le temps de fin du ripples noté en list_ripples  
    
    if opt=='A':
        fact=8 #augmente pour la detection de pic épileptique
    if val_fig==1:
        plt.subplot(2,1,2)
        val_fig+=1
    if val_fig==0:
        plt.figure(figsize=(30,30))
        plt.subplot(2,1,1)
        val_fig+=1
       
    #aff_puiss(char1,T)
    for i in range(1,len(Tp)-1):
        #print(list_ripples)
        if seuil<Y[i]:#il faut voir le cas où le les valeurs de départ ont déja dans sharpw dans ces cas là on a un problem d'index out of range 
            if (Y[i-1]<seuil):#vérifie que l'élément d'avant n'était pas dans un ripple
                list_ripples+=[[Tp[i],Tp[i]]]
                #sharpw=1
#                print(list_ripples)
                list_ind+=[[i,i]]
#                plt.plot(Tp[i],Y[i],'g*')
                #fin_ripples+=[Tp[i]]
            if (Y[i+1]<seuil): # le cas ou l'element d'après n'est plus au dessus du seuil et que le debut de l'extrait n'a pas commence sur un pic 
                list_ripples[-1][1]=Tp[i+1]#on ajoute l'element de fin 
                #print(list_ind[-1][1])
                list_ind[-1][1]=i+1
#                plt.plot(Tp[i+1],Y[i+1],'r*')
                pic_max=max_fact*ecart+moy #par défaut on condière que le pic n'est pas un sharpw
#                print(list_ripples)
                #sharpw=0
                #Traiter le cas où le pic max est sur un sommet
                if list_ripples[-1][1]==list_ripples[-1][0]:#le cas où le point i étudié est un maximum
                    pic_max=[Y[list_ind[-1][0]]]
                    print(list_max)
                #@print(list_time_max)
                if (list_ripples[-1][1]-list_ripples[-1][0]) > 0.02:  #Si le pic est assez large
                    #On calcule le maximum du pic, soit une interpolation
                    l_sharpw=Y[list_ind[-1][0]:list_ind[-1][1]]#liste des valeurs de Y etant potentiellement un sharpw
                    pic_max=max(l_sharpw) #le maximum du pic
                    if pic_max<=max_fact*ecart+moy:
                        #print(pic_max)
                        #print
                        #print(l_sharpw.index(pic_max))
                        list_time_max+=[Tp[l_sharpw.index(pic_max)+list_ind[-1][0]]]#l'indice du maximum de pic
                        list_max+=[pic_max]
                    else:
                        del list_ripples[-1]
                else:
                    del list_ripples[-1]
                    #print(list_ripples)
                        #plt.plot(Tp[list_index_max[-1]],pic_max,'r.')
                
    return (list_time_max,list_max,list_ripples[1:])

def sort_sharpw_ripples(char1,T,opt='ripples',h=20):
    """Trie les pics en trois catégorie et les affiche sur le graphe des puissance"""
    plt.figure(figsize=(30,15))
    #aff_puiss(char1,T)
    #recoltons les pics compris entre 3 et 5 fois l'ecart type

    aff_puiss(char1,T)
    
    U0=detec_pic(char1,T,'ripples',3,5,h)
    plt.plot(U0[0],U0[1],'g*',label="between 3-5 std")
    
    U1=detec_pic(char1,T,'ripples',5,7,h)
    plt.plot(U1[0],U1[1],'b*',label="between 5-7 std")
    
    U2=detec_pic(char1,T,'ripples',7,50,h)
    plt.plot(U2[0],U2[1],'r*',label="above 7 std")
    
    plt.legend()
    
    
def vect_detect_pic(char1,T,opt='ripples',fact=3,max_fact=10):
    """retourne un vecteur de 0 et et de 1 correspondant à la detection de pic. Soit 1 quand la valeur du signal correspond à un pic sharpw 0 sinon"""
    U0=detec_pic(char1,T,opt,fact,max_fact,1)[2]
    print(len(T))
    vect=[]#liste qui ca contenir les 0 et les 1
    i=0
    for elem in T:
        if i<len(U0):# qd on a détecté tous les sharpw ripples
            if  elem>=U0[i][0]:
                if elem<round(U0[i][1],6):
                    vect+=[1]
                if elem==round(U0[i][1],6):
                    vect+=[1]
                    i+=1
                    
            else:
                vect+=[0]
        else:
            vect+=[0] #on a detecté tous les sharpw ripples
    #print(vect)
    #print('taille vect', len(vect[:-1])) #j'ai un pb de dimension de vecteurs : bizarre
    #plt.title("Detection sharpw signal "+char1[66:-4])
    plt.grid()
    #plt.figure(figsize=(15,30))
   # plt.subplot(2,1,2)
    #print("T et vect" ,len(T),len(vect))
    plt.plot(T,vect,label="Detection sharpw signal "+char1[66:-4])
    #plt.show()    
    return vect
    
def detect_delta(char_delta,T,h):
    """Detecte les pics supposés caractéristique des rythmes delta du cerveau selon un critère d'amplitude"""
    plt.figure(figsize=(30,15))
    plt.subplot(2,1,1)
    aff_puiss(char_delta,T,h,'delta')
    Ud2=detec_pic(char_delta,T,'delta',2,100,h);#On considère uniquement les pics élevés
    plt.plot(Ud2[0],Ud2[1],'r*',label='above 2 std')
    #Ud1=detec_pic(char_delta,T,'delta',0.3,2,h);#déterminé arbitrairement, pour avoir des pics intéressant
    #plt.plot(Ud1[0],Ud1[1],'b*',label='between 0.3 and two std')
    plt.title("Detection de pic delta "+char_delta[66:-4])
    plt.legend()

   
    
def detec_delta_sharp_ripples(char_delta,char_ripples,T):
    """detecte sur la puissance d'un signal delta si il y a des signaux ripples
    """

    
    #T=calc_puiss(char_delta,T,h=20,opt='delta')[1]
    X=detec_pic(char_ripples,T)[0]
    aff_puiss(char_delta,T,h=20,opt='delta')
    #print(X)
    for elem in X:
        plt.axvline(x=elem[0])
    plt.show()
    #for k in len(range(Y)):
        #if T[k] in X:
    #Y_ripples+=[Y[k] for k in X]
    #print(Y_ripple)
    
def detec_epileptic_pic(char_A,char_B,T):
    """Affiche à la fois le graphe brut signal A, le signal filtré en puissance issus des electrode A et issu electrode B"""
    plt.figure(figsize=(20,30))
    plt.subplot(3,1,1) #penser à commenter des bouts de certaines partie de code afin que tout s'affiche bien 
    trace(char_A,T)          
    plt.subplot(3,1,2)
    detec_pic(char_A,T,opt='A')
    plt.subplot(3,1,3)
    detec_pic(char_B,T)
    plt.xlabel('temps en seconde')

    
def phase_delta(char_B,char_O,T,h):
    """Determinons la phase du signal delta lorsque le critère sharpw est détecté aux instants appartenant à la liste_t"""
    #On utilise la transformée de Hilbert 
    Tpuiss,Y=calc_puiss(char_O,T,h,'delta')[1],calc_puiss(char_O,T,h,'delta')[0]
    list_t=detec_pic(char_B,T)[0] #liste des point où on detecte un sharpw
    #Y=np.cos(T)
    signal_analytic=sp.hilbert(Y)
    phase_instantaneous=np.angle(signal_analytic)#on a bien une periodicité de la phase compris entre [-pi,pi]]
    fig=plt.figure(figsize=(30,15))
    ax0=fig.add_subplot(211)
    ax0.plot(Tpuiss,Y,label='signal')
    ax0.legend()
    plt.title(char_O[66:-4])
    #ax3=fig.add_subplot(312)
    #list_t=detec_pic(char_B,T) 
    ax2=fig.add_subplot(212)
    plt.title("phase de la puissance du signal "+char_O[66:-4])
    ax2.plot(Tpuiss,phase_instantaneous)
    ax2.set_xlabel("time in seconds")
    for elem in list_t:
        ax2.axvline(x=elem,color='r')
    return phase_instantaneous
    
def statistic_sharpw(char1,T,fact=3,max_fact=10,h=20):
    """Fonction qui retourne le nombre de sharpw detectés, leur amplitude max, la moyenne et l'ecart-type"""
    U0=detec_pic(char1,T,'ripples',fact,max_fact,h)[1]#liste contenant les maximum d'amplitude
    print('Moyenne des pic d amplitude comprise est ',np.mean(U0))
    print('Deviation moyenne' ,(np.std(U0)))
    print('Valeur maximal', (np.max(U0)))
    print('Valeur minimal',(np.min(U0)))
    print('nombre de sharpw détécté', len(U0))
    
def is_epil_pic(t):
    """Fonction qui retourne vrai si le pic à t correspond à un pic epileptic false sinon"""
    return 0;
    
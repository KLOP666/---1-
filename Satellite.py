from skyfield.api import load, wgs84, EarthSatellite
import numpy as np
from math import sqrt
import math
import pandas as pd
import matplotlib.pyplot as plt
#Convert degrees
def convert(deg):
  d, m, s = str(deg).replace('deg', '').split(" ")
  ans = float(float(d) + (float(m.strip("'")) / 60) + (float(s.strip('"')) / 3600))
  return str(ans)
with open('krf20090301_2_S1_bg.thr') as f:
    Th = np.array([row.strip() for row in f])
    #print("Len:\n", len(Th))
    #print("TIME HiSTORY:\n", Th)
#Считываем файл
th = np.zeros((len(Th), len(Th[1].split())))
for i in range(0, len(Th)):
    #print(Th[i].split())
    temparr = Th[i].split()
    for j in range(0, len(Th[i].split())):
        th[i][j] = float(temparr[j])
#Закончили с файлом
#print('FILE:\n', th)
Time = np.zeros((len(Th)-60, len(Th[0].split())-10))#Создаем массив времени
for i in range(60, len(Th)):
    for j in range(0, len(Th[0].split())-10):
        Time[i-60][j] = th[i][j]
# Закончили со временем
#print('TIME:\n', Time)
#Создаем массив из количеств счета
sc = np.zeros((len(Th)-60, len(Th[1].split())-2))
for i in range(60, len(Th)):
    k = 0
    for j in range(2, len(Th[0].split())):
        sc[i-60][k] = th[i][j]
        k += 1
#Закончили со счетами
#print("Number of scores:\n",sc)
#Создаем массив мертвого времени
DT = np.zeros((len(Th)-60, 1))
sum = np.zeros((len(Th)-60, 1))
for i in range(0, len(Th)-60):
    for j in range(0, len(Th[1].split())-2):
        sum[i][0] += sc[i][j]
#print("Summ elements of score:\n", sum)
DT = 0.000006*sum
#Закончили с этим
#print("Dead Time:\n",DT)
AT = 4-DT
#print("Alive time:\n",AT)
#Скорость счета
Rate = sc/AT
#Intensity
Int = Rate/127
Intensity_Gamma = np.zeros(14)
mean_of_energy = np.zeros(4)
mean_of_energy[0] += sqrt(8*280)
mean_of_energy[1] += sqrt(280*400)
mean_of_energy[2] += sqrt(400*640)
mean_of_energy[3] += sqrt(640*1000)
#print("Rate of scores:\n", Rate)
for time in range(0, 14):
    S_Int = np.zeros(1436)
    for i in range(0, len(S_Int)):
        for j in range(0, 4):
            S_Int[i] += mean_of_energy[j]*Int[i + 1436*time][j]
#print("Rate of Spectrum number 1:\n", len(S_Int))
    AllTime = np.zeros((len(Time)-60))
    for i in range(60, len(Time)):
        AllTime[i-60] = Time[i][1]
#print("All time:\n", AllTime)

    with open("2009.bsp") as f:
        tle = np.array([row.strip() for row in f])
#k=47-89,i=46-88-March
    satellite = EarthSatellite(tle[92], tle[93], name='KP')
    ts = load.timescale()
    Latitude = np.zeros(1436)
    Intensity = np.zeros(1436)
    Longitude = np.zeros(1436)
    Sunlight = np.zeros(len(Intensity))
    Shadow = np.zeros(len(Intensity))
    eph = load('de421.bsp')
    k = 0
    for i in range(0, 5744, 4):
        t = ts.utc(2009, 3, 1, 00, 00, i + 5744*time )
        geocentric = satellite.at(t)
        subpoint = wgs84.subpoint(geocentric)
        lat = np.array(convert(subpoint.latitude), dtype = float)
        lng = np.array(convert(subpoint.longitude), dtype = float)
        Latitude[k] = lat
        Longitude[k] = lng
        sunlit = satellite.at(t).is_sunlit(eph)
        print(k," Latitude: ", lat," Longetude: ",lng,'{}  {} is in {}'.format(
            t.utc_strftime('%Y-%m-%d %H:%M'),
            satellite.name,
            'sunlight' if sunlit else 'shadow',),"\n")
        if(0 < lat < 25):
            sunlit = satellite.at(t).is_sunlit(eph)
            Intensity[k] = S_Int[k]
            if sunlit: Sunlight[k] = Intensity[k]
            else: Shadow[k] = Intensity[k] ;
            #print(k, "Intensity: ", Intensity[k], " S_INT:", S_Int[k],'{}  {} is in {}'.format(
            #   t.utc_strftime('%Y-%m-%d %H:%M'),
            #    satellite.name,
            #    'sunlight' if sunlit else 'shadow',), "\n")
            #print(k," Latitude in INTERVAL: ", lat, " Longitude in INTERVAL: ",lng,'{}  {} is in {}'.format(
            #    t.utc_strftime('%Y-%m-%d %H:%M'),
            #    satellite.name,
            #    'sunlight' if sunlit else 'shadow',),"\n")
            k+=1
        else: k += 1
    n=0
    Sun = np.zeros(104)
    Sh = np.zeros(104)
    sh = 0
    s = 0
    print("Difference between INTENSITY for the number of spin", time, ":" )
    for i in range(0,len(Shadow)):
        if Sunlight[i] == 0:
            n+=1
        else:
            Sun[s] += Sunlight[i]
            s += 1
    for i in range(0, len(Sunlight)):
         if Shadow[i] == 0:
             n+=1
         else:
             Sh[sh] += Shadow[i]
             sh += 1
    for i in range(0, len(Sh)):
        print(i," Intensity in the sunlight: ",Sun[i]," Intensity in the shadow: ", Sh[i], "\n")
    Int_sunlight = pd.Series(Sunlight)
    result_sun = Int_sunlight.describe()
    #print("Result for Sunlight:\n", result_sun)
    Int_shadow = pd.Series(Shadow)
    result_sh = Int_shadow.describe()
    Intensity_Gamma[time] = abs(result_sh['mean']-result_sun['mean'])*1.6*1e-9
    t = np.zeros(104)
    for i in range(0,len(t)):
        t[i] = i+1
    #plt.title("Intensity(Sunlight)")
    #plt.ylabel("Intensity on the sunlight")
    #plt.xlabel("Time")
    #plt.plot(t, Sun, 'g')
    #plt.show()
    #plt.title("Intensity(Shadow)")
    #plt.ylabel("Intensity in the shadow")
    #plt.xlabel("Time")
    #plt.plot(t, Sh, 'r')
    #plt.show()
print("Number:","Intensity of the Gamma Background:")
for i in range(0,len(Intensity_Gamma)):
    print("\n",i,"  ",Intensity_Gamma[i])
Daily_Intensity = pd.Series(Intensity_Gamma)
result_day = Daily_Intensity.describe()
print("\nDaily Intensity: ",result_day['mean'])

#print("Latitude_le")
#for j in range(0,len(Latitude)):
 #   print("\n",j," ",Latitude[j])

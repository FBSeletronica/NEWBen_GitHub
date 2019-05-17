# PROGRAMA DISTRIBUICAO GAUSIANA
import serial
import math
import time
import struct
from time import localtime, strftime
import numpy as np
import matplotlib.pyplot as plt

# Configura a serial
print "**Please Calibrate Bench and Software Before Emulating a Signal Behaviour**"
print
print "**Variable Attenuation = ((Mean Downlink Power - Fixed Attenuation - System Losses) * 2)**"
print
print "**0dB < Variable Attenuation < 63dB**"
print
n_serial = raw_input("Enter Sink Serial Port # = ") #seta a serial

ser = serial.Serial("com"+n_serial, 9600, timeout=0.5,parity=serial.PARITY_NONE) # seta valores da serial

a_serial = raw_input("Enter �Proc. Serial Port # = ") #seta a serial
arduino = serial.Serial("com"+a_serial, 9600, timeout=0.5,parity=serial.PARITY_NONE) # seta valores da serial

trans_power = raw_input("Enter Transmission Power in dBm = ") #seta a transmission power
t = int (trans_power)

atten_mean = raw_input("Enter the Variable Attenuation in dB = ") #seta a attenuation
at = float (atten_mean) #the 6-bit variable attenuator attenuates 0.5 dB per bit.

stand_dev = raw_input("Enter the Standard Deviation in dB = ") #seta a sd
sd = float (stand_dev) 

num_medidas = raw_input('Enter Number of Readings = ')
w = int(num_medidas)

# Identificacao da base
ID_base = 0

# Cria o vetor Pacote
Pacote = {}

#Cria o vetor para salvar os valores das potências
listaPotDesviod ={}
listaPotDesviou ={}

# Cria Pacote de 52 bytes com valor zero em todas as posições
for i in range(0,52): # faz um array com 52 bytes
   Pacote[i] = 0

while True:
   try:
      #Inicializacao das variaveis

      contador_tot = 0
      contador_pot = 0
      contador_erro_consec = 0
      potmediad = 0.0
      potacumulad = 0.0
      potmeddbd = 0.0
      contador_err = 0
      potmediau = 0.0
      potacumulau = 0.0
      potmeddbu = 0.0
      PER = 0

      AcumDPd = 0
      AcumDPu = 0
      AcumVad = 0
      AcumVau = 0
      MedDPd = 0
      MedDPu = 0
      DPd = 0
      DPu = 0 

      PotMaxd = -200
      PotMind = 10

      PotMaxu = -200
      PotMinu = 10

      PotTrans = t # Transmission power set on the BE900/990

      #Gera a Gaussiana
      i=0 # array for x2
      u = at # mean must lie between 0 and 16.25 mean #the 6-bit variable attenuator attenuates 0.5 dB per bit.
      o = sd # standard deviation 
      s = np.random.normal(loc=u, scale=o, size=w)
      x2 = np.array(s, 'int')

      #print x2 # Prints the array of values created by random function.
         
      Opcao = "1"

      # Limpa o buffer da serial
      ser.flushInput()

      # Coloca no pacote o ID_base
      
      Pacote[10] = int(ID_base)
      Pacote[37] = 1 #Liga o LDR

      
      if Opcao == "1":
         ID_sensor = 1  # Sensor a ser acessado
         Pacote[8] = int(ID_sensor) # Coloca no pacote o ID_sensor
         
         Atenuador = 0

         primeira_rodada = 1
              
         filename1 = strftime("Gauss_data @_%d_%m_%Y @ %H-%M-%S.csv")
         start_time = strftime("%d_%m_%Y @ %H-%M-%S")
         
         print
         print "Start Time: %s" % filename1
         print
         S = open(filename1, 'w')

         while i < w :

         # Rotina de controle da Atenuacao
                #if primeira_rodada:
                    #pass
                #else:
                Atenuador = x2[i]
                i=i+1
                config_atenuador = 1
                primeira_rodada = 0

                while config_atenuador:
                    arduino.flushInput()
                    if Atenuador >= 64:
                        comando = 63
                    elif Atenuador <= 0:
                       comando = 0
                    else:
                        comando = Atenuador
                    arduino.flushInput()
                    while arduino.inWaiting() != 1:
                       if arduino.inWaiting() < 1:
                          arduino.write(chr(comando))
                          time.sleep(0.3)
                       if arduino.inWaiting() > 1:
                          arduino.flushInput()
                          arduino.write(chr(comando))
                          time.sleep(0.3)
                           
                    atenuador_rx = arduino.read(1)
                    if ord(atenuador_rx) == comando:
                        config_atenuador = 0  
                
             #for j in range(0,w):
                ser.flushInput()
                for k in range(0,52): # transmite pacote
                   TXbyte = chr(Pacote[k])
                   ser.write(TXbyte)

                # Aguarda a resposta do sensor
                time.sleep(0.3)

                contador_tot = contador_tot + 1

                line = ser.read(52) # faz a leitura de 52 bytes do buffer que recebe da serial pela COM
                if len(line) == 52:

                   rssid = ord(line[0]) # RSSI_DownLink
                   rssiu = ord(line[2]) # RSSI_UpLink
             
                   #RSSI Downlink
                   if rssid > 128:
                      RSSId=((rssid-256)/2.0)-74
                
                   else:
                      RSSId=(rssid/2.0)-74

                   #RSSI Uplink
                   if rssiu > 128:
                      RSSIu=((rssiu-256)/2.0)-74
                
                   else:
                      RSSIu=(rssiu/2.0)-74

                   count = ord(line[12])  # contador de pacotes enviados pelo sensor

                   if RSSId > PotMaxd:
                      PotMaxd = RSSId
                   
                   if RSSId < PotMind:   
                      PotMind = RSSId

                   if RSSIu > PotMaxu:
                      PotMaxu = RSSIu
                   
                   if RSSIu < PotMinu:   
                      PotMinu = RSSIu
                   
                   Attenuationd = (RSSId*-1) + PotTrans
                   Attenuationu = (RSSIu*-1) + PotTrans
                   
                   listaPotDesviod[contador_pot]= RSSId   #Grava a potencia de downlink para calculo do desvio padrao
                   listaPotDesviou[contador_pot]= RSSIu   #Grava a potencia de uplink para calculo do desvio padrao

                   contador_pot=contador_pot+1 #incrementa o contador utilizado para a media de potencia e para o desvio padrao

                   potmwd = pow(10,(RSSId/10))   #converte a potencia de downlink em dBm para mW.
                   potacumulad = potacumulad + potmwd  #Soma a potencia em mW em um acumulador

                   potmwu = pow(10,(RSSIu/10))   #converte a potencia de uplink em dBm para mW
                   potacumulau= potacumulau + potmwu

                   contador_erro_consec = 0
                   
                   print'Packet Number = ',contador_tot, ' RSSI DownLink = ',  RSSId, 'dBm ', '  RSSI UpLink = ', RSSIu, 'dBm ', ' Attenuation = ', comando/2.0, 'dB '           
                   print >>S,time.asctime(),' ;Packet Number =; ',contador_tot, ';RSSI DownLink =; ', RSSId, '  ;RSSI UpLink =; ', RSSIu, ';Attenuation =; ', comando, 'dB '
                     
                else:
                     contador_erro_consec = contador_erro_consec + 1 #counts the number of consecutive errors
                     contador_err = contador_err + 1 #counts the number of errors
                     print'Packet Number = ',contador_tot, ' Attenuation = ', comando/2.0, 'dB ',' Packet Loss '
                     print >>S,time.asctime(),' Packet Loss'
                     ser.flushInput()
                     
                if contador_erro_consec >= 3:
                   ser.close() # closes and resets the serial
                   ser = serial.Serial("com"+n_serial, 9600, timeout=0.5,parity=serial.PARITY_NONE) # seta valores da serial
                   contador_erro_consec = 0
                   time.sleep(1)      
                
                time.sleep(0.7)

         for l in range(0,contador_pot):
            AcumVad =AcumVad+ listaPotDesviod[l]   #acumula o valor da lista para calcular a media
            AcumVau =AcumVau+ listaPotDesviou[l]   #acumula o valor da lista para calcular a media

         MedDPd = float (AcumVad)/float(contador_pot)
         MedDPu = float (AcumVau)/float(contador_pot)

         for m in range(0,contador_pot):
            AcumDPd =AcumDPd+ pow((listaPotDesviod[m]- MedDPd),2)   #acumula o valor da variancia
            AcumDPu =AcumDPu+ pow((listaPotDesviou[m]- MedDPu),2)  #acumula o valor da variancia

         DPd = float (AcumDPd)/float(contador_pot)   #termina o calculo da variancia
         DPu = float (AcumDPu)/float(contador_pot)   #termina o calculo da variancia

         potmediad = potacumulad /contador_pot
         potmeddbd = 10*math.log10(potmediad)
         print
         print 'Gaussian Bench Statistics For a', w, 'Readings'
         print
         print 'Maximum Downlink Power:', "%.2f" %PotMaxd,' dBm'
         print 'Minimum Downlink Power:', "%.2f" %PotMind,' dBm'
         print 'Mean Downlink Power:', "%.2f" %potmeddbd,' dBm'
         print 'Downlink Standard Deviation:', "%.2f" %DPd, 'dB'
         print
         print >>S,time.asctime(),';Maximum Downlink Power:;', "%.2f" %PotMaxd,' ;dBm;'
         print >>S,time.asctime(),';Minimum Downlink Power:;', "%.2f" %PotMind,' ;dBm;'
         print >>S,time.asctime(),';Mean Downlink Power:;', "%.2f" %potmeddbd,' ;dBm;'
         print >>S,time.asctime(),';Downlink Standard Deviation:;', "%.2f" %DPd,' ;dB;'

         potmediau = potacumulau /contador_pot
         potmeddbu = 10*math.log10(potmediau)
         
         print 'Maximum Uplink Power:', "%.2f" %PotMaxu,' dBm'
         print 'Minimum Uplink Power:', "%.2f" %PotMinu,' dBm'
         print 'Mean Uplink Power:', "%.2f" %potmeddbu,' dBm'
         print 'Uplink Standard Deviation:', "%.2f" %DPu, 'dB'
         
         print >>S,time.asctime(),';Maximum Uplink Power:;', "%.2f" %PotMaxu,' ;dBm;'
         print >>S,time.asctime(),';Minimum Uplink Power:;', "%.2f" %PotMinu,' ;dBm;'
         print >>S,time.asctime(),';Mean Uplink Power:;', "%.2f" %potmeddbu,' ;dBm;'
         print >>S,time.asctime(),';Uplink Standard Deviation:;', "%.2f" %DPu,' ;dB;'
         print
         PER = (float(contador_err)/float(contador_tot))* 100

         print 'Total PER:', float(PER),'%'
         print >>S,time.asctime(),';PER:;', float(PER),';%;'
         print
         finish_time = strftime("%d_%m_%Y @ %H-%M-%S")
         print "Start Time: %s"% start_time,',', "End Time: %s"   % finish_time  
         
         S.close()
         
         ser.close() # fecha a porta COM
         print 'End of Programme'  # escreve na tela
         break
            
   except KeyboardInterrupt:
       S.close()
       ser.close()

       break


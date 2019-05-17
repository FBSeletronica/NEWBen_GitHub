# PROGRAMA DISTRIBUICAO NORMAL
import serial
import math
import time
import struct
from time import localtime, strftime

contador_erro_consec = 0

# Configura a serial
n_serial = raw_input("Enter Sink Serial Port # = ") #seta a serial

ser = serial.Serial("com"+n_serial, 9600, timeout=0.5,parity=serial.PARITY_NONE) # seta valores da serial

num_medidas = raw_input('Enter Number of Readings = ')
w = int(num_medidas)

# Identificacao da base
ID_base = 0

# Cria o vetor Pacote
Pacote = {}

#Cria o vetor para salvar os valores das potências
listaPotDesviod ={}
listaPotDesviou ={}

listaAttDesviod ={}
listaAttDesviou ={}

# Cria Pacote de 52 bytes com valor zero em todas as posições
for i in range(0,52): # faz um array com 52 bytes
   Pacote[i] = 0

while True:
   try:
      #Inicializacao das variaveis

      contador_tot = 0
      contador_pot = 0
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

      PotTrans = 10 # Transmission power set on the BE900/990
      FixAtten = 37 # Fixed amount of attenuation plus sistemic losses on the emulation bench.
      
      contador_Att = 0
      Attmediad = 0.0
      Attacumulad = 0.0
      Attmeddbd = 0.0
      Attmediau = 0.0
      Attacumulau = 0.0
      Attmeddbu = 0.0

      AttAcumDPd = 0
      AttAcumDPu = 0
      AttAcumVad = 0
      AttAcumVau = 0
      AttMedDPd = 0
      AttMedDPu = 0
      AttDPd = 0
      AttDPu = 0
      
      Opcao = "1"

      # Coloca no pacote o ID_base
      
      Pacote[10] = int(ID_base)
      
      if Opcao == "1":
         ID_sensor = 1  # Sensor a ser acessado
         Pacote[8] = int(ID_sensor) # Coloca no pacote o ID_sensor
              
         filename1 = strftime("Validation_data @_%d_%m_%Y @ %H-%M-%S.csv")
         start_time = strftime("%d_%m_%Y @ %H-%M-%S")
         print
         print "Start Time: %s" % filename1
         print
         S = open(filename1, 'w')
  
         for j in range(0,w):
            # Limpa o buffer da serial
                ser.flushInput()
                for k in range(0,52): # transmite pacote
                   TXbyte = chr(Pacote[k])
                   ser.write(TXbyte)

                # Aguarda a resposta do sensor
                time.sleep(0.5)

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
                   
                   Attenuationd = (RSSId*-1) + PotTrans # Attenuation
                   Attenuationu = (RSSIu*-1) + PotTrans
 
                   listaPotDesviod[contador_pot]= RSSId   #Grava a potencia de downlink para calculo do desvio padrao
                   listaPotDesviou[contador_pot]= RSSIu   #Grava a potencia de uplink para calculo do desvio padrao

                   listaAttDesviod[contador_Att]= Attenuationd   #Grava a attenuation de downlink para calculo do desvio padrao
                   listaAttDesviou[contador_Att]= Attenuationu   #Grava a attenuation de uplink para calculo do desvio padrao

                   contador_pot=contador_pot+1 #incrementa o contador utilizado para a media de potencia e para o desvio padrao

                   contador_Att=contador_Att+1 #incrementa o contador utilizado para a media da attenuation e para o desvio padrao

                   potmwd = pow(10,(RSSId/10))   #converte a potencia de downlink em dBm para mW.
                   potacumulad = potacumulad + potmwd  #Soma a potencia em mW em um acumulador

                   Attmwd = pow(10,(Attenuationd/10))   #converte a attenuation de downlink em dBm para mW.
                   Attacumulad = Attacumulad + Attmwd  #Soma a attenuation em mW em um acumulador             
                   
                   potmwu = pow(10,(RSSIu/10))   #converte a potencia de uplink em dBm para mW
                   potacumulau= potacumulau + potmwu # Soma a potencia em mW em um acumulador

                   Attmwu = pow(10,(Attenuationu/10))   #converte a attenuation de uplink em dBm para mW.
                   Attacumulau = Attacumulau + Attmwu  #Soma a attenuation em mW em um acumulador   
                   
                   contador_erro_consec = 0
                   
                   print'Packet Number = ',contador_tot, ' RSSI DownLink = ', RSSId, 'dBm ', ' RSSI UpLink = ', RSSIu, 'dBm ' , ' Atten. DownLink = ', Attenuationd, 'dBm ' , ' Atten. UpLink = ', Attenuationu, 'dB '          

                   print >>S,time.asctime(),' ;Packet Number =; ',contador_tot, ' ;RSSI DownLink =; ', RSSId, ' ;RSSI UpLink =;', RSSIu, ' ;Atten. DownLink =;', Attenuationd, ' ;Atten. UpLink =;', Attenuationu
                  
                else:
                     contador_erro_consec = contador_erro_consec + 1 #counts the number of consecutive errors
                     contador_err = contador_err + 1 #counts the number of errors
                     print'Packet Number = ',contador_tot,' Packet Loss '
                     print >>S,time.asctime(),' ;Packet Loss; '
                     ser.flushInput()
                     
                if contador_erro_consec >= 3:
                   ser.close() # closes and resets the serial
                   ser = serial.Serial("com"+n_serial, 9600, timeout=0.5,parity=serial.PARITY_NONE) # seta valores da serial
                   contador_erro_consec = 0
                   time.sleep(0.5)      
                
                time.sleep(1.0)

         for l in range(0,contador_pot):
            AcumVad =AcumVad+ listaPotDesviod[l]   #acumula o valor da lista para calcular a media
            AcumVau =AcumVau+ listaPotDesviou[l]   #acumula o valor da lista para calcular a media
            
            AttAcumVad =AttAcumVad+ listaAttDesviod[l]   #acumula o valor da lista para calcular a media
            AttAcumVau =AttAcumVau+ listaAttDesviou[l]   #acumula o valor da lista para calcular a media

         MedDPd = float (AcumVad)/float(contador_pot) # encontra a media
         MedDPu = float (AcumVau)/float(contador_pot) # encontra a media
         
         AttMedDPd = float (AttAcumVad)/float(contador_Att) # encontra a media da atenuacao
         AttMedDPu = float (AttAcumVau)/float(contador_Att) # encontra a media da atenuacao
         
         for m in range(0,contador_pot):
            AcumDPd =AcumDPd+ pow((listaPotDesviod[m]- MedDPd),2)  #acumula o valor da variancia
            AcumDPu =AcumDPu+ pow((listaPotDesviou[m]- MedDPu),2)  #acumula o valor da variancia

            AttAcumDPd =AttAcumDPd+ pow((listaAttDesviod[m]- AttMedDPd),2)  #acumula o valor da variancia da attenuation
            AttAcumDPu =AttAcumDPu+ pow((listaAttDesviou[m]- AttMedDPu),2)  #acumula o valor da variancia da attenuation

         Vard = float (AcumDPd)/float(contador_pot)   #termina o calculo da variancia
         Varu = float (AcumDPu)/float(contador_pot)   #termina o calculo da variancia

         DPd = Vard ** 0.5 # calculates the square root
         DPu = Varu ** 0.5 # calculates the square root

         AttVard = float (AttAcumDPd)/float(contador_Att)   #termina o calculo da variancia da atenuacao
         AttVaru = float (AttAcumDPu)/float(contador_Att)   #termina o calculo da variancia da atenuacao

         AttDPd = (AttVard ** 0.5) # calculates the square root
         AttDPu = AttVaru ** 0.5 # calculates the square root

         potmediad = potacumulad /contador_pot
         potmeddbd = 10*math.log10(potmediad) #Retorna o logaritmo de base 10.

         Attmediad = Attacumulad /contador_Att
         Attmeddbd = 10*math.log10(Attmediad) #Retorna o logaritmo de base 10.
         
         print
         print 'Validation Statistics For a', w, 'Readings'
         print
         print 'Maximum Downlink Power:', "%.2f" %PotMaxd,' dBm'
         print 'Minimum Downlink Power:', "%.2f" %PotMind,' dBm'
         print 'Mean Downlink Power:', "%.2f" %potmeddbd,' dBm'
         print 'Downlink Standard Deviation:', "%.2f" %DPd, 'dB'
         print
         print 'Downlink Attenuation Mean:', "%.2f" %Attmeddbd,' dB'
         print 'Downlink Attenuation Standard Deviation:', "%.2f" %AttDPd, ' dB'
         print >>S
         print >>S,time.asctime(),';Maximum Downlink Power:;', "%.2f" %PotMaxd,' ;dBm;'
         print >>S,time.asctime(),';Minimum Downlink Power:;', "%.2f" %PotMind,' ;dBm;'
         print >>S,time.asctime(),';Mean Downlink Power:;', "%.2f" %potmeddbd,' ;dBm;'
         print >>S,time.asctime(),';Downlink Standard Deviation:;', "%.2f" %DPd,' ;dB;'
         print >>S
         print >>S,time.asctime(),';Downlink Attenuation Mean:;', "%.2f" %Attmeddbd,' ;dB;'
         print >>S,time.asctime(),';Downlink Attenuation Standard Deviation:;', "%.2f" %AttDPd,' ;dB;'
         print
         potmediau = potacumulau/contador_pot
         potmeddbu = 10*math.log10(potmediau)

         Attmediau = Attacumulau /contador_Att
         Attmeddbu = 10*math.log10(Attmediau)

         #EmulationAtten = Attmeddbd - FixAtten + PotTrans
         EmulationAtten = (Attmeddbd - FixAtten) * 2 #Because the variable attenuator sets .5 db per unit values set.

         print 'Maximum Uplink Power:', "%.2f" %PotMaxu,' dBm'
         print 'Minimum Uplink Power:', "%.2f" %PotMinu,' dBm'
         print 'Mean Uplink Power:', "%.2f" %potmeddbu,' dBm'
         print 'Uplink Standard Deviation:', "%.2f" %DPu, 'dB'
         print
         print 'Uplink Attenuation Mean:', "%.2f" %Attmeddbu,' dB'
         print 'Uplink Attenuation Standard Deviation:', "%.2f" %AttDPu,' dB'
         print
         print '*Emulation Bench Data* - Attenuation Mean:', "%.2f" %EmulationAtten,' dB'
         print '*Emulation Bench Data* - Standard Deviation:', "%.2f" %AttDPd,' dB'
         print
         print >>S
         print >>S,time.asctime(),';Maximum Uplink Power:;', "%.2f" %PotMaxu,' ;dBm;'
         print >>S,time.asctime(),';Minimum Uplink Power:;', "%.2f" %PotMinu,' ;dBm;'
         print >>S,time.asctime(),';Mean Uplink Power:;', "%.2f" %potmeddbu,' ;dBm;'
         print >>S,time.asctime(),';Uplink Standard Deviation:;', "%.2f" %DPu,' ;dB;'
         print >>S
         print >>S,time.asctime(),';Uplink Attenuation mean:;', "%.2f" %Attmeddbu,' ;dB;'
         print >>S,time.asctime(),';Uplink Attenuation Standard Deviation:;', "%.2f" %AttDPu,' ;dB;'
         print >>S
         print >>S,time.asctime(),';*Emulation Bench Data* - Attenuation Mean:;', "%.2f" %EmulationAtten,' ;dB;'
         print >>S,time.asctime(),';*Emulation Bench Data* - Standard Deviation:;', "%.2f" %AttDPd,' ;dB;'
         
         PER = (float(contador_err)/float(contador_tot))* 100

         print 'Total PER:', "%.2f" %PER,'%'
         print>>S
         print >>S,time.asctime(),';PER:;', "%.2f" %PER,'%'
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


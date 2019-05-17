import schedule
import time
from Tkinter import *
import tkMessageBox
from ScrolledText import ScrolledText
import threading
import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg,    NavigationToolbar2TkAgg
from matplotlib.figure import Figure
from matplotlib import style
from datetime import datetime
import serial
import math
import struct
from time import localtime, strftime
import numpy as np
import matplotlib.pyplot as plt
import scipy.stats
from scipy.stats import weibull_min

style.use("ggplot")

start_time = strftime("%d_%m_%Y @ %H-%M-%S")

global s1, ser, arduino, p_env, p_rec

# classe que herda os metodos para tratar threads:parar e iniciar
class myThread(threading.Thread):
    def __init__(self, function):
        self.running = False
        self.function = function
        super(myThread, self).__init__()

    def start(self):
        self.running = True
        super(myThread, self).start()

    def run(self):
        while self.running:
            self.function()

    def stop(self):
        self.running = False

#funcao que gera os graficos usando a matplotlib
def grafico_e():
        fig = plt.figure()
        fig.subplots_adjust( hspace=0.65 )
        ax1 = fig.add_subplot(111)
        x = []
        y = []
        try:
            dados = open("Gauss_Screen_data.csv",'r')
            
        except Exception as erro:
            tkMessageBox.showinfo(message=erro)
        for line in dados:
            line=line.strip()
            print (line)
            X, Y = line.split(';')
            x.append(float(X))
            y.append(float(Y))
        dados.close()
        
        ax1.plot(y,label='RSSI_Down')
        ax1.plot(x,label='RSSI_Up')
        ax1.set_title('RSSI Readings')
        ax1.set_xlabel('Number of Readings')
        ax1.set_ylabel('RSSI')
        ax1.legend()
                
        plt.rcParams['figure.figsize'] = (17,17)
        plt.show()

def start_rede():
     schedule.every(3).seconds.do(medir)
     while True: #loop infinito
        schedule.run_pending() #realiza as tarefas agendadas
        time.sleep(1)

def inicia(ope):
    global op
    op=ope
    v1 = myThread(function = start_rede) 
    if(ope==1):
        v1.start()
    elif(ope==0):
        schedule.clear()
        v1.stop()
        botao3.config(state="normal")

def verificar_portas():
    portas_ativas = []
    for n in range(100):
        try:
            ver=serial.Serial("COM"+str(n))
            portas_ativas.append(ver.portstr)
            ver.close()
        except serial.SerialException:
            pass
    return portas_ativas

def callback():
    if tkMessageBox.askokcancel("Sure you want to leave?"):
        inicia(0)
        raiz.destroy()

def enviar():
    try:
        global ser, p_env,p_rec, media_rssi
        p_env=0
        p_rec=0
        media_rssi = 0
        print 'Test Sent to Sink Node'
        
        Pacote = {}
        ser = serial.Serial(p.get(), 9600, timeout=0.5) # seta valores da serial
                
        time.sleep(1.6)

        ID_sensor = 1
        ID_base = 0

        # Cria Pacote de 52 bytes com valor zero em todas as posições
        for i in range(0,52): # faz um array com 52 bytes
           Pacote[i] = 0

        # Limpa o buffer da serial
        ser.flushInput()

        # Coloca no pacote o ID_sensor e ID_base
        Pacote[8] = ID_sensor #origem
        
        Pacote[10] = ID_base #destino
        Pacote[49] = 1 #1 indica pacote de apenas requisicao
        
        # TX pacote - envia pacote para a base transmitir
        for i in range(0,52):
           TXbyte = chr(Pacote[i]) # Deve converter para caracter em ASCII para escrever na serial
           ser.write(TXbyte)

        # Tempo de espera para que receba a resposta do sensor
        time.sleep(0.3)

        # RX pacote - recebe o pacote enviado pelo sensor
        line = ser.read(52) # faz a leitura de 52 bytes do buffer que recebe da serial pela COM
        
        # Checa se recebeu 52 bytes 
        if len(line) == 52:
           print 'OK'
           tkMessageBox.showinfo(message="Port "+ p.get()+ " Connected")
           
        else:
           print 'ERROR'
           tkMessageBox.showinfo(message="Port "+ p.get() + " NOT Connected")
           time.sleep(0.3)
           ser.flushInput()

    except Exception as error:
        tkMessageBox.showinfo(message=error)

def enviar1():
    try:
        global arduino
        print 'Test Sent to Micro-Contoller'
        
        Pacote1 = {}
        
        arduino = serial.Serial(p1.get(), 9600, timeout=0.5) # seta valores da serial
                
        time.sleep(1.6)  

        # Cria Pacote de 52 bytes com valor zero em todas as posições
        for i in range(0,1): # faz um array com 1 byte
           Pacote1[i] = 0

        # Limpa o buffer da serial
        arduino.flushInput()

        for i in range(0,1):
           TXbyte = chr(Pacote1[i]) # Deve converter para caracter em ASCII para escrever na serial
           arduino.write(TXbyte)

        # Tempo de espera para que receba a resposta do sensor
        time.sleep(0.3)

        # RX pacote - recebe o pacote enviado pelo sensor
        line = arduino.read(52) # faz a leitura de 52 bytes do buffer que recebe da serial pela COM
        
        # Checa se recebeu 52 bytes 
        if len(line) == 1:
           print 'OK'
           tkMessageBox.showinfo(message="Port "+ p1.get()+ " Connected")
           
        else:
           print 'ERROR'
           tkMessageBox.showinfo(message="Port "+ p1.get() + " NOT Connected")
           time.sleep(0.3)
           arduino.flushInput()

    except Exception as erro:
         tkMessageBox.showinfo(message=erro)
         
#def parar():
    #sys.exit()

def medir():
    global ser, arduino, p_rec, p_env, media_rssi
    p_env=p_env+1
   
    conteudo.config(state="normal")
    
    ID_base = 0
    w = int(data_medidas.get())

    # Cria o vetor Pacote
    Pacote = {}

    #Cria o vetor para salvar os valores das potÃªncias
    listaPotDesviod ={}
    listaPotDesviou ={}

    # Cria Pacote de 52 bytes com valor zero em todas as posiÃ§Ãµes
    for i in range(0,52): # faz um array com 52 bytes
       Pacote[i] = 0

    while True:
       try:
          #Inicializacao das variaveis

          contador_erro_consec = 0
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

          #Gera a distribuição
          i = 0 # array de x2
          u = float(data_param1.get())# mean
          o = float(data_param2.get())# standard deviation
          x = float(data_param3.get())#TBD
          s = np.random.normal(loc=u, scale=o, size=w)
          x2 = np.array(s, 'int')
             
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
                  
             filename1 = strftime("Gauss_Screen_stats @_%d_%m_%Y_%H-%M-%S.csv")
             print
             print "Start Time: %s" % filename1
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
                        arduino.write(chr(comando))
                        time.sleep(0.3)
                        atenuador_rx = arduino.read(1)
                        if ord(atenuador_rx) == comando:
                            config_atenuador = 0  

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

                       num_pacote = ord(line[12])
                       rssi_t = str(RSSId) 
                       rssi_w = (1* pow(10,-3))*pow(10,(RSSId/10.0))
                       media_rssi = media_rssi + rssi_w

                       conteudo.insert(END, str(num_pacote)+  " RSSId: "+str(RSSId)+ "dBm" + " RSSIu: "+str(RSSIu)+ "dBm"'\n')

                       conteudo.see("end") 

                       count = ord(line[12]) # contador de pacotes enviados pelo sensor
                       s1=("Gauss_Screen_Data.csv")
                      
                       S1 = open(s1, 'a')
                       S1.write(str(RSSId)+';'+str(RSSIu)+'\n') 

                       if RSSId > PotMaxd:
                          PotMaxd = RSSId
                       
                       if RSSId < PotMind:   
                          PotMind = RSSId

                       if RSSIu > PotMaxu:
                          PotMaxu = RSSIu
                       
                       if RSSIu < PotMinu:   
                          PotMinu = RSSIu
                                       
                       listaPotDesviod[contador_pot]= RSSId   #Grava a potencia de downlink para calculo do desvio padrao
                       listaPotDesviou[contador_pot]= RSSIu   #Grava a potencia de uplink para calculo do desvio padrao

                       contador_pot=contador_pot+1 #incrementa o contador utilizado para a media de potencia e para o desvio padrao

                       potmwd = pow(10,(RSSId/10))   #converte a potencia de downlink em dBm para mW.
                       potacumulad = potacumulad + potmwd  #Soma a potencia em mW em um acumulador

                       potmwu = pow(10,(RSSIu/10))   #converte a potencia de uplink em dBm para mW
                       potacumulau= potacumulau + potmwu #Soma a potencia em mW em um acumulador           

                    else:          
                         conteudo.insert(END,"Packet Loss "'\n')
                         conteudo.see("end")

                         contador_erro_consec = contador_erro_consec + 1 #counts the number of consecutive errors
                         contador_err = contador_err + 1
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
             
             print >>S
             print >>S,time.asctime(),';Maximum Downlink Power:;', "%.2f" %PotMaxd,' ;dBm;'
             print >>S,time.asctime(),';Minimum de Downlink Power:;', "%.2f" %PotMind,' ;dBm;'
             print >>S,time.asctime(),';Mean Downlink Power:;', "%.2f" %potmeddbd,' ;dBm;'
             print >>S,time.asctime(),';Downlink Standard Deviation:;', "%.2f" %DPd,' ;dB;'
         
             potmediau = potacumulau /contador_pot
             potmeddbu = 10*math.log10(potmediau)
             
             print >>S
             print >>S,time.asctime(),';Maximum Uplink Power:;', "%.2f" %PotMaxu,' ;dBm;'
             print >>S,time.asctime(),';Minimum Uplink Power:;', "%.2f" %PotMinu,' ;dBm;'
             print >>S,time.asctime(),';Mean Uplink Power:;', "%.2f" %potmeddbu,' ;dBm;'
             print >>S,time.asctime(),';Uplink Standard Deviation:;', "%.2f" %DPu,' ;dB;'
      
             PER = (float(contador_err)/float(contador_tot))* 100
             print >>S
             print >>S,time.asctime(),';PER:;', "%.2f" %PER,';%;'
             print
             finish_time = strftime("%d_%m_%Y @ %H-%M-%S")
             print "Start Time: %s"% start_time,',', "End Time: %s"   % finish_time  
             S.close()
             ser.close() # fecha a porta COM
             break
                
       except KeyboardInterrupt:
           S.close()
           ser.close()

           break
       conteudo.see("end") 

def nova():    
        jan=Toplevel()
        fig = Figure(figsize=(6, 4), facecolor='white')
        b=Button(jan, text='Save Graphic', command=lambda:salvar(fig))
        b.grid(row = 0, column=0)
        canvas = FigureCanvasTkAgg(fig, master=jan)
        canvas.get_tk_widget().grid(row=3, column=1, columnspan=3, sticky='NSEW')
        grafico(fig,canvas)
  
def salvar(ff):
        ftypes = [('.png (PNG)', '*.png')]
        f = asksaveasfilename(filetypes=ftypes, defaultextension=".png")
        #print(f)

        #if f != '':
            #ff.savefig(f)
        
raiz=Tk() #cria a tela principal , usando um objeto TKinter
raiz.configure(background='powder blue')
raiz.title(" NEWBen - Network Emulation WorkBench ") #funcao para alterar titulo da janela

label_dados=Label(master=raiz, font=("Arial", 14, "bold"),text = "SETTINGS",padx=5,pady=5)
label_dados.configure(background='powder blue')

label_param=Label(master=raiz,font=("Arial", 14, "bold"), text = " RESULTS",padx=5,pady=5)
label_param.configure(background='powder blue')

label_dados.grid(row=0,column=0,columnspan=4)
label_param.grid(row=0,column=32,columnspan=4)

p = StringVar()
portas = ttk.Combobox(width=16,textvariable = p)
portas.grid(row=1,column=1)
portas['values']= verificar_portas()

p1 = StringVar()
portas1 = ttk.Combobox(width=16,textvariable = p1)
portas1.grid(row=2,column=1)
portas1['values']= verificar_portas()

btn_teste=Button(raiz,text="Sink Serial",command=enviar)
btn_teste.configure(font=("Arial", 10, "bold"),background='powder blue')
btn_teste.grid(row=1,column=0)

btn_teste1=Button(raiz,text="Proces. Serial",command=enviar1)
btn_teste1.configure(font=("Arial", 10, "bold"),background='powder blue')
btn_teste1.grid(row=2,column=0)

data_param1=Entry(raiz)
data_param1.grid(row=4,column=1)
data_param1.config(state="normal")

label_a=Label(master=raiz,text = "Attenuation Mean")
label_a.configure(background='powder blue')
label_a.grid(row=4,column=0)

data_param2=Entry(raiz)
data_param2.grid(row=5,column=1)
data_param2.config(state="normal")

label_a1=Label(master=raiz,text = "Stand. Deviation")
label_a1.configure(background='powder blue')
label_a1.grid(row=5,column=0)

data_param3=Entry(raiz)
data_param3.grid(row=6,column=1)
data_param3.config(state="normal")

label_a2=Label(master=raiz,text = "TBD")
label_a2.configure(background='powder blue')
label_a2.grid(row=6,column=0)

data_medidas=Entry(raiz)
data_medidas.grid(row=7,column=1)
data_medidas.config(state="normal")

label_med=Label(master=raiz,text = "Number of Readings")
label_med.configure(background='powder blue')
label_med.grid(row=7,column=0)

botao3=Button(raiz,text="Start Readings",command= lambda:inicia(1))
botao3.configure(font=("Arial", 10, "bold"),background='powder blue')
botao3.grid(row=1,column=34,padx=5,pady=5,sticky='NSEW')

conteudo = ScrolledText(raiz,width=35,height=15,padx=5,pady=5)
conteudo.config(state="disabled")
conteudo.grid(row=2,column=34,rowspan=8,padx=5,pady=5,sticky='NSEW')

botao4=Button(raiz,text="Get Graphic",command=grafico_e)
botao4.configure(font=("Arial", 10, "bold"),background='powder blue')
botao4.grid(row=25,column=34,padx=5,pady=5,sticky='NSEW')
botao4.config(state="normal")

raiz.protocol("WM_DELETE_WINDOW", callback)
raiz.mainloop()


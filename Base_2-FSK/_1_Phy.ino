// Phy : classe da camada Fisica

// Mais informacoes acesse www.radiuino.cc
// Copyright (c) 2015
// Author: Pedro Henrique Gomes, Omar C. Branquinho, Tiago T. Ganselli, Debora M. Ferreira, Guilherme Lopes da Silva, Raphael Montali de Assumpçao.
// Versao 2.3: 18/05/2017

// Este arquivo e parte da plataforma Radiuino
// Este programa e um software livre; voce pode redistribui-lo e/ou modifica-lo dentro dos termos da Licenca Publica Geral Menor GNU 
// como publicada pela Fundacao do Software Livre (FSF); na versao 2 da Licenca, ou (na sua opniao) qualquer futura versao.
// Este programa e distribuido na esperanca que possa ser  util, mas SEM NENHUMA GARANTIA; sem uma garantia implicita 
// de ADEQUACAO a qualquer MERCADO ou APLICACAO EM PARTICULAR. Veja a Licenca Publica Geral Menor GNU para maiores detalhes.
// Voce deve ter recebido uma copia da Licenca Publica Geral Menor GNU junto com este programa, se nao, escreva para a Fundacao 
// do Software Livre(FSF) Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
    
// This library is free software; you can redistribute it and/or modify it under the terms of the GNU Lesser General Public License 
// as published by the Free Software Foundation; either version 2 of the License, or (at your option) any later version. This library 
// is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY 
// or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more details. You should have received a copy 
// of the GNU Lesser General Public License along with this library; if not, write to the Free Software Foundation, Inc., 51 Franklin St, 
// Fifth Floor, Boston, MA  02110-1301  USA

#include "Headers.h"

/** Construtor da camada Fisica. */

PHY::PHY()
{  
 /********** AJUSTE DE Potencia *************/
 /* A Potencia de transmissao pode ser escolhida entre 8 valores possíveis (0 a 7).
  * Em geral a Potencia e ajustada para o maximo de 7 (10 dBm).
  * Abaixo esta a tabela que relaciona o numero com a Potencia de transmissao.
  * | -30 | -20 | -15 | -10 |   0 |   5 |   7 |  10 |   - Potencia em dBm
  * |   0 |   1 |   2 |   3 |   4 |   5 |   6 |   7 |   - numero que deve ser colocado na Potencia
  * !! ATENÇÃO !!: Potencias maiores que 0dBm podem fazer com que as placas percam a comunicacão quando estão muito próximas.
  *                Recomendamos posicion�-las com uma dist�ncia m�nima de 1 metro. */
  power = 7;                 

  /********** CANAL DE COMUNICAÇÃO **********/
  /* Pode ser escolhido de 0 a 65. Os canais estão espa�ados de 125kHz e dispostos na faixa de 915 a 923.125 MHz */
  channel = 40;               /* Canal */
  
  /********** AJUSTE DE OFFSET **********/
  /* A diferen�a de frequência dos cristais de cada placa deve ser compensada.
   * Este valor esta escrito em cada placa do BE900. */
  freq_offset = 0x11;        /* Offset de Frequencia */
  
  /********** VELOCIDADE DA SERIAL **********/
  serial_baudrate = 9600;    /* Serial baudrate */ 

  /************ 0 - BE900/RFBee || 1 - BE990***************/
  set_radio = 0;
}

/** Inicializa a camada F�sica. */

void PHY::initialize(void)
{
  /* Configurando o serial baudrate */
  Serial.begin(serial_baudrate);
  
  //* Inicializa o transceptor CC1101 */
  cc1101.PowerOnStartUp();
  
  /* Inicializa a Configuracao do transceptor CC1101 */
  initCC1101Config();
  
  /* Configura o canal a ser usada */
  setChannel(channel);

  /* Configura a Potencia a ser usada */
  setPower(power);
  
  /* Configura o offset de frequência */
  setFreqOffset(freq_offset);

  /*Configura o tipo de rádio*/
  setRadio(set_radio);
  
  /************************
   * CONTROLE DOS LEDs    *
   ************************/
  /* O Led VERDE (Pino 6) pisca ao RECEBER um pacote, mesmo que ele nao seja processado.
   * Para desabilitar essa funcao, escreva 0 na variavel abaixo. */
  Phy.RxLedBlink = 1;
  
  /* O Led VERMELHO (Pino 4) pisca ao ENVIAR um pacote.
   * Para habilitar essa funcao, escreva 1 na variavel abaixo. */
  Phy.TxLedBlink = 1; 
  
}

/** Recebe dados da porta serial. */

void PHY::receiveSerial(void) 
{ 
  byte len;             /* Tamanho do dado recebido pela porta serial */
  byte fifoSize = 0;    /* Tamanho do espaco livre no FIFO de TX */
 
  static byte pos = 0;  /* Total de bytes recebidos pela porta serial */
  
  /* Le a porta serial e incrementa o total de bytes recebidos */
  len = Serial.available() + pos;
  
  /* Processa no maximo BUFFLEN bytes */
  if (len > BUFFLEN ) 
  {
    len = BUFFLEN;
  }
  
  /* Verifica quanto espaco temos no FIFO de TX */
  fifoSize = Phy.txFifoFree();   /* O fifoSize deve ter o numero de bytes atualmente livre no FIFO de TX */
  
  /* Reinicializa as variaveis e sai da funcao */
  if ( fifoSize <= 0)
  {
    Serial.flush();
    pos = 0;
    return;
  }
  
  /* Evita estourar o FIFO de TX */
  if (len > fifoSize) 
  {
    len = fifoSize;  
  }
    
  /* Finalmente escreve os dados lidos da serial no FIFO de TX */
  for (byte i = pos; i < len; i++)
  {
    serialData[i] = Serial.read();  /* serialData eh o nosso buffer global */
  }
    
  /* Atraso de 1 milissegundo */
  delayMicroseconds(1000);
  
  /* Verifica se existem mais dados para receber */
  if ((Serial.available() > 0)  && (len < CC1101_PACKT_LEN))
  {
    pos = len;  /* Mantem a quantidade de bytes ja recebidos e espera pela proxima entrada nessa funcao */
    return;
  }
  
  if (len == sizeof(packet))
  {     
    /* Aguarda enquanto o canal esta sendo utilizado */
    while(Phy.carrierSense());

    /* Envia a mensagem recebida pelo RF */
    Phy.send((packet *)serialData);
    
    /* O buffer da serial esta livre novamente */
    pos = 0; 
  }
  else 
  {
    Serial.flush();
    pos = 0;
    return;
  }
}

/**
 * Transmite dados pela porta serial.
 */
void PHY::sendSerial(packet * pkt) 
{ 
  /* Escreve o pacote inteiro na porta serial */
  Serial.write((byte *)pkt, sizeof(packet)); 
}

/**
 * Le o espaco disponivel no FIFO de TX.
 */
byte PHY::txFifoFree(void) 
{
  byte size;

  cc1101.Read(CC1101_TXBYTES, &size);
  
  /* Trata um possivel underflow to FIFO de TX */
  if (size >= 64)
  {
    cc1101.Strobe(CC1101_SFTX);
    cc1101.Read(CC1101_TXBYTES,&size);
  }
  
  return (CC1101_FIFO_SIZE - size);
}

/**
 * Ajusta o canal a ser usado.
 */
void PHY::setChannel(byte channel)
{
  cc1101.Write(CC1101_CHANNR, channel);
}

/**
 * Ajusta a Potencia a ser usada.
 */
void PHY::setPower(byte power)
{
  cc1101.setPA(0, power);
}

/**
 * Ajusta o offset de frequencia.
 */
void PHY::setFreqOffset(byte freq_offset)
{
  cc1101.Write(CC1101_FSCTRL0, freq_offset);
}

/* Ajusta o offset de frequencia.*/
void PHY::setRadio(int set_radio){
  
  if(set_radio == 1){

    /*configura pinos do PA e LNA*/
    pinMode (14, OUTPUT); // pino PC0 ligado ao PA - tx
    pinMode (15, OUTPUT); // pino PC1 ligado ao LNA - rx  
  
    /*Deixa LNA ligado*/
    digitalWrite (14, LOW); // desliga PA
    digitalWrite (15, HIGH);  // liga LNA
  
  }
}
/**
 * Inicializa a Configuracao do CC1101.
 */
int PHY::initCC1101Config(void)
{
  /* Carrega a primeira Configuracao (pode ser inserida mais de uma Configuracao no c�digo) */
  cc1101.Setup(0);
  
  /* Configura o endereco do r�dio */
  cc1101.Write(CC1101_ADDR, Net.my_addr);

  /* Configura a Potencia para a maxima possivel (7) */
  cc1101.setPA(0, 7);
  
  /* Coloca o CC1101 no estado de RX */
  cc1101.Strobe(CC1101_SIDLE);
  delay(1);
  cc1101.Write(CC1101_MCSM1 ,   0x0F );
  cc1101.Strobe(CC1101_SFTX);
  cc1101.Strobe(CC1101_SFRX);
  cc1101.Strobe(CC1101_SRX);
    
  return OK;
}

/**
 * Retorna o status de presenca de portadora no canal (Carrier Sense)
 * return   1 se o canal esta ocupado, 0 se o canal esta livre
 */
boolean PHY::carrierSense(void)
{
  byte cs;

  /* O status da portadora e lido no registrador PKTSTATUS */  
  cc1101.Read(CC1101_PKTSTATUS,&cs);
  /* O bit de Carrier Sense e o bit 6 */
  cs &= 0x40;
  
  if (cs)
    return true;
  else
    return false;
    
}

/**
 * Configura o valor do timeout do WatchDog
 * 0=16ms, 1=32ms, 2=64ms, 3=128ms, 4=250ms, 5=500ms, 6=1sec, 7=2sec, 8=4sec, 9=8sec
 */
void PHY::configWatchdog(int time) {

  byte value;

  if (time > 9 ) time = 9;
  value = time & 7;
  if (time > 7) value |= (1<<5);
  value |= (1<<WDCE);

  /* Habilita a interrupcao de WatchDog no Satus Register */
  MCUSR &= ~(1<<WDRF);
  
  /* Configura as flags do registrador de WatchDog */
  WDTCSR |= (1<<WDCE) | (1<<WDE);
  
  /* Configura o valor do timeout */
  WDTCSR = value;
  
  /* Habilita a interrupcao do WatchDog */
  WDTCSR |= _BV(WDIE);

}

/**
 *    Strobe a command in order to the CC1101 go to the IDLE state
 */

void PHY::strobe_idle_wait( void )
{
  byte current_state;
  
  /* Strobe to IDLE state */
  cc1101.Strobe(CC1101_SIDLE);
  
  do 
  {
    /* Read current state */	
    cc1101.Read( CC1101_MARCSTATE, &current_state);
      
  /* Until in IDLE state */
  } while ( current_state != 0x01 );
}

/**
 * Envia dados pelo RF.
 */
inline void PHY::send(packet * pkt)
{  
  byte current_state;
  byte *txData = (byte *)pkt;
  
  if(set_radio == 1){
    
    // pino PC1 ligado ao LNA - rx
    digitalWrite (15, LOW);  // pino PC1 ligado ao LNA - rx
  
    // pino PC0 ligado ao PA - tx  
    digitalWrite (14, HIGH); // pino PC0 ligado ao PA - tx  
    delay(1);
  
  }
  
  /* Coloca o CC1101 no estado IDLE */
  cc1101.Strobe(CC1101_SIDLE);
  
  /* Escreve uma rajada com os dados a serem transmitidos */
  cc1101.WriteBurst(CC1101_TXFIFO, txData, sizeof(packet));
   
  /* Vai para o estado TX */
  cc1101.Strobe(CC1101_STX);
  
  /* Aguarda enquanto todos os bytes est�o sendo transmitidos */
  while(1)
  {
    byte size;
        cc1101.Read(CC1101_TXBYTES, &size);
    if( size == 0 )
    {
      break;
    }
    else
    {
      cc1101.Strobe(CC1101_STX);
    }
  }
  
  /* Espera que o modulo retorne para o estado de RX */
  do
  {
    cc1101.Read(CC1101_MARCSTATE, &current_state);
  } while ( current_state != 0x0D );
  
  if(set_radio == 1){
    
    // desliga PA - tx 
    digitalWrite (14, LOW); // pino PC0 ligado ao PA - tx

    // liga  LNA - rx
    digitalWrite (15, HIGH);  // pino PC1 ligado ao LNA - rx
  
  }
}

/**
 * Recebe dados pelo RF.
 */
inline int PHY::receive(packet * pkt)
{
  byte rxBytes, rxBytesVerify, rssi, lqi, current_state;

  /* Garante que o pacote terminou de ser recebido - deve ler duas vezes a mesma quantidade de bytes */
  cc1101.Read(CC1101_RXBYTES, &rxBytesVerify);
  do
  {
    rxBytes = rxBytesVerify;
    cc1101.Read(CC1101_RXBYTES, &rxBytesVerify);  
  } while (rxBytes != rxBytesVerify);
  
  /* Checagem de sanidade para ver se o buffer nao esta vazio */
  if (rxBytes == 0)
  {
    cc1101.Strobe(CC1101_SRX);
    return ERR;
  }
  
  if ((rxBytes != (sizeof(packet) + 2) || (rxBytes & 0x80))) 
  {
     /* Flush receive FIFO to reset receive.  Must go to IDLE state to do this. */
     strobe_idle_wait();
     cc1101.Strobe( CC1101_SFRX );
     cc1101.Strobe( CC1101_SRX );
     
     /* Flush complete, skip to end */
     return ERR;
  }

  /* Le uma rajada de dados do FIFO de RX */
  cc1101.ReadBurst(CC1101_RXFIFO, (byte *)pkt, sizeof(packet));
  
  /* Le o byte de RSSI */
  cc1101.Read(CC1101_RXFIFO, &rssi);

  /* Le o byte de LQI */
  cc1101.Read(CC1101_RXFIFO, &lqi);
  
  /* Verifica se o endereco destino e o meu - o pacote e para mim */
  if (pkt->NetHdr[0] != Net.my_addr)
  {
    return ERR;
  }

  /* Trata um possivel overflow do FIFO de RX */
  if (!(lqi & 0x80))
  {
    strobe_idle_wait();            /* Descarta o FIFO de RX */
    cc1101.Strobe( CC1101_SFRX );
    cc1101.Strobe( CC1101_SRX );
    return ERR;
  }

  /* Coloca a informacao de RSSI e LQI no cabecalho da camada f�sica */
  pkt->PhyHdr[2] = rssi;
  pkt->PhyHdr[3] = lqi;
  
  /* Espera que o modulo retorne para o estado de RX */
  do
  {
    cc1101.Read(CC1101_MARCSTATE, &current_state);
  } while ( current_state != 0x0D );
  
  return OK;
}

/* Instanciacao do objeto de acesso a classe da camada F�sica */
PHY Phy = PHY();

// Radiuino_Base : firmware para o no Base da rede

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

#include <RADIUINO.h>
#include <EEPROM.h>
#include <SPI.h>

#include "Headers.h"

#define FIRMWARE_VERSION   2.2     /* Versao 2.2 Radiuino */
byte int_rx = 0;                   /* Inicializacao da interrupcao de recepcao de pacotes - O hardware gera uma interrupcao no comeco que nao deve ser tratada */
byte int_buff = 0;                 /* Inicializacao da interrupcao de buffer overflow - O hardware gera uma interrupcao no comeco que nao deve ser tratada */

/**
 * Configura o Arduino. Executado uma unica vez no inicio do firmware.
 */
void setup()
{  
  /* Inicializacao da camada Fisica */
  Phy.initialize();

  /* Inicializacao da camada de Controle de Acesso ao Meio */
  Mac.initialize();
  
  /* Inicializacao da camada de Rede */
  Net.initialize();
  
  /* Anexa as funcoes de interrupcao de recepcao de pacotes e de estouro de buffer de recepcao */
  attachInterrupt(0, IntReceiveData, RISING);
  attachInterrupt(1, IntBufferOverflow, RISING); 
  pinMode(GDO0, INPUT);
/*interrupcao de estouro do Timer1 */
  Timer1.attachInterrupt(IntTimer1);  
  
  /* Escreve mensagem de inicializacao */
  Serial.print("Radiuino! Base");
  
  
}

/**
 * Laco de execucao do Arduino. Executado continuamente.
 */
void loop()
{
  /* Aguarda pela recepcao de comandos da porta serial */
  if (Serial.available() > 0)
  { 
    Phy.receiveSerial();
  }
  
}

/**
 * Trata o pacote recebido pela rede sem fio.
 */
void IntReceiveData()
{ 
  /* Se for a primeira vez que a interrupcao e executada */
  if (int_rx == 0) 
  {
    int_rx = 1;
    return;
  }

  /* Reenvia toda informacao recebida da rede para o PC */
  if ( digitalRead(GDO0) == HIGH ) {
    
    /* Recebe os dados do RF */
    if (Phy.receive(&g_pkt) == ERR)
      return;
    
    /* Reenvia pela porta serial */
    Phy.sendSerial(&g_pkt);
  }
  
  return;
}

/**
 * Trata o estouro do buffer de recepcao.
 */
void IntBufferOverflow() 
{
  /* Se for a primeira vez que a interrupcao e executada */
  if (int_buff == 0) {
    int_buff = 1;
    return;
  }



Phy.initialize();

  

  /* Esvazia o buffer recepcao e vai para o estado de RX */  
  cc1101.Strobe(CC1101_SFRX);
  cc1101.Strobe(CC1101_SRX);
  
  return;  
}

/**
 * Trata o estouro do período do Timer1.
 */
void IntTimer1()
{  
  /* Aqui podem ser colocadas tarefas periodicas. O periodo do Timer1 é de 1 segundo por padrão.
   * Mas pode ser mudado no setup() */  
  
  return;
}

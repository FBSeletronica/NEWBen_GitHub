// MAC : classe da camada de Controle de Acesso ao Meio

// Mais informacoes em www.radiuino.cc
// Copyright (c) 2015
// Author: Pedro Henrique Gomes, Omar C. Branquinho, Tiago T. Ganselli e Debora M Ferreira, Guilherme Lopes da Silva, Raphael Montali de Assumpçao.
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

/**
 * Construtor da camada de Controle de Acesso ao Meio.
 */
MAC::MAC()
{
}

/**
 * Inicializa a camada de Controle de Acesso ao Meio.
 */
void MAC::initialize(void) 
{
  time_to_sleep = -1;

  /* Seta a flag do Sleep2 para False */
  flag_sleep2 = false;
  /* inicializa para o sleep2 */
  last_wakeup = millis();
}

/**
 * Envia o pacote para a camada inferior
 */
inline void MAC::send(packet * pkt) 
{
  unsigned long starttime = millis();

  /* Aguarda enquanto o canal esta ocupado. Espera no maximo 100 ms */
  while(Phy.carrierSense() && ((millis() - starttime) < 100));
  
  /* Envia para a camada inferior */
  Phy.send(pkt);
  
  return;  
}

/**
 * Recebe o pacote da camada inferior
 */
inline void MAC::receive(packet * pkt) 
{
  /* Se a mensagem e do tipo SLEEP */
  if (pkt->MACHdr[0] == SLEEP_MSG) {
    
    /* Calcula o tempo total para dormir */
    time_to_sleep = 256 * (pkt->MACHdr[1] & 0x7F) + pkt->MACHdr[2];
    
    /* Retorna um pacote de SLEEP ACK para o emissor */
    pkt->MACHdr[0] = SLEEP_ACK;

    /* Troca os enderecos de Origem e Destino */
    //Net.swapAddresses(pkt);

    /* Seta a flag do Sleep2 para False */
    flag_sleep2 = false;

    /* Envia o pacote para a camada de rede*/
    Net.receive(pkt);
    
    /* Send SLEEP ACK packet */
    //Phy.send(pkt);
  }

  else if (pkt->MACHdr[0] == SLEEP2_MSG) {
    
    /* Calcula o tempo total para dormir */
    time_to_sleep = pkt->MACHdr[1]*15 ;

    t2 = pkt->MACHdr[2]*15000 ;
    t3 = pkt->MACHdr[3]*15 ;
    
    /* Retorna um pacote de SLEEP ACK para o emissor */
    pkt->MACHdr[0] = SLEEP2_ACK;

    /* Troca os enderecos de Origem e Destino */
    //Net.swapAddresses(pkt);
    
    
    /* Seta a flag do Sleep2 para True */
    flag_sleep2 = true;

    /* Envia o pacote para a camada de rede*/
    Net.receive(pkt);
    
    /* Send SLEEP ACK packet */
    //Phy.send(pkt);
  }
  
  else {
    /* Seta a flag do Sleep2 para False */
    flag_sleep2 = false;

    /* Envia o pacote para a camada de rede*/
    Net.receive(pkt);
  }
  
  return;  
}

/* Instanciacao do objeto de acesso a classe da camada de Controle de Acesso ao Meio */
MAC Mac = MAC();





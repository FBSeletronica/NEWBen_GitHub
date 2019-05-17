// NET : classe da camada de Rede

// Mais informacoes em www.radiuino.cc
// Copyright (c) 2015
// Author: Pedro Henrique Gomes, Omar C. Branquinho, Tiago T. Ganselli e Debora M Ferreira, Guilherme Lopes da Silva, Raphael Montali de Assumpçao. 
// Versao 2.3: 18/05/2017

// Este arquivo e parte da plataforma Radiuino
// Este programa e um software livre; voce pode redistribui-lo e/ou modifica-lo dentro dos termos da Licenca P�blica Geral Menor GNU 
// como publicada pela Fundacao do Software Livre (FSF); na vers�o 2 da Licenca, ou (na sua opniao) qualquer futura versao.
// Este programa � distribuido na esperan�a que possa ser  util, mas SEM NENHUMA GARANTIA; sem uma garantia implicita 
// de ADEQUACAO a qualquer MERCADO ou APLICACAO EM PARTICULAR. Veja a Licen�a Publica Geral Menor GNU para maiores detalhes.
// Voce deve ter recebido uma copia da Licenca Publica Geral Menor GNU junto com este programa, se nao, escreva para a Funda�ao 
// do Software Livre(FSF) Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
    
// This library is free software; you can redistribute it and/or modify it under the terms of the GNU Lesser General Public License 
// as published by the Free Software Foundation; either version 2 of the License, or (at your option) any later version. This library 
// is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY 
// or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more details. You should have received a copy 
// of the GNU Lesser General Public License along with this library; if not, write to the Free Software Foundation, Inc., 51 Franklin St, 
// Fifth Floor, Boston, MA  02110-1301  USA

#include "Headers.h"

/**
 * Construtor da camada de Rede.
 */
NET::NET()
{
  my_addr = 1;    /* Endere�o */ 
}

/**
 * Inicializa a camada de Controle de Acesso ao Meio.
 */
void NET::initialize(void) 
{
}

/**
 * Realiza a troca de endere�os Origem e Destino
 */
void NET::swapAddresses(packet * pkt) 
{
  /* Troca os endere�os de destino e origem para a retranmiss�o dos pacotes */
  pkt->NetHdr[0] = pkt->NetHdr[2];
  pkt->NetHdr[2] = Net.my_addr;
}

/**
 * Envia o pacote para a camada inferior
 */
inline void NET::send(packet * pkt) 
{
  /* Envia para a camada inferior */
  Mac.send(pkt);
  
  return;  
}

/**
 * Recebe o pacote da camada inferior
 */
inline void NET::receive(packet * pkt) 
{    
   
if((pkt->NetHdr[0]==my_addr))
{
  /* Troca os endere�os de destino e origem para a retranmiss�o dos pacotes */
  pkt->NetHdr[0] = pkt->NetHdr[2];
  pkt->NetHdr[2] = Net.my_addr;
  
  /* Envia para a camada superior */
  Transp.receive(pkt);
  
  return;
}   
}

/* Instancia��o do objeto de acesso � classe da camada de Rede */
NET Net = NET();





// Tansp : classe da camada de Transporte

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
 * Construtor da camada de Transporte.
 */
TRANSP::TRANSP()
{
}

/**
 * Inicializa a camada de Transporte.
 */
void TRANSP::initialize(void) 
{  
}

/**
 * Envia o pacote para a camada inferior
 */
inline void TRANSP::send(packet * pkt) 
{
  /* Envia para a camada inferior */
  Net.send(pkt);
  
  return;  
}

/**
 * Recebe o pacote da camada inferior
 */
inline void TRANSP::receive(packet * pkt) 
{
  static byte counter = 0;
  
  /* Insere um contado no cabe�alho de transporte do pacote */
  pkt->TranspHdr[0] = counter++;

  /* Envia para a camada superior */
  App.receive(pkt);
  
  return;  
}

/* Instancia��o do objeto de acesso � classe da camada de Transporte */
TRANSP Transp = TRANSP();





// APP : classe da camada de Aplica��o

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
 * Construtor da camada de Aplica��o.
 */
APP::APP()
{
}

/**
 * Inicializa a camada de Aplica��o.
 */
void APP::initialize(void) 
{  
  // Faz com que todos os pinos de IO sejam saida
  pinMode (IO0_PIN, OUTPUT); 
  pinMode (IO1_PIN, OUTPUT); 
  pinMode (IO2_PIN, OUTPUT); 
  pinMode (IO3_PIN, OUTPUT); 
  pinMode (IO4_PIN, OUTPUT); 
  pinMode (IO5_PIN, OUTPUT);
}

/**
 * Envia o pacote para a camada inferior
 */
inline void APP::send(packet * pkt) 
{    
  return;  
}

/**
 * Recebe o pacote da camada inferior
 */
inline void APP::receive(packet * pkt) 
{
  //Variáveis inteiras de 2 bytes para armazenar informações a respeito da rede.
  int AD0, AD1, AD2, AD3, AD4, AD5;

  /*
   * Acionamento dos pinos I/O por meio dos bytes do pacote
  */
  
  // IO0_PIN - pino 4 do RFBee / BE900 / BE990 
  if (pkt->IO0[0] == 1)  // Este é o byte 34 do pacote
  {
    digitalWrite (IO0_PIN, HIGH); // Liga led vermelho no DK101
  }
  else 
  {
    digitalWrite (IO0_PIN, LOW); // Desliga led vermelhor no DK101
  }
   
  // IO1_PIN - pino 17 do RFBee / BE900 / BE990
  if (pkt->IO1[0] == 1)  // Este é o byte 37
  {
    digitalWrite (IO1_PIN, HIGH);
  }
  else 
  {
    digitalWrite (IO1_PIN, LOW);
  }

  // IO2_PIN - pino 18 do RFBee / BE900 / BE990
  if (pkt->IO2[0] == 1)  // Este é o byte 40
  {
    digitalWrite (IO2_PIN, HIGH);
  }
  else 
  {
    digitalWrite (IO2_PIN, LOW);
  }
 
  // IO3_PIN - pino 8 do RFBee / BE900 / BE990
  if (pkt->IO3[0] == 1)  // Este é o byte 43
  {
    digitalWrite (IO3_PIN, HIGH);
  }
  else 
  {
    digitalWrite (IO3_PIN, LOW);
  }

  // IO4_PIN - pino 7 do RFBee / BE900 / BE990
  if (pkt->IO4[0] == 1)  // Este é o byte 46
  {
    digitalWrite (IO4_PIN, HIGH);
  }
  else 
  {
    digitalWrite (IO4_PIN, LOW);
  }

  // IO5_PIN - pino 6 do RFBee / BE900 / BE990
  if (pkt->IO5[0] == 1)  // Este é o byte 49
  {
    digitalWrite (IO5_PIN, HIGH);
  }
  else 
  {
    digitalWrite (IO5_PIN, LOW);
  }
  
                   /*------------------Observação importante--------------------------------*/
     
    /*Os pinos AD0_PIN e AD1_PIN não podem ser utilizados no Hardware BE990
    * Isso se deve ao fato de o BE990 possuir componentes que já utilizam os pinos AD0_PIN e AD1_PIN.
    * Para mais informações, acesse www.radiuino.cc
    */
/*---------------------------------------------------------------------------------------------------------*/


  /*
   * Leitura dos conversores AD's
   * As leituras são armazenadas nas variáveis inteiras AD0, AD1, AD2, AD3, AD4, AD5 , todas de 2 bytes. Então, serão necessários 2 bytes do pacote para transmitir cada variável.   
   * O procedimento consiste em dividir a variável por 256 (tamanho de 1 byte, ou 2^8); o valor inteiro da divisão é colocado em 1 byte do pacote e; o resto colocado no byte seguinte.
   * No computador, para voltar no valor de 0 a 1023 deve ser feita a conta:  Valor = Inteiro * 256 + Resto.
   * 
   * Também podem ser transmitidas outros tipos de variáveis de dados, como float, long,boolean, etc. Para isso, basta aplicar a mesma lógica do que foi explicado a cima: dividindo  
   * pelo total de valores da variável e inserindo o resto no byte seguinte do pacote. 
  */   
  
  // AD0_PIN - pino 15 do RFBee / BE900 / BE990
  AD0 = analogRead(AD0_PIN); // Valor de 0 a 1023 e será necessário dois bytes para representar
  pkt->AD0[0] = 0; // Pode ser utilizado para indicar o tipo de sensor no byte 16
  pkt->AD0[1] = (byte) (AD0/256); // Valor inteiro no byte 17
  pkt->AD0[2] = (byte) (AD0%256); // Resto da divisão no byte 18
  
  // AD1_PIN - pino 13 do RFBee / BE900 / BE990
  AD1 = analogRead(AD1_PIN);
  pkt->AD1[0] = 1; // Pode ser utilizado para indicar o tipo de sensor o byte 19
  pkt->AD1[1] = (byte) (AD1/256); // Valor inteiro no byte 20
  pkt->AD1[2] = (byte) (AD1%256); // Resto da divisão noo byte 21

  // AD2_PIN - pino 12 do RFBee / BE900 / BE990
  AD2 = analogRead(AD2_PIN);
  pkt->AD2[0] = 2; // Pode ser utilizado para indicar o tipo de sensor o byte 22
  pkt->AD2[1] = (byte) (AD2/256); // Valor inteiro no byte 23
  pkt->AD2[2] = (byte) (AD2%256); // Resto da divisão noo byte 24

  // AD3_PIN - pino 11 do RFBee / BE900 / BE990
  AD3 = analogRead(AD3_PIN);
  pkt->AD3[0] = 3; // Pode ser utilizado para indicar o tipo de sensor o byte 25
  pkt->AD3[1] = (byte) (AD3/256); // Valor inteiro no byte 26
  pkt->AD3[2] = (byte) (AD3%256); // Resto da divisão noo byte 27

  // AD4_PIN - pino 20 do RFBee / BE900 / BE990
  AD4 = analogRead(AD4_PIN);
  pkt->AD4[0] = 0; // Pode ser utilizado para indicar o tipo de sensor o byte 28
  pkt->AD4[1] = (byte) (AD4/256); // Valor inteiro no byte 29
  pkt->AD4[2] = (byte) (AD4%256); // Resto da divisão noo byte 30

  // AD5_PIN - pino 19 do RFBee / BE900 / BE990
  AD5 = analogRead(AD5_PIN);
  pkt->AD5[0] = 0; // Pode ser utilizado para indicar o tipo de sensor o byte 31
  pkt->AD5[1] = (byte) (AD5/256); // Valor inteiro no byte 32
  pkt->AD5[2] = (byte) (AD5%256); // Resto da divisão noo byte 33
  
  // Envia o pacote para a camada de transporte
  Transp.send(pkt);
  
  return;  
}
 
/* Instanciação do objeto de acesso � classe da camada de Aplicação */
APP App = APP();

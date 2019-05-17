/*
  Controlador do atenuador da bancada de emulação de canal.

Controlar o atenuador que compões parte da bancada de emulação de canal
através de uma mensagem recebida pela comunicação serial entre o 
computador e o Arduino. A mensagem com o parâmetro de configuração do Atenuador
é enviada pelo programa em python que gerencia a aquisição de dados do experimento.

  
 The circuit:
 Pinos do Atenuador ligados do LSB ao MSB de forma crescente nos pinos digitais de 8 a 13

 created 2016
 by Raphael Montali da Assumpção
 */


int attPins[] = {8, 9, 10, 11, 12, 13};
int attControl[]={0,0,0,0,0,0};

void setup() {
  // initialize the serial communication:
  Serial.begin(9600);
  // initialize the ledPin as an output:
  for (int i=0; i<6; i++) {
        pinMode(attPins[i], OUTPUT);
    }
}

void loop() {
  byte atenuacao;

  // check if data has been sent from the computer:
  if (Serial.available()) {
    // read the most recent byte (which will be from 0 to 255):
    atenuacao = Serial.read();
    // set the attenuator control vector:
    for (int i=0; i<6; i++) {
      if(1 << i & atenuacao){
        attControl[i]=1;
      }
      else{
        attControl[i]=0;
      }
    }
    // turn the pins high or low according to the attenuator control vector: 
    for (int i=0; i<6; i++) {
      digitalWrite(attPins[i],attControl[i]);
    }

  Serial.write(atenuacao);
  }
}


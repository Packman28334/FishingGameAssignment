const long BAUD = 9600;

const int RED = 9;
const int BLUE = 10;
const int GREEN = 11;

// modes:
// - 0: all off
// - 1: all on

// - 2: red only
// - 3: blue only
// - 4: green only

// - 5: fast cycle
// - 6: medium cycle
// - 7: slow cycle

// - 8: fast inverse cycle
// - 9: medium inverse cycle
// - 10: slow inverse cycle

// - 11: fast flash
// - 12: medium flash
// - 13: slow flash
int mode = 0;

void setup() {
  // put your setup code here, to run once:
  Serial.begin(BAUD);
  pinMode(RED, OUTPUT);
  pinMode(BLUE, OUTPUT);
  pinMode(GREEN, OUTPUT);
}

void loop() {
  // put your main code here, to run repeatedly:

  if (Serial.available()) { // very based code
    int read = Serial.parseInt()-1;
    //Serial.println(read);
    if (read > -1) {
      mode = read;
      digitalWrite(RED, LOW);
      digitalWrite(BLUE, LOW);
      digitalWrite(GREEN, LOW);
    }
  }

  Serial.write(mode);

  switch (mode) {
    case 0:
      mode0();
      break;
    case 1:
      mode1();
      break;

    case 2:
      mode2();
      break;
    case 3:
      mode3();
      break;
    case 4:
      mode4();
      break;

    case 5:
      modes567(250);
      break;
    case 6:
      modes567(500);
      break;
    case 7:
      modes567(750);
      break;

    case 8:
      modes8910(250);
      break;
    case 9:
      modes8910(500);
      break;
    case 10:
      modes8910(750);
      break;

    case 11:
      modes111213(150);
      break;
    case 12:
      modes111213(300);
      break;
    case 13:
      modes111213(600);
      break;
  }

}


void mode0() { // all off
  digitalWrite(RED, LOW);
  digitalWrite(BLUE, LOW);
  digitalWrite(GREEN, LOW);
}

void mode1() { // all on
  digitalWrite(RED, HIGH);
  digitalWrite(BLUE, HIGH);
  digitalWrite(GREEN, HIGH);
}

void mode2() { // red only
  digitalWrite(RED, HIGH);
  digitalWrite(BLUE, LOW);
  digitalWrite(GREEN, LOW);
}

void mode3() { // blue only
  digitalWrite(RED, LOW);
  digitalWrite(BLUE, HIGH);
  digitalWrite(GREEN, LOW);
}

void mode4() { // green only
  digitalWrite(RED, LOW);
  digitalWrite(BLUE, LOW);
  digitalWrite(GREEN, HIGH);
}

void modes567(int loop_delay) { // cycle
  digitalWrite(GREEN, LOW);
  digitalWrite(RED, HIGH);
  delay(loop_delay);
  digitalWrite(RED, LOW);
  digitalWrite(BLUE, HIGH);
  delay(loop_delay);
  digitalWrite(BLUE, LOW);
  digitalWrite(GREEN, HIGH);
  delay(loop_delay);
}

void modes8910(int loop_delay) { // inverse cycle
  digitalWrite(RED, LOW);
  digitalWrite(GREEN, HIGH);
  delay(loop_delay);
  digitalWrite(GREEN, LOW);
  digitalWrite(BLUE, HIGH);
  delay(loop_delay);
  digitalWrite(BLUE, LOW);
  digitalWrite(RED, HIGH);
  delay(loop_delay);
}

void modes111213(int loop_delay) { // flash
  digitalWrite(RED, HIGH);
  digitalWrite(BLUE, HIGH);
  digitalWrite(GREEN, HIGH);
  delay(loop_delay);
  digitalWrite(RED, LOW);
  digitalWrite(BLUE, LOW);
  digitalWrite(GREEN, LOW);
  delay(loop_delay);
}

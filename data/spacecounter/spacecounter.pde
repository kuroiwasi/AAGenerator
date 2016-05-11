PImage msp;

void setup(){
  size(32,32);
  msp = loadImage("mspgothic_learge_space.png");
  int w = msp.width;
  int h = msp.height;
  int count = 0;
  int prevred = 0;
  for(int y=0; y<h; y+=16){
    count=0;
    print("[");
    for(int x=0; x<w; ++x){
      color c = msp.get(x,y);
      int red = int(red(c));
      if(count!=0 && red != prevred){
        if(count < 10) print(" ");
        print(count+",");
        count = 0;
      }
      prevred = red;
      ++count;
    }
    println("],");
  }
}
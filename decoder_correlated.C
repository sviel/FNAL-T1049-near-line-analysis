#include <sstream>
#include <iostream>
#include <fstream>
#include <sstream>
#include <string>
#include <vector>
#include <stdio.h>
#include <stdlib.h>
#include <math.h>


std::string hexaToBin(std::string sHex);
int binToDec(std::string sBin);


void decoder_correlated(std::string name){

  std::string line, item;
  std::ifstream dataFile(name.c_str());
  
  if(!dataFile.is_open()){
    std::cout << "Unable to read input file: " << name.c_str() << std::endl;
    exit(1);
  }
  
  // We remove lines with a # symbol at the begining of the file
  // they are considered as comments
  do { getline(dataFile, line); }
  while(line[0] == '#');
  
  int counter = 0; // event number counter
  
  int currentChar;
  int nWords; // The number of words in a line
  std::string ip, trig, word, binWord;
  
  unsigned int trig_dec;
  int address, tdoTemp, pdoTemp;
  
  
  while ( (line.compare("")!=0)  && !dataFile.eof()  ) {
    
    // we reject the filling fafafafa words that mark the boundary between events
    std::size_t found = line.find("fafafafa");
    if (found!=std::string::npos){
      //      std::cout << line << "<--- this should be a fafafafa \n";
      counter++;
      getline(dataFile, line);
    }

    // Here we have a readable word
    else {
      // First read the IP address
      ip = std::string(line, 0, 2);
      
      // Then the trigger ID
      trig = std::string(line, 6, 6);
      sscanf(trig.c_str(), "%x", &trig_dec);
      
      // Then we start at char 28. The others characters are rest of the header
      currentChar = 28;
      
      // For testing
      //      line = "16--00000000004c4e4200000000e123a40be524e980e924f299ed2592d9f12552d7f5255081";

      nWords = (line.length()-28)/8;
      if ( ((line.length()-28) % 8) != 0 ) std::cout << "Warning: Input data file does not have an integer number of 32-bit words:"<<line.length() <<" without header: "<<(line.length()-28)<< std::endl;

      
      for(int i = 0; i < nWords; i++){

        word = std::string(line, currentChar, 8);
        binWord = hexaToBin(word);
        //        std::cout << binWord << std::endl;

        address = binToDec(std::string(binWord, 0, 6));
        tdoTemp = binToDec(std::string(binWord, 6, 13));
        pdoTemp = binToDec(std::string(binWord, 19, 13));

        std::cout << counter << "\t" << address << "\t" << tdoTemp << "\t" << pdoTemp << "\t"
                  << ip << "\t" << trig_dec << std::endl;
        
        currentChar+=8;
      }
      
      getline(dataFile, line);

    } // end if readable word
  } // end while loop

  dataFile.close();

  return;

}




// String hexadecimal to binary converter 
std::string hexaToBin (std::string sHex) {
  std::string sReturn = "";
  for (unsigned int i = 0; i < sHex.length(); ++i){
    switch (sHex[i]){
      case '0': sReturn.append("0000"); break;
      case '1': sReturn.append("0001"); break;
      case '2': sReturn.append("0010"); break;
      case '3': sReturn.append("0011"); break;
      case '4': sReturn.append("0100"); break;
      case '5': sReturn.append("0101"); break;
      case '6': sReturn.append("0110"); break;
      case '7': sReturn.append("0111"); break;
      case '8': sReturn.append("1000"); break;
      case '9': sReturn.append("1001"); break;
      case 'a': sReturn.append("1010"); break;
      case 'b': sReturn.append("1011"); break;
      case 'c': sReturn.append("1100"); break;
      case 'd': sReturn.append("1101"); break;
      case 'e': sReturn.append("1110"); break;
      case 'f': sReturn.append("1111"); break;
    }
  }
  return sReturn;
}




// String binary to decimal converter
int binToDec(std::string sBin){
  int toReturn = 0;
  int base = 1;
  
  for(int i = sBin.length() - 1; i >= 0; i--){
    toReturn += (sBin[i] - 48) * base;
    base *= 2;
  }
  
  return toReturn;
}

function Decoder(b, port) {
var decoded = {};
    switch (port) {
      case 1:
         decoded.lat = ((b[0]<<16)>>>0) + ((b[1]<<8)>>>0) + b[2];
  decoded.lat = (decoded.lat / 16777215.0 * 180) - 90;

  decoded.lon = ((b[3]<<16)>>>0) + ((b[4]<<8)>>>0) + b[5];
  decoded.lon = (decoded.lon / 16777215.0 * 360) - 180;

  var altValue = ((b[6]<<8)>>>0) + b[7];
  var sign = b[6] & (1 << 7);
  if(sign)
  {
    decoded.alt = 0xFFFF0000 | altValue;
  }
  else
  {
    decoded.alt = altValue;
  }

  decoded.hdop = b[8] / 10.0;

        break;
        case 2:
            decoded.lat =  (b[0] + (b[1] << 8) + (b[2] << 16)) / -10000;
            decoded.lon =  (b[3] + (b[4] << 8) + (b[5] << 16)) / 10000;
      decoded.alt = b[6];
      decoded.tdop = b[7]/100;
        break;
        

}

return decoded;
}


void eval(int *numbers,char operator)
{
  if (operator == '+') {
    numbers[*numbers + -1] = numbers[*numbers + -1] + numbers[*numbers];
  }
  else if (operator < ',') {
    if (operator == '*') {
      numbers[*numbers + -1] = numbers[*numbers + -1] * numbers[*numbers];
    }
  }
  else if (operator == '-') {
    numbers[*numbers + -1] = numbers[*numbers + -1] - numbers[*numbers];
  }
  else if (operator == '/') {
    numbers[*numbers + -1] = numbers[*numbers + -1] / numbers[*numbers];
  }
  *numbers = *numbers + -1;
  return;
}
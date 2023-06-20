undefined4 parse_expr(int operators,int *arr_100)
{
  int copy_;
  int cmp_w_0;
  undefined4 uVar2;
  int in_GS_OFFSET;
  int iStack_8c;
  int idx;
  int op_idx;
  char operator2 [100];
  int iStack_10;
  
  iStack_10 = *(int *)(in_GS_OFFSET + 0x14);
  iStack_8c = operators;
  op_idx = 0;
  bzero(operator2,100);
  idx = 0;
  do {
    // not number (receive operator)
    if (9 < (int)*(char *)(operators + idx) - '0') {
      cmp_w_0 = (operators + idx) - iStack_8c;
      copy_ = malloc(idx + 1);
      // 
      memcpy(copy_,iStack_8c,idx);
      *(undefined *)(copy_ + idx) = 0;
      // error if num is 0
      cmp_w_0 = strcmp(copy_,&UNK_080bf7a8);
      if (cmp_w_0 == 0) {
        puts(&UNK_080bf7aa);
        fflush(_IO_2_1_stdout_);
        uVar2 = 0;
        goto LAB_0804935f;
      }
      
      // encounter number, idx ++
      // 1 + 2
      copy_ = atoi(copy_);
      if (0 < copy_) {
        cmp_w_0 = *arr_100;
        *arr_100 = *arr_100 + 1; // +
        arr_100[cmp_w_0 + 1] = copy_; // 1
      }

      // pattern error
      if (*(char *)(operators + idx) != '\0' && ((9 < (int)*(char *)(operators + idx + 1) - '0' )))
      {
        puts(&UNK_080bf7c3);
        fflush(_IO_2_1_stdout_);
        uVar2 = 0;
        goto LAB_0804935f;
      }

      iStack_8c = operators + idx + 1; // 2
      if (operator2[op_idx] == '\0') {
        operator2[op_idx] = *(char *)(operators + idx); // +
      }
      else {
        // check operator in front of numbers
        switch(*(undefined *)(operators + idx)) {
        case 0x25:
        case 0x2a:
        case 0x2f: // '/'
          if ((operator2[op_idx] == '+') || (operator2[op_idx] == '-')) {
            operator2[op_idx + 1] = *(char *)(operators + idx);
            op_idx = op_idx + 1;
          }
          else {
            eval(arr_100,(int)operator2[op_idx]);
            operator2[op_idx] = *(char *)(operators + idx);
          }
          break;
        default: // number ?
          eval(arr_100,(int)operator2[op_idx]);
          op_idx = op_idx + -1;
          break;
        case 0x2b: // '+'

        case 0x2d: // '-'
          // arr_100 will point to 
          eval(arr_100,(int)operator2[op_idx]);
          operator2[op_idx] = *(char *)(operators + idx);
        }
      }

      if (*(char *)(operators + idx) == '\0') {
        for (; -1 < op_idx; op_idx = op_idx + -1) {
          eval(arr_100,(int)operator2[op_idx]);
        }
        // when eval return, arr_100 --> &arr_100[0]
        uVar2 = 1;
LAB_0804935f:
        if (iStack_10 != *(int *)(in_GS_OFFSET + 0x14)) {
                    /* WARNING: Subroutine does not return */
          __stack_chk_fail();
        }
        return uVar2;
      }
    }
    idx = idx + 1;
  } while( true );
}


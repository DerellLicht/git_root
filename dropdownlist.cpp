//  this code was scavenged from main_controls.cpp in svr10 source code.
//  It will be used to support a list of available palettes

//==========================================================================
//    Baudrate combobox functions
//==========================================================================

//  example of .rc record
// A drop-down that doesn't let the user type into it is still a COMBOBOX control -- 
// there isn't a separate CONTROL class name for it. The difference is purely the style flag:
// 
// CBS_DROPDOWN — has an editable text box with a drop-down list (what you're running into)
// CBS_DROPDOWNLIST — drop-down list only, no edit control, user must pick from the list (what you want)
// CBS_SIMPLE — list is always visible, no drop-down

COMBOBOX IDC_MYCOMBO, 10, 10, 100, 100, CBS_DROPDOWNLIST | WS_VSCROLL | WS_TABSTOP

//***********************************************************************
//  combobox elements
//***********************************************************************
unsigned baudrates[] = 
   { 1200, 2400, 4800, 9600, 19200, 28800, 38400, 57600 } ;

//***********************************************************************
//  get baudrate from selection
//***********************************************************************
uint get_baudrate_value(uint idx)
{
   for (uint j=0; baudrates[j] != 0; j++) {
      if (j == idx)
         return baudrates[j];
   }
   return 1200 ;
}

//***********************************************************************
//  get selection from baudrate
//***********************************************************************
static uint get_brate_index(uint baudrate)
{
   for (uint j=0; baudrates[j] != 0; j++) {
      if (baudrates[j] == baudrate)
         return j;
   }
#ifdef  SUPPORT_300BAUD
   return 1;
#else
   return 0;
#endif
}

//****************************************************************************
uint get_baudrate(void)
{
   uint sel = SendMessageA(hwnd_CBbaudrate, CB_GETCURSEL, 0, 0);
   return get_baudrate_value(sel) ;
}

//***********************************************************************
static void fill_brate_combobox(HWND hwnd, unsigned init_idx)
{
   // char msgstr[81] ;
   for (uint j=0; baudrates[j] != 0; j++) {
      char bauds[10] ;
      wsprintfA(bauds, "%u", baudrates[j]) ;
   // for (j=0; bauds[j] != 0; j++) {
      // syslog("LB: adding %s\n", elements[j]) ;
      LRESULT result = SendMessageA(hwnd, CB_ADDSTRING, 0, (LPARAM) bauds);
      switch (result) {
      case CB_ERR:
         syslog("CB_ADDSTRING: CB_ERR: %s\n", get_system_message()) ;
         break;
      case CB_ERRSPACE:
         syslog("CB_ADDSTRING: CB_ERRSPACE: %s\n", get_system_message()) ;
         break;

      default:
         // wsprintfA(msgstr, "CB_ADDSTRING returned %u\n", result) ;
         // OutputDebugStringA(msgstr) ;
         break;
      }
   }
   SendMessageA(hwnd, CB_SETCURSEL, (WPARAM) init_idx, 0);
}

//***********************************************************************
static void set_cbox_baudrate_index(uint sel)
{
   PostMessageA(hwnd_CBbaudrate, CB_SETCURSEL, (WPARAM) sel, 0);
}

void set_baudrate_entry(uint baudrate)
{
   uint sel = get_brate_index(baudrate);
   set_cbox_baudrate_index(sel) ;
}

//==========================================================================
void fill_brate_cbox(void)
{
   int sel = get_brate_index(1200) ; //  this *should* get changed later to INI setting
   fill_brate_combobox(hwnd_CBbaudrate, sel) ;
}


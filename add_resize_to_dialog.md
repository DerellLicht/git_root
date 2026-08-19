##  Series of instructions to incorporate resize operations into existing dialog application  
This will incorporate data from my existing `winagrams` app.

NOTES: These instructions assume that `CStatusBar` class from `der_libs` is included in app. 
Many of these computations will change if that is not the case.

PREREQUISITE: this assumes `uint cxClient` / `uint cyClient` already exist as globals
(defined in the .cpp, declared `extern` in the .h) before starting -- the data block
and `WM_INITDIALOG` code below both read/write them directly. If starting from a
dialog that doesn't already have these (e.g. not cloned from `winagrams`), add them
first.

- In the `.rc` resource file, add `WS_THICKFRAME` to STYLE for the relevant dialog definition  

- copy the data block labeled `BEGIN/END Claude resize data block`,  
  place at top of file.
  
- in `WM_INITDIALOG` handler, add this code near top:
```
   hwndMain = hwnd ;
   get_monitor_dimens(hwnd);

   RECT myRect ;
   // GetWindowRect(hwnd, &myRect) ;
   GetClientRect(hwnd, &myRect) ;
   cxClient = (myRect.right - myRect.left) ;
   cyClient = (myRect.bottom - myRect.top) ;

   // Claude 08/14/26 - measure actual border/caption size once, from live
   // window+client rects, rather than guessing at SM_CXFRAME/SM_CYCAPTION
   // (which can be wrong under theming/DPI). Used to convert client-size
   // values into the window-size values WM_GETMINMAXINFO actually wants.
   {
   RECT winRect ;
   GetWindowRect(hwnd, &winRect) ;
   dx_frame = (winRect.right - winRect.left) - (int) cxClient ;
   dy_frame = (winRect.bottom - winRect.top) - (int) cyClient ;
   // syslog("frame delta: dx_frame=%d, dy_frame=%d\n", dx_frame, dy_frame) ;
   }
```
Also, add the following after CStatusBar control is configured:  
```
   // Claude 08/14/26 - the real, permanent floor for WM_GETMINMAXINFO.
   // Same shape as resize_font_dialog's live layout math, just solved for
   // the smallest acceptable listview height (MIN_LISTVIEW_VISIBLE_DY)
   // instead of the current one. Computed once, here, and never touched
   // again -- see the comment on the variable itself.
   min_application_window_height = get_terminal_top() + MIN_LISTVIEW_VISIBLE_DY
      + MainStatusBar->height() + (uint) get_dy_offset() + (uint) dy_frame ;
```

- add following message handlers (and associated functions)
```
   case WM_GETMINMAXINFO:
      do_getminmaxinfo(hwnd, message, wParam, lParam) ;
      return FALSE;

   case WM_SIZE:
      do_size(hwnd, message, wParam, lParam) ;
      return TRUE ;

   //  this is only required if width is fixed in dialog
   case WM_WINDOWPOSCHANGING:
      {
      WINDOWPOS* pos = (WINDOWPOS*)lParam;
      if (!(pos->flags & SWP_NOSIZE))
         pos->cx = cxClient;   // hardcoded, no private_data needed
      break;
      }      
      return TRUE ;

```




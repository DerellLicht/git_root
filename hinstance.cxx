// [2920] hInstance=4194304, 4194304, 4194304
   syslog("hInstance=%u, %u, %u\n",
      hInstance,
      GetWindowLong(hwnd, GWL_HINSTANCE),
      GetModuleHandle(NULL)
      );

